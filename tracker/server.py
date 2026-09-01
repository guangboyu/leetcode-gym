#!/usr/bin/env python3
"""LeetCode Gym — local web UI. Stdlib only.

    python3 tracker/server.py [--port 8765] [--data-dir DIR] [--autocommit] [--push]

Serves tracker/static/ plus:
    GET  /data/problems.json   the merged problem table (read-only input; served
                               from memory with an ETag and gzip)
    GET  /api/progress         all progress entries (derived from the event log)
    POST /api/review           {"slug": ..., "action": "solved"|"solved_help"|"forgotten"|"reset"|"undo"}
                               -> {"slug": ..., "entry": <updated entry or null>, "undoable": bool}
                               "undo" cancels the slug's most recent effective event.
    GET  /api/activity         {"days": {"YYYY-MM-DD": {action: n}}, "first": date|null}
    GET  /api/settings         UI preferences (rating cap, skips, drill defaults, theme)
    POST /api/settings         partial patch of the same, or {"reset": true} -> full settings
    GET  /api/data-dir         {"path": ...}          POST /api/data-dir {"path": ...}
    GET  /api/about            name, version, python, dataDir, configFile, problemsSnapshot, desktop

--data-dir   where reviews.jsonl + progress.json live (default: ./data, which is
             gitignored). To git-back-up your progress without leaking it from a
             published repo, point this at a SEPARATE PRIVATE repo.
--autocommit git-commit the progress files in their data dir 60s after the last
             review action, and on shutdown.
--push       after each autocommit, also `git push` the data dir's repo.
"""
import argparse
import gzip
import hashlib
import json
import platform
import subprocess
import threading
from datetime import date
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tracker import __version__, config, store
from tracker.resources import resource_root
from tracker.scheduler import ACTIONS, apply_action

ROOT = resource_root()
STATIC = ROOT / "tracker" / "static"
PROBLEMS_FILE = ROOT / "data" / "problems.json"

LOCK = threading.Lock()

# problems.json is ~1 MB and immutable while the server runs, so it is read
# once: the raw bytes, a gzip copy (~150 KB on the wire) and a strong ETag so
# the SPA revalidates with a 304 on every launch after the first.
_PROBLEMS_RAW = PROBLEMS_FILE.read_bytes()
_PROBLEMS_GZ = gzip.compress(_PROBLEMS_RAW, compresslevel=6)
_PROBLEMS_ETAG = '"' + hashlib.sha1(_PROBLEMS_RAW).hexdigest() + '"'
_PROBLEMS_DATA = json.loads(_PROBLEMS_RAW)
SLUGS = frozenset(_PROBLEMS_DATA["problems"])
PROBLEMS_SNAPSHOT = _PROBLEMS_DATA.get("snapshot")
PROGRESS = {}
SETTINGS = dict(store.DEFAULT_SETTINGS)
_ACTIVITY = None            # cached /api/activity payload; None = recompute
DESKTOP = False             # set by the desktop launcher for /api/about

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


# Validation for POST /api/settings: key -> predicate on the JSON value.
def _is_int_or_none(v):
    return v is None or (isinstance(v, int) and not isinstance(v, bool))


def _is_str_list(v):
    return isinstance(v, list) and all(isinstance(x, str) for x in v)


SETTING_RULES = {
    "cap": _is_int_or_none,
    "routeShowOptional": lambda v: isinstance(v, bool),
    "routeSkipped": _is_str_list,
    "drillPools": _is_str_list,
    "drillTopics": lambda v: v is None or _is_str_list(v),
    "drillLo": _is_int_or_none,
    "drillHi": _is_int_or_none,
    "lastView": lambda v: isinstance(v, str),
    "lastPattern": lambda v: v is None or isinstance(v, str),
    "lastSection": lambda v: v is None or isinstance(v, str),
    "theme": lambda v: v in ("system", "light", "dark"),
}
assert set(SETTING_RULES) == set(store.DEFAULT_SETTINGS)


def _validate_settings_patch(patch):
    """Return (clean_patch, error). Unknown keys and wrong types are errors so
    a client bug never silently poisons the shared settings file."""
    if not isinstance(patch, dict):
        return None, "bad request"
    clean = {}
    for k, v in patch.items():
        rule = SETTING_RULES.get(k)
        if rule is None:
            return None, f"unknown setting: {k}"
        if not rule(v):
            return None, f"bad value for {k}"
        clean[k] = v
    return clean, None


