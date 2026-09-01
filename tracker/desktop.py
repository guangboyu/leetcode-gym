#!/usr/bin/env python3
"""Native desktop wrapper for the LeetCode study tracker.

Runs the stdlib HTTP server (tracker/server.py) on a private localhost port in a
background thread, then shows it in a native OS window via pywebview — no browser
tab, no terminal. pywebview is the ONLY third-party dependency, and it's imported
lazily inside run(), so the server itself stays stdlib-only.

Run from source:   python -m tracker.desktop        (or: python desktop_app.py)
Packaged:          double-click the built "LeetCode Gym" app.

Progress (reviews.jsonl / progress.json / settings.json) lives in a persistent
per-user directory — NEVER inside the app bundle, which is read-only and, for a
frozen build, a temp dir wiped on exit. Resolution order:
    1. --data-dir argument
    2. folder chosen in the Settings UI (tracker/config.py)
    3. $LEETCODE_TRACKER_DATA   (point at a Dropbox folder to sync machines)
    4. ~/LeetCodeTracker, if it exists (pre-0.2 default; never moved silently)
    5. <config dir>/data  (e.g. ~/Library/Application Support/LeetCode Gym/data)
"""
import os
import sys
import threading
import traceback
from pathlib import Path

from tracker import config, server

APP_NAME = config.APP_NAME
LEGACY_DATA_DIR_NAME = "LeetCodeTracker"
WINDOW_SIZE = (1200, 860)
MIN_WINDOW_SIZE = (900, 600)


def default_data_dir():
    """Persistent per-user location for progress files (before any UI choice).

    An existing ~/LeetCodeTracker (the pre-0.2 default) keeps being used so an
    upgrade never silently changes where a user's history lives; fresh installs
    get a folder under the OS config dir instead of a visible one in $HOME."""
    env = os.environ.get("LEETCODE_TRACKER_DATA")
    if env:
        return Path(env).expanduser()
    legacy = Path.home() / LEGACY_DATA_DIR_NAME
    if legacy.is_dir():
        return legacy
    return config.config_dir() / "data"


def resolve_data_dir(arg=None):
    """Where progress lives, most-intentional first:
    explicit --data-dir  >  folder chosen in the UI (config)  >  default."""
    if arg:
        return Path(arg).expanduser()
    saved = config.get_data_dir()
    if saved:
        return Path(saved).expanduser()
    return default_data_dir()


class _Api:
    """Bridge exposed to the page as ``window.pywebview.api``. Lets the Settings
    dialog open a real OS folder picker (the browser can't)."""

    def __init__(self):
        self.window = None

    def choose_folder(self):
        import webview
        result = self.window.create_file_dialog(webview.FOLDER_DIALOG)
        if not result:
            return None
        return result[0] if isinstance(result, (list, tuple)) else result


def _log_crash(exc, data_dir):
    """A windowed build has no console, so drop the traceback beside the data
    where a failed launch can still be diagnosed. Returns the log path."""
    log = Path(data_dir) / "desktop-error.log"
    try:
        Path(data_dir).mkdir(parents=True, exist_ok=True)
        with log.open("a", encoding="utf-8") as f:
            f.write("".join(traceback.format_exception(exc)))
            f.write("\n")
    except OSError:
        pass
    return log


def selftest(report_path, data_dir):
    """Headless smoke test of the PACKAGED runtime: start the server from the
    (possibly frozen) bundle, fetch its endpoints, write a JSON report, and
    return an exit code — without opening a window. Lets a build be verified in
    CI or by hand. Trigger by setting $LEETCODE_TRACKER_SELFTEST to a file path.
    """
    import json
    import urllib.request

    from tracker import resources

    server.configure(data_dir=str(data_dir))
    httpd = server.make_server(port=0)
    port = httpd.server_address[1]
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/data/problems.json") as r:
            problems = json.loads(r.read()).get("problems", {})
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/") as r:
            index_ok = r.status == 200 and b"<title>" in r.read()
    finally:
        httpd.shutdown()
        httpd.server_close()

    ok = bool(problems) and index_ok
    report = {"ok": ok, "frozen": resources.is_frozen(),
              "problems": len(problems), "index_ok": index_ok}
    Path(report_path).write_text(json.dumps(report), encoding="utf-8")
    return 0 if ok else 1


def run(data_dir=None):
    """Start the server on a free port and open the native window (blocks until
    the window is closed)."""
    import webview  # lazy: keeps the module importable without the GUI dep

    data_dir = resolve_data_dir(data_dir)
    server.configure(data_dir=str(data_dir), desktop=True)
    httpd = server.make_server(port=0)  # port 0 -> OS picks a free port
    port = httpd.server_address[1]
    threading.Thread(target=httpd.serve_forever, daemon=True,
                     name="tracker-http").start()

    api = _Api()
    window = webview.create_window(APP_NAME, f"http://127.0.0.1:{port}/",
                                   width=WINDOW_SIZE[0], height=WINDOW_SIZE[1],
                                   min_size=MIN_WINDOW_SIZE, js_api=api)
    api.window = window
    try:
        webview.start()
    finally:
        httpd.shutdown()      # stop serve_forever cleanly on window close
        httpd.server_close()  # release the listening socket


def main():
    import argparse
    ap = argparse.ArgumentParser(description=f"{APP_NAME} (desktop window)")
    ap.add_argument("--data-dir", default=None,
                    help="where progress is stored (default: the folder chosen in "
                         "Settings, $LEETCODE_TRACKER_DATA, ~/LeetCodeTracker if it "
                         "exists, else the per-user config dir)")
    # parse_known_args: tolerate stray args a frozen app may be launched with
    args, _ = ap.parse_known_args()
    data_dir = resolve_data_dir(args.data_dir)

    report = os.environ.get("LEETCODE_TRACKER_SELFTEST")
    if report:  # build-verification mode: no window, just check + exit code
        sys.exit(selftest(report, data_dir))

    try:
        run(data_dir)
    except Exception as exc:  # last-resort crash log for the windowed build
        log = _log_crash(exc, data_dir)
        print(f"Fatal error — see {log}", file=sys.stderr)
        raise


if __name__ == "__main__":
    main()
