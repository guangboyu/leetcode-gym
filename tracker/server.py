#!/usr/bin/env python3
"""LeetCode study tracker — local web UI. Stdlib only.

    python3 tracker/server.py [--port 8765] [--data-dir DIR] [--autocommit] [--push]

Serves tracker/static/ plus:
    GET  /data/problems.json   the merged problem table (read-only input)
    GET  /api/progress         all progress entries (derived from the event log)
    POST /api/review           {"slug": ..., "action": "solved"|"solved_help"|"forgotten"|"reset"}
                               -> {"slug": ..., "entry": <updated entry or null>}

--data-dir   where reviews.jsonl + progress.json live (default: ./data, which is
             gitignored). To git-back-up your progress without leaking it from a
             published repo, point this at a SEPARATE PRIVATE repo.
--autocommit git-commit the progress files in their data dir 60s after the last
             review action, and on shutdown.
--push       after each autocommit, also `git push` the data dir's repo.
"""
import argparse
import json
import subprocess
import threading
from datetime import date
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tracker import store
from tracker.resources import resource_root
from tracker.scheduler import ACTIONS, apply_action

ROOT = resource_root()
STATIC = ROOT / "tracker" / "static"
PROBLEMS_FILE = ROOT / "data" / "problems.json"

LOCK = threading.Lock()
SLUGS = frozenset(json.loads(PROBLEMS_FILE.read_text(encoding="utf-8"))["problems"])
PROGRESS = {}

AUTOCOMMIT = False
PUSH = False
COMMIT_DELAY = 60
_commit_timer = None
_warned = False


def _git(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)


def commit_now():
    """Commit (and optionally push) the progress files in their own data dir."""
    global _warned
    d = store.LOG_FILE.parent
    files = [store.LOG_FILE.name, store.SNAPSHOT_FILE.name]
    if _git(d, "rev-parse", "--git-dir").returncode != 0:
        if not _warned:
            print(f"[autocommit] {d} is not a git repository — progress not backed up.")
            _warned = True
        return
    _git(d, "add", "--", *files)
    if _git(d, "diff", "--cached", "--quiet", "--", *files).returncode == 0:
        ignored = _git(d, "check-ignore", *files).stdout.strip()
        if ignored and not _warned:
            print(f"[autocommit] {ignored.splitlines()[0]} is gitignored here — "
                  "point --data-dir at a separate private repo to back up progress.")
            _warned = True
        return
    _git(d, "commit", "-q", "-m", f"progress backup {date.today().isoformat()}")
    msg = f"[autocommit] progress committed ({date.today().isoformat()})"
    if PUSH:
        r = _git(d, "push")
        msg += " and pushed" if r.returncode == 0 else f" (push failed: {r.stderr.strip()})"
    print(msg)


def schedule_commit():
    global _commit_timer
    if _commit_timer:
        _commit_timer.cancel()
    _commit_timer = threading.Timer(COMMIT_DELAY, commit_now)
    _commit_timer.daemon = True
    _commit_timer.start()


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC), **kwargs)

    def send_json(self, obj, status=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/api/progress":
            with LOCK:
                self.send_json(PROGRESS)
        elif self.path == "/data/problems.json":
            body = PROBLEMS_FILE.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            super().do_GET()

    def do_POST(self):
        if self.path != "/api/review":
            self.send_json({"error": "not found"}, 404)
            return
        try:
            length = int(self.headers.get("Content-Length", 0))
            req = json.loads(self.rfile.read(length))
            slug, action = req["slug"], req["action"]
        except (ValueError, KeyError, json.JSONDecodeError):
            self.send_json({"error": "bad request"}, 400)
            return
        if slug not in SLUGS:
            self.send_json({"error": f"unknown slug: {slug}"}, 400)
            return
        if action not in ACTIONS:
            self.send_json({"error": f"unknown action: {action}"}, 400)
            return
        with LOCK:
            today = date.today().isoformat()
            entry = apply_action(PROGRESS.get(slug), action, today)
            store.append_event(slug, action, today)
            if entry is None:
                PROGRESS.pop(slug, None)
            else:
                PROGRESS[slug] = entry
            store.save_snapshot(PROGRESS)
        if AUTOCOMMIT:
            schedule_commit()
        self.send_json({"slug": slug, "entry": entry})

    def log_message(self, fmt, *args):
        pass  # keep the terminal quiet


def configure(data_dir=None, autocommit=False, push=False):
    """Load progress and set backup options. Call once before make_server().

    Shared by the CLI (main) and the desktop launcher so both go through the
    same startup path. data_dir=None keeps store's default (./data)."""
    global AUTOCOMMIT, PUSH, PROGRESS
    AUTOCOMMIT, PUSH = autocommit, push
    if data_dir is not None:
        store.set_data_dir(data_dir)
    PROGRESS = store.load_progress()


def make_server(port=8765, host="127.0.0.1"):
    """Build (but don't start) the tracker HTTP server. Pass port=0 to let the
    OS pick a free port; read the chosen port from server.server_address[1]."""
    return ThreadingHTTPServer((host, port), Handler)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--data-dir", default=str(ROOT / "data"),
                    help="directory for reviews.jsonl + progress.json (default: ./data)")
    ap.add_argument("--autocommit", action="store_true",
                    help="git-commit progress files in the data dir after review activity")
    ap.add_argument("--push", action="store_true",
                    help="also git-push the data dir's repo after each autocommit")
    args = ap.parse_args()
    configure(data_dir=args.data_dir, autocommit=args.autocommit, push=args.push)
    server = make_server(port=args.port)
    print(f"Tracking {len(SLUGS)} problems — open http://localhost:{args.port}")
    flags = "  (autocommit" + (" + push)" if PUSH else ")") if AUTOCOMMIT else ""
    print(f"Event log: {store.LOG_FILE}" + flags)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        if AUTOCOMMIT:
            commit_now()
        print("\nbye")


if __name__ == "__main__":
    main()