def _activity_payload():
    """Heatmap data, cached until the next review action."""
    global _ACTIVITY
    if _ACTIVITY is None:
        days = store.activity(store.load_events())
        _ACTIVITY = {"days": days, "first": min(days) if days else None}
    return _ACTIVITY


class Handler(SimpleHTTPRequestHandler):
    # Trust our own table over the OS registry: on Windows, `mimetypes` can map
    # .js to text/plain, which makes browsers refuse ES modules.
    extensions_map = {
        **SimpleHTTPRequestHandler.extensions_map,
        ".js": "text/javascript",
        ".mjs": "text/javascript",
        ".css": "text/css",
        ".svg": "image/svg+xml",
        ".json": "application/json",
        ".md": "text/markdown; charset=utf-8",
        ".woff2": "font/woff2",
        ".woff": "font/woff",
        ".ttf": "font/ttf",
        ".gif": "image/gif",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC), **kwargs)

    def end_headers(self):
        # Always revalidate: static files still get 304s via Last-Modified /
        # If-Modified-Since (SimpleHTTPRequestHandler), API responses never
        # come from a cache.
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    def send_json(self, obj, status=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_problems(self):
        if self.headers.get("If-None-Match") == _PROBLEMS_ETAG:
            self.send_response(304)
            self.send_header("ETag", _PROBLEMS_ETAG)
            self.end_headers()
            return
        accept = self.headers.get("Accept-Encoding", "")
        use_gzip = "gzip" in [t.split(";")[0].strip() for t in accept.split(",")]
        body = _PROBLEMS_GZ if use_gzip else _PROBLEMS_RAW
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("ETag", _PROBLEMS_ETAG)
        self.send_header("Vary", "Accept-Encoding")
        if use_gzip:
            self.send_header("Content-Encoding", "gzip")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def do_GET(self):
        path = urlsplit(self.path).path
        if path == "/api/progress":
            with LOCK:
                self.send_json(PROGRESS)
        elif path == "/api/data-dir":
            self.send_json({"path": str(store.LOG_FILE.parent)})
        elif path == "/api/settings":
            with LOCK:
                self.send_json(SETTINGS)
        elif path == "/api/activity":
            with LOCK:
                self.send_json(_activity_payload())
        elif path == "/api/about":
            self.send_json(about())
        elif path == "/data/problems.json":
            self._send_problems()
        elif path.startswith("/api/") or path.startswith("/data/"):
            self.send_json({"error": "not found"}, 404)
        else:
            super().do_GET()

    def do_HEAD(self):
        if urlsplit(self.path).path == "/data/problems.json":
            self._send_problems()
        else:
            super().do_HEAD()

    def _read_json(self):
        length = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(length))

    def do_POST(self):
        path = urlsplit(self.path).path
        if path == "/api/review":
            self._handle_review()
        elif path == "/api/data-dir":
            self._handle_set_data_dir()
        elif path == "/api/settings":
            self._handle_settings()
        else:
            self.send_json({"error": "not found"}, 404)

    def _handle_review(self):
        global PROGRESS, _ACTIVITY
        try:
            req = self._read_json()
            slug, action = req["slug"], req["action"]
        except (ValueError, KeyError, TypeError, json.JSONDecodeError):
            self.send_json({"error": "bad request"}, 400)
            return
        if slug not in SLUGS:
            self.send_json({"error": f"unknown slug: {slug}"}, 400)
            return
        if action not in ACTIONS and action != store.UNDO:
            self.send_json({"error": f"unknown action: {action}"}, 400)
            return
        with LOCK:
            today = date.today().isoformat()
            if action == store.UNDO:
                # Replaying the whole log (a few thousand lines at most) is
                # far cheaper than reasoning about an inverse; it also keeps
                # the snapshot identical to what a fresh start would compute.
                events = store.load_events()
                if not any(e["slug"] == slug for e in store.effective_events(events)):
                    self.send_json({"error": "nothing to undo"}, 400)
                    return
                events.append(store.append_event(slug, action, today))
                PROGRESS = store.replay(events)
                entry = PROGRESS.get(slug)
                undoable = any(e["slug"] == slug for e in store.effective_events(events))
            else:
                entry = apply_action(PROGRESS.get(slug), action, today)
                store.append_event(slug, action, today)
                if entry is None:
                    PROGRESS.pop(slug, None)
                else:
                    PROGRESS[slug] = entry
                undoable = True
            store.save_snapshot(PROGRESS)
            _ACTIVITY = None
        if AUTOCOMMIT:
            schedule_commit()
        self.send_json({"slug": slug, "entry": entry, "undoable": undoable})

    def _handle_settings(self):
        global SETTINGS
        try:
            req = self._read_json()
        except (ValueError, json.JSONDecodeError):
            self.send_json({"error": "bad request"}, 400)
            return
        if isinstance(req, dict) and req.get("reset") is True:
            clean = json.loads(json.dumps(store.DEFAULT_SETTINGS))
            replace = True
        else:
            clean, err = _validate_settings_patch(req)
            replace = False
            if err:
                self.send_json({"error": err}, 400)
                return
        with LOCK:
            SETTINGS = clean if replace else {**SETTINGS, **clean}
            store.save_settings(SETTINGS)
            self.send_json(SETTINGS)

    def _handle_set_data_dir(self):
        try:
            path = str(self._read_json()["path"]).strip()
        except (ValueError, KeyError, json.JSONDecodeError):
            self.send_json({"error": "bad request"}, 400)
            return
        if not path:
            self.send_json({"error": "empty path"}, 400)
            return
        try:
            newpath = switch_data_dir(path)
        except OSError as e:
            self.send_json({"error": f"cannot use that folder: {e}"}, 400)
            return
        with LOCK:
            self.send_json({"path": newpath, "progress": PROGRESS})

    def log_message(self, fmt, *args):
        pass  # keep the terminal quiet


