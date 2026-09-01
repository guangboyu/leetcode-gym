#!/usr/bin/env python3
"""Native desktop wrapper for LeetCode Gym.

Runs the stdlib HTTP server (tracker/server.py) on a private localhost port in a
background thread, then shows it in a native OS window via pywebview — no browser
tab, no terminal. pywebview is the ONLY third-party dependency, and it's imported
lazily inside run(), so the server itself stays stdlib-only and this module
imports cleanly on machines without the GUI stack (tests, CI).

Run from source:   python -m tracker.desktop        (or: python desktop_app.py)
Packaged:          double-click the built "LeetCode Gym" app.

What the wrapper adds on top of a plain window:
  * macOS: a hidden-inset title bar (traffic lights sit inside the sidebar), a
    real menu bar with ⌘ shortcuts, window size/position remembered between
    launches, dark mode following the system.
  * Everywhere: persistent WebKit storage (pywebview defaults to a private
    session that is wiped on every launch), text selection, a folder picker,
    "open folder"/"reveal log" helpers exposed to the page as
    ``window.pywebview.api``.

Menu items never carry logic of their own: each one calls
``window.Gym.dispatch(name, arg)`` in the page, the same entry point the in-page
keyboard shortcuts use, so the browser and the desktop app behave identically.

Progress (reviews.jsonl / progress.json / settings.json) lives in a persistent
per-user directory — NEVER inside the app bundle, which is read-only and, for a
frozen build, a temp dir wiped on exit. Resolution order:
    1. --data-dir argument
    2. folder chosen in the Settings UI (tracker/config.py)
    3. $LEETCODE_TRACKER_DATA   (point at a Dropbox folder to sync machines)
    4. ~/LeetCodeTracker, if it exists (pre-0.2 default; never moved silently)
    5. <config dir>/data  (e.g. ~/Library/Application Support/LeetCode Gym/data)
"""
import json
import os
import subprocess
import sys
import threading
import traceback
import webbrowser
from pathlib import Path

from tracker import __version__, config, server, store

APP_NAME = config.APP_NAME
LEGACY_DATA_DIR_NAME = "LeetCodeTracker"
DEFAULT_SIZE = (1280, 820)   # sidebar 200px + comfortable content pane
MIN_SIZE = (960, 640)
HELP_URL = "https://github.com/guangboyu/leetcode-gym#readme"
LOG_NAME = "desktop-error.log"

# Light/dark window backgrounds; must match --bg in tracker/static/css/tokens.css
# so the native window never flashes a different colour before the page paints.
BG_LIGHT = "#FFFFFF"
BG_DARK = "#1C1C1E"

# How far (px) a remembered window rect must overlap a screen to be reused.
MIN_VISIBLE = 100


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


def shell_name():
    """Short OS tag the page reads from ``?shell=`` to reserve the title-bar
    strip (mac), pick ⌘ vs Ctrl labels, etc."""
    if sys.platform == "darwin":
        return "mac"
    if sys.platform == "win32":
        return "win"
    return "linux"


def os_prefers_dark():
    """True when macOS is in Dark mode (used only to pick the window's initial
    background so it doesn't flash white). Other platforms: False."""
    if sys.platform != "darwin":
        return False
    try:
        out = subprocess.run(["defaults", "read", "-g", "AppleInterfaceStyle"],
                             capture_output=True, text=True, timeout=2)
        return out.returncode == 0 and "dark" in out.stdout.lower()
    except (OSError, subprocess.SubprocessError):
        return False


def _log(msg):
    """Non-fatal diagnostics. The windowed build has no console, so these only
    matter when run from a terminal; never raise from here."""
    try:
        print(f"[desktop] {msg}", file=sys.stderr)
    except Exception:
        pass


# --------------------------------------------------------------------------- #
# Menu bar
# --------------------------------------------------------------------------- #

