#!/usr/bin/env python3
"""LeetCode study tracker — local web UI. Stdlib only.

    python3 tracker/server.py [--port 8765]

Serves tracker/static/ plus:
    GET  /data/problems.json   the merged problem table (read-only input)
    GET  /api/progress         all progress entries (data/progress.json)
    POST /api/review           {"slug": ..., "action": "solved"|"forgotten"|"reset"}
                               -> {"slug": ..., "entry": <updated entry or null>}
"""
import argparse
import json
import os
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tracker.scheduler import ACTIONS, apply_action

ROOT = Path(__file__).resolve().parent.parent
STATIC = ROOT / "tracker" / "static"
PROBLEMS_FILE = ROOT / "data" / "problems.json"
PROGRESS_FILE = ROOT / "data" / "progress.json"

LOCK = threading.Lock()
SLUGS = frozenset(json.loads(PROBLEMS_FILE.read_text(encoding="utf-8"))["problems"])


def load_progress():
    if not PROGRESS_FILE.exists():
        return {}
    return json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))


def save_progress(progress):
    tmp = PROGRESS_FILE.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(progress, ensure_ascii=False, indent=1) + "\n",
                   encoding="utf-8")
    os.replace(tmp, PROGRESS_FILE)


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
                self.send_json(load_progress())
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
            progress = load_progress()
            entry = apply_action(progress.get(slug), action)
            if entry is None:
                progress.pop(slug, None)
            else:
                progress[slug] = entry
            save_progress(progress)
        self.send_json({"slug": slug, "entry": entry})

    def log_message(self, fmt, *args):
        pass  # keep the terminal quiet


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--port", type=int, default=8765)
    args = ap.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"Tracking {len(SLUGS)} problems — open http://localhost:{args.port}")
    print(f"Progress file: {PROGRESS_FILE}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nbye")


if __name__ == "__main__":
    main()