def switch_data_dir(path):
    """Point storage at `path`, merging any progress already there with the
    current progress so nothing is lost in either direction (adopt a synced
    folder's history AND keep local history), reload, and remember the choice.
    Returns the new absolute path as a string. Raises OSError if unusable."""
    global PROGRESS
    target = Path(path).expanduser()
    current_dir = store.LOG_FILE.parent
    if target.resolve() == current_dir.resolve():
        config.set_data_dir(str(target))  # same folder: just remember it
        return str(target)
    global SETTINGS, _ACTIVITY
    with LOCK:
        current_events = store.load_events()          # from the old dir
        store.set_data_dir(str(target))               # LOG_FILE now points at target
        merged = store.merge_events(current_events, store.load_events())
        store.write_events(merged)                    # lossless union in the new dir
        PROGRESS = store.replay(merged)
        store.save_snapshot(PROGRESS)
        _ACTIVITY = None
        # Preferences are not merged: adopt the synced folder's if it has one
        # (that is what "sync across machines" means), else seed it with ours.
        if store.SETTINGS_FILE.exists():
            SETTINGS = store.load_settings()
        else:
            store.save_settings(SETTINGS)
    config.set_data_dir(str(target))
    return str(target)


def about():
    return {
        "name": config.APP_NAME,
        "version": __version__,
        "python": platform.python_version(),
        "dataDir": str(store.LOG_FILE.parent),
        "configFile": str(config.config_file()),
        "problemsSnapshot": PROBLEMS_SNAPSHOT,
        "problems": len(SLUGS),
        "desktop": DESKTOP,
    }


def configure(data_dir=None, autocommit=False, push=False, desktop=False):
    """Load progress and settings, and set backup options. Call once before
    make_server().

    Shared by the CLI (main) and the desktop launcher so both go through the
    same startup path. data_dir=None keeps store's default (./data)."""
    global AUTOCOMMIT, PUSH, PROGRESS, SETTINGS, DESKTOP, _ACTIVITY
    AUTOCOMMIT, PUSH, DESKTOP = autocommit, push, desktop
    if data_dir is not None:
        store.set_data_dir(data_dir)
    PROGRESS = store.load_progress()
    SETTINGS = store.load_settings()
    _ACTIVITY = None


def make_server(port=8765, host="127.0.0.1"):
    """Build (but don't start) the tracker HTTP server. Pass port=0 to let the
    OS pick a free port; read the chosen port from server.server_address[1]."""
    return ThreadingHTTPServer((host, port), Handler)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--data-dir", default=None,
                    help="directory for reviews.jsonl + progress.json "
                         "(default: last folder chosen in the UI, else ./data)")
    ap.add_argument("--autocommit", action="store_true",
                    help="git-commit progress files in the data dir after review activity")
    ap.add_argument("--push", action="store_true",
                    help="also git-push the data dir's repo after each autocommit")
    args = ap.parse_args()
    data_dir = args.data_dir or config.get_data_dir() or str(ROOT / "data")
    configure(data_dir=data_dir, autocommit=args.autocommit, push=args.push)
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
