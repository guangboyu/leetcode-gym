#!/usr/bin/env python3
"""LeetCode study tracker — local web UI. Stdlib only.

    python3 tracker/server.py [--port 8765] [--autocommit]

Serves tracker/static/ plus:
    GET  /data/problems.json   the merged problem table (read-only input)
    GET  /api/progress         all progress entries (derived from data/reviews.jsonl)
    POST /api/review           {"slug": ..., "action": "solved"|"solved_help"|"forgotten"|"reset"}
                               -> {"slug": ..., "entry": <updated entry or null>}

--autocommit: git-commit the progress files (data/reviews.jsonl + data/progress.json)
60 seconds after the last review action, and on shutdown. Never pushes.
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
from tracker.scheduler import ACTIONS, apply_action

ROOT = Path(__file__).resolve().parent.parent
STATIC = ROOT / "tracker" / "static"
PROBLEMS_FILE = ROOT / "data" / "problems.json"

LOCK = threading.Lock()
SLUGS = frozenset(json.loads(PROBLEMS_FILE.read_text(encoding="utf-8"))["problems"])
PROGRESS = store.load_progress()

AUTOCOMMIT = False
COMMIT_DELAY = 60
_commit_timer = None


def commit_now():
    files = [str(store.LOG_FILE), str(store.SNAPSHOT_FILE)]
    subprocess.run(["git", "add", "--"] + files, cwd=ROOT, capture_output=True)
    staged = subprocess.run(["git", "diff", "--cached", "--quiet", "--"] + files,
                            cwd=ROOT, capture_output=True)
    if staged.returncode != 0:
        subprocess.run(["git", "commit", "-q", "-m",
                        f"progress backup {date.today().isoformat()}"],
                       cwd=ROOT, capture_output=True)
        print(f"[autocommit] progress committed ({date.today().isoformat()})")


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


def main():
    global AUTOCOMMIT
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--autocommit", action="store_true",
                    help="git-commit progress files after review activity")
    args = ap.parse_args()
    AUTOCOMMIT = args.autocommit
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"Tracking {len(SLUGS)} problems — open http://localhost:{args.port}")
    print(f"Event log: {store.LOG_FILE}" + ("  (autocommit on)" if AUTOCOMMIT else ""))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        if AUTOCOMMIT:
            commit_now()
        print("\nbye")


if __name__ == "__main__":
    main()