# Platform-agnostic menu description. Each row is a menu title followed by its
# items; an item is (title, dispatch-name, dispatch-arg, key) where `key` is the
# single character used as the ⌘ key equivalent on macOS (None = no shortcut),
# or None for a separator. The special title "__app__" is pywebview's marker
# for "insert into the application menu" (after About). Items whose dispatch
# name starts with "@" are handled natively in Python (see _native_actions)
# instead of being forwarded to the page.
MENU_SPEC = [
    ("__app__", [
        ("Settings…", "go", "settings", ","),
    ]),
    ("Go", [
        ("Learn", "go", "learn", "1"),
        ("Today", "go", "today", "2"),
        ("Browse", "go", "browse", "3"),
        ("Drill", "go", "drill", "4"),
        ("Stats", "go", "stats", "5"),
        None,
        ("Search Problems", "search", None, "f"),
        None,
        ("Back", "history", "back", "["),
        ("Forward", "history", "forward", "]"),
    ]),
    ("Drill", [
        ("Draw Problem", "drill", "draw", "d"),
        ("Reveal", "drill", "reveal", "r"),
        None,
        ("Mark Solved", "drill", "solved", None),
        ("Mark Solved With Help", "drill", "solved_help", None),
        ("Mark Forgot", "drill", "forgotten", None),
        ("Skip", "drill", "skip", None),
    ]),
    ("Window", [
        ("Minimize", "@minimize", None, "m"),
        ("Zoom", "@zoom", None, None),
    ]),
    ("Help", [
        (f"{APP_NAME} Help", "@help", None, None),
        ("Keyboard Shortcuts", "shortcuts", None, "/"),
        None,
        ("Open Data Folder", "@open_data", None, None),
        ("Reveal Log", "@reveal_log", None, None),
    ]),
]

# (menu title, item title) -> ⌘ key, derived from the spec so the two can't drift.
KEYS = {(menu, item[0]): item[3]
        for menu, items in MENU_SPEC for item in items if item and item[3]}


def dispatch_js(name, arg=None):
    """The JS snippet a menu item runs in the page. No-op when the page has not
    installed window.Gym yet (e.g. during load), instead of throwing."""
    return (f"window.Gym && window.Gym.dispatch("
            f"{json.dumps(name)}, {json.dumps(arg)})")


def build_menu(window, menu_mod=None, native=None):
    """Turn MENU_SPEC into pywebview Menu objects.

    `menu_mod` is ``webview.menu`` (injectable so tests don't need pywebview);
    `native` maps "@name" actions to Python callables (defaults to
    _native_actions(window))."""
    if menu_mod is None:
        import webview.menu as menu_mod  # lazy: GUI dependency
    native = native if native is not None else _native_actions(window)
    menus = []
    for title, items in MENU_SPEC:
        entries = []
        for item in items:
            if item is None:
                entries.append(menu_mod.MenuSeparator())
                continue
            label, name, arg, _key = item
            if name.startswith("@"):
                fn = native[name]
            else:
                fn = _page_action(window, name, arg)
            entries.append(menu_mod.MenuAction(label, fn))
        menus.append(menu_mod.Menu(title, entries))
    return menus


def _page_action(window, name, arg):
    def run():
        try:
            window.evaluate_js(dispatch_js(name, arg))
        except Exception as exc:  # the window may be gone; menus must not crash
            _log(f"dispatch {name} failed: {exc}")
    return run


def _native_actions(window):
    api = getattr(window, "_gym_api", None)
    return {
        "@minimize": lambda: window.minimize(),
        "@zoom": lambda: api.zoom() if api else None,
        "@help": lambda: webbrowser.open(HELP_URL),
        "@open_data": lambda: api.open_path(store.LOG_FILE.parent) if api else None,
        "@reveal_log": lambda: api.reveal_log() if api else None,
    }


def _patch_menu_keys(window):
    """Give menu items their ⌘ shortcuts by title. pywebview's MenuAction has no
    shortcut field, and it installs the menu right before the run loop starts,
    so this runs after `loaded` and retries once if the menu isn't there yet."""
    try:
        import AppKit
        from PyObjCTools import AppHelper
    except ImportError:
        return

    def apply(retry=True):
        try:
            main = AppKit.NSApp.mainMenu()
            go = main.itemWithTitle_("Go") if main else None
            if go is None:
                if retry:
                    AppHelper.callLater(0.5, apply, False)
                return
            for (menu_title, item_title), key in KEYS.items():
                if menu_title == "__app__":
                    holder = main.itemAtIndex_(0).submenu()
                else:
                    top = main.itemWithTitle_(menu_title)
                    holder = top.submenu() if top else None
                item = holder.itemWithTitle_(item_title) if holder else None
                if item is None:
                    continue
                item.setKeyEquivalent_(key)
                item.setKeyEquivalentModifierMask_(AppKit.NSEventModifierFlagCommand)
            win_menu = main.itemWithTitle_("Window")
            if win_menu is not None:
                AppKit.NSApp.setWindowsMenu_(win_menu.submenu())
        except Exception as exc:
            _log(f"menu shortcuts not applied: {exc}")

    AppHelper.callAfter(apply)


# --------------------------------------------------------------------------- #
# macOS title bar
# --------------------------------------------------------------------------- #

def _style_titlebar_mac(window):
    """Hidden-inset title bar: the web content extends under a transparent
    title bar and the traffic lights sit inside the page's sidebar (the page
    reserves the strip via ?shell=mac). pywebview's own `frameless` hides the
    buttons entirely, so this is done on the NSWindow after creation.

    Runs from the `loaded` event, which pywebview fires on a worker thread —
    every AppKit call is marshalled to the main thread with callAfter. All
    failures are logged and ignored: a plain title bar beats a crash."""
    try:
        import AppKit
        from PyObjCTools import AppHelper
    except ImportError:
        return

    def apply():
        ns = window.native
        if ns is None:
            return
        try:
            ns.setStyleMask_(ns.styleMask() | AppKit.NSWindowStyleMaskFullSizeContentView)
            ns.setTitlebarAppearsTransparent_(True)
            ns.setTitleVisibility_(AppKit.NSWindowTitleHidden)
        except Exception as exc:
            _log(f"transparent titlebar failed: {exc}")
        try:
            # An empty unified-compact toolbar is what moves the traffic
            # lights down into the inset position (like Notes/Finder).
            tb = AppKit.NSToolbar.alloc().initWithIdentifier_("gym.toolbar")
            tb.setShowsBaselineSeparator_(False)
            ns.setToolbar_(tb)
            ns.setToolbarStyle_(AppKit.NSWindowToolbarStyleUnifiedCompact)
            ns.setTitlebarSeparatorStyle_(AppKit.NSTitlebarSeparatorStyleNone)
        except Exception as exc:
            _log(f"inset toolbar failed: {exc}")
        try:
            # Dynamic colour: follows light/dark switches while running.
            ns.setBackgroundColor_(AppKit.NSColor.windowBackgroundColor())
        except Exception as exc:
            _log(f"window background failed: {exc}")
        try:
            # pywebview paints the title-bar container view opaque for framed
            # windows (platforms/cocoa.py); make it see-through so the page's
            # sidebar colour shows behind the traffic lights.
            container = ns.contentView().superview().subviews().lastObject()
            if container is not None and container.respondsToSelector_("setBackgroundColor:"):
                container.setBackgroundColor_(AppKit.NSColor.clearColor())
        except Exception as exc:
            _log(f"titlebar container clear failed: {exc}")

    AppHelper.callAfter(apply)


# --------------------------------------------------------------------------- #
# Window geometry memory
# --------------------------------------------------------------------------- #

def _restore_geometry(rect, screens):
    """Pure: return `rect` if it is at least partly on one of `screens`
    (objects with x, y, width, height, top-left origin like pywebview's), else
    {} so the window falls back to the default size and cascade position.
    Guards against a remembered position on a monitor that is unplugged."""
    if not rect:
        return {}
    try:
        x, y, w, h = (int(rect[k]) for k in ("x", "y", "width", "height"))
    except (KeyError, TypeError, ValueError):
        return {}
    if w < MIN_SIZE[0] or h < MIN_SIZE[1]:
        return {}
    for s in screens or ():
        if (x < s.x + s.width - MIN_VISIBLE and x + w > s.x + MIN_VISIBLE
                and y < s.y + s.height - MIN_VISIBLE and y + h > s.y + MIN_VISIBLE):
            return {"x": x, "y": y, "width": w, "height": h}
    return {}


class _Geometry:
    """Collects the window rect from pywebview's resized/moved events and
    persists it on `closing` (the one event that runs synchronously on the
    caller's thread). A full-screen/maximized rect is never saved — reopening
    at screen size would be surprising, and macOS full screen is a mode, not a
    size."""

    def __init__(self, initial=None):
        self.rect = dict(initial or {})
        self.fullscreen = False

    def on_resized(self, width, height):
        self.rect.update(width=int(width), height=int(height))

    def on_moved(self, x, y):
        self.rect.update(x=int(x), y=int(y))

    def on_maximized(self):
        self.fullscreen = True

    def on_restored(self):
        self.fullscreen = False

    def complete(self):
        return all(k in self.rect for k in ("x", "y", "width", "height"))

    def on_closing(self):
        if not self.fullscreen and self.complete():
            try:
                config.set_window(self.rect)
            except Exception as exc:
                _log(f"window rect not saved: {exc}")
        return None  # not False: never cancel the close


# --------------------------------------------------------------------------- #
# JS bridge
# --------------------------------------------------------------------------- #

class _Api:
    """Bridge exposed to the page as ``window.pywebview.api`` — the few things
    a web page cannot do itself: native folder picker, window zoom, opening a
    folder in Finder/Explorer."""

    def __init__(self, data_dir=None):
        self.window = None
        self.data_dir = Path(data_dir) if data_dir else None

    def platform(self):
        return {"shell": shell_name(), "version": __version__, "frozen": bool(getattr(sys, "frozen", False))}

    def choose_folder(self):
        import webview
        result = self.window.create_file_dialog(webview.FOLDER_DIALOG)
        if not result:
            return None
        return result[0] if isinstance(result, (list, tuple)) else result

    def zoom(self):
        """macOS title-bar double-click behaviour (fit to screen / restore);
        maximize elsewhere."""
        if sys.platform == "darwin" and self.window is not None and self.window.native is not None:
            try:
                from PyObjCTools import AppHelper
                AppHelper.callAfter(self.window.native.performZoom_, None)
                return True
            except Exception as exc:
                _log(f"zoom failed: {exc}")
        if self.window is not None:
            self.window.maximize()
        return True

    def open_path(self, path):
        """Open an existing file/folder with the OS (Finder/Explorer)."""
        p = Path(str(path)).expanduser()
        if not p.exists():
            return False
        try:
            if sys.platform == "darwin":
                subprocess.Popen(["open", str(p)])
            elif sys.platform == "win32":
                os.startfile(str(p))  # type: ignore[attr-defined]
            else:
                subprocess.Popen(["xdg-open", str(p)])
            return True
        except OSError as exc:
            _log(f"open_path failed: {exc}")
            return False

    def reveal_log(self):
        """Open the crash log if there is one, else the data folder."""
        base = self.data_dir or Path(store.LOG_FILE).parent
        log = base / LOG_NAME
        return self.open_path(log if log.is_file() else base)


def _log_crash(exc, data_dir):
    """A windowed build has no console, so drop the traceback beside the data
    where a failed launch can still be diagnosed. Returns the log path."""
    log = Path(data_dir) / LOG_NAME
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
    report = {"ok": ok, "frozen": resources.is_frozen(), "version": __version__,
              "problems": len(problems), "index_ok": index_ok}
    Path(report_path).write_text(json.dumps(report), encoding="utf-8")
    return 0 if ok else 1


def _screens(webview):
    """pywebview exposes `screens` as a lazy list proxy in 6.x (a function in
    5.x); normalise to a plain list and never let it break startup."""
    try:
        s = webview.screens
        try:
            return list(s)
        except TypeError:
            return list(s())
    except Exception as exc:
        _log(f"screens unavailable: {exc}")
        return []


def _icon_path():
    """Dock/window icon when running from source (a frozen .app carries its own)."""
    from tracker import resources
    if resources.is_frozen():
        return None
    p = resources.resource_root() / "packaging" / "AppIcon.icns"
    return str(p) if p.is_file() else None


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

    # Only an element that IS the drag region drags the window, not everything
    # inside it — otherwise every button in the toolbar would start a drag.
    webview.settings["DRAG_REGION_DIRECT_TARGET_ONLY"] = True

    geo = _restore_geometry(config.get_window(), _screens(webview))
    api = _Api(data_dir)
    window = webview.create_window(
        APP_NAME, f"http://127.0.0.1:{port}/?shell={shell_name()}",
        js_api=api,
        width=geo.get("width", DEFAULT_SIZE[0]), height=geo.get("height", DEFAULT_SIZE[1]),
        x=geo.get("x"), y=geo.get("y"), min_size=MIN_SIZE,
        text_select=True,
        background_color=BG_DARK if os_prefers_dark() else BG_LIGHT,
    )
    api.window = window
    window._gym_api = api  # for the native menu actions

    g = _Geometry(geo)
    window.events.resized += g.on_resized
    window.events.moved += g.on_moved
    window.events.maximized += g.on_maximized
    window.events.restored += g.on_restored
    window.events.closing += g.on_closing
    if sys.platform == "darwin":
        window.events.loaded += _style_titlebar_mac
        window.events.loaded += _patch_menu_keys

    try:
        # private_mode=False keeps localStorage/IndexedDB between launches
        # (pywebview's default wipes them every start).
        webview.start(private_mode=False, menu=build_menu(window), icon=_icon_path())
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
