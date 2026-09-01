"""The GUI-free parts of the desktop launcher: where progress lives by default,
window-geometry memory, and the menu bar description.

tracker.desktop must import without pywebview (it is imported lazily inside
run()/build_menu()), so these tests run on any machine and in CI. The menu is
built against a tiny stand-in for webview.menu.
"""
import os
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tracker import config, desktop


class TestDefaultDataDir(unittest.TestCase):
    def setUp(self):
        self._cfg = tempfile.TemporaryDirectory()
        self._home = tempfile.TemporaryDirectory()
        os.environ["LEETCODE_TRACKER_CONFIG_DIR"] = self._cfg.name
        os.environ.pop("LEETCODE_TRACKER_DATA", None)
        self._patch = mock.patch.object(desktop.Path, "home", return_value=Path(self._home.name))
        self._patch.start()

    def tearDown(self):
        self._patch.stop()
        self._cfg.cleanup()
        self._home.cleanup()
        os.environ.pop("LEETCODE_TRACKER_CONFIG_DIR", None)
        os.environ.pop("LEETCODE_TRACKER_DATA", None)

    def test_app_name_comes_from_config(self):
        self.assertEqual(desktop.APP_NAME, config.APP_NAME)
        self.assertEqual(desktop.APP_NAME, "LeetCode Gym")

    def test_fresh_install_uses_config_dir(self):
        self.assertEqual(desktop.default_data_dir(), Path(self._cfg.name) / "data")

    def test_existing_legacy_home_folder_is_kept(self):
        legacy = Path(self._home.name) / "LeetCodeTracker"
        legacy.mkdir()
        self.assertEqual(desktop.default_data_dir(), legacy)

    def test_env_beats_everything(self):
        (Path(self._home.name) / "LeetCodeTracker").mkdir()
        os.environ["LEETCODE_TRACKER_DATA"] = str(Path(self._home.name) / "Dropbox" / "gym")
        self.assertEqual(desktop.default_data_dir(), Path(self._home.name) / "Dropbox" / "gym")

    def test_resolve_data_dir_precedence(self):
        (Path(self._home.name) / "LeetCodeTracker").mkdir()
        self.assertEqual(desktop.resolve_data_dir("/explicit"), Path("/explicit"))
        config.set_data_dir("/chosen")
        self.assertEqual(desktop.resolve_data_dir(None), Path("/chosen"))
        self.assertEqual(desktop.resolve_data_dir("/explicit"), Path("/explicit"))


def _screen(x, y, w, h):
    return SimpleNamespace(x=x, y=y, width=w, height=h)


class TestRestoreGeometry(unittest.TestCase):
    SCREENS = [_screen(0, 0, 1920, 1080), _screen(1920, 0, 2560, 1440)]

    def test_none_or_garbage_gives_default(self):
        self.assertEqual(desktop._restore_geometry(None, self.SCREENS), {})
        self.assertEqual(desktop._restore_geometry({"x": "a"}, self.SCREENS), {})
        self.assertEqual(desktop._restore_geometry({"x": 1, "y": 2}, self.SCREENS), {})

    def test_on_screen_rect_is_kept(self):
        r = {"x": 100, "y": 50, "width": 1180, "height": 800}
        self.assertEqual(desktop._restore_geometry(r, self.SCREENS), r)

    def test_rect_on_second_monitor_is_kept(self):
        r = {"x": 2200, "y": 100, "width": 1180, "height": 800}
        self.assertEqual(desktop._restore_geometry(r, self.SCREENS), r)

    def test_unplugged_monitor_rect_is_dropped(self):
        r = {"x": 2200, "y": 100, "width": 1180, "height": 800}
        self.assertEqual(desktop._restore_geometry(r, self.SCREENS[:1]), {})

    def test_barely_visible_rect_is_dropped(self):
        # Only 40 px of the window would be on screen: not enough to grab.
        r = {"x": 1880, "y": 100, "width": 1180, "height": 800}
        self.assertEqual(desktop._restore_geometry(r, self.SCREENS[:1]), {})

    def test_too_small_rect_is_dropped(self):
        r = {"x": 0, "y": 0, "width": 300, "height": 200}
        self.assertEqual(desktop._restore_geometry(r, self.SCREENS), {})

    def test_no_screens_gives_default(self):
        r = {"x": 0, "y": 0, "width": 1180, "height": 800}
        self.assertEqual(desktop._restore_geometry(r, []), {})


class TestGeometryPersistence(unittest.TestCase):
    def setUp(self):
        self._cfg = tempfile.TemporaryDirectory()
        os.environ["LEETCODE_TRACKER_CONFIG_DIR"] = self._cfg.name

    def tearDown(self):
        self._cfg.cleanup()
        os.environ.pop("LEETCODE_TRACKER_CONFIG_DIR", None)

    def test_saved_on_closing(self):
        g = desktop._Geometry()
        g.on_resized(1300.0, 850.0)
        g.on_moved(40.0, 60.0)
        self.assertIsNone(g.on_closing())  # never cancels the close
        self.assertEqual(config.get_window(), {"x": 40, "y": 60, "width": 1300, "height": 850})

    def test_incomplete_rect_not_saved(self):
        g = desktop._Geometry()
        g.on_resized(1300, 850)
        g.on_closing()
        self.assertIsNone(config.get_window())

    def test_fullscreen_rect_not_saved_but_restored_is(self):
        g = desktop._Geometry({"x": 1, "y": 2, "width": 1180, "height": 800})
        g.on_maximized()
        g.on_resized(2560, 1440)
        g.on_closing()
        self.assertIsNone(config.get_window())
        g.on_restored()
        g.on_resized(1180, 800)
        g.on_closing()
        self.assertEqual(config.get_window()["width"], 1180)

    def test_initial_rect_seeds_the_cache(self):
        # A window that was never moved/resized still remembers where it opened.
        g = desktop._Geometry({"x": 10, "y": 20, "width": 1180, "height": 800})
        g.on_closing()
        self.assertEqual(config.get_window(), {"x": 10, "y": 20, "width": 1180, "height": 800})


class _FakeMenu:
    def __init__(self, title, items=None):
        self.title, self.items = title, list(items or [])


class _FakeAction:
    def __init__(self, title, function):
        self.title, self.function = title, function


class _FakeSep:
    pass


FAKE_MENU_MOD = SimpleNamespace(Menu=_FakeMenu, MenuAction=_FakeAction, MenuSeparator=_FakeSep)


class TestMenu(unittest.TestCase):
    def _menus(self, window=None, native=None):
        window = window or SimpleNamespace(evaluate_js=mock.Mock(), minimize=mock.Mock())
        native = native or {n: mock.Mock() for n in
                            ("@minimize", "@zoom", "@help", "@open_data", "@reveal_log")}
        return desktop.build_menu(window, menu_mod=FAKE_MENU_MOD, native=native), window, native

    def test_structure_matches_spec(self):
        menus, _, _ = self._menus()
        self.assertEqual([m.title for m in menus], [t for t, _ in desktop.MENU_SPEC])
        go = next(m for m in menus if m.title == "Go")
        self.assertEqual([getattr(i, "title", "-") for i in go.items],
                         ["Learn", "Today", "Browse", "Drill", "Stats", "-",
                          "Search Problems", "-", "Back", "Forward"])
        self.assertTrue(all(isinstance(i, _FakeSep) for i in go.items if not hasattr(i, "title")))

    def test_keys_are_unique_single_characters_and_match_spec(self):
        keys = list(desktop.KEYS.values())
        self.assertEqual(len(keys), len(set(keys)), "two menu items share a ⌘ key")
        self.assertTrue(all(len(k) == 1 for k in keys))
        for (menu, title), key in desktop.KEYS.items():
            items = dict(desktop.MENU_SPEC)[menu]
            row = next(i for i in items if i and i[0] == title)
            self.assertEqual(row[3], key)
        # the shortcuts the plan promises
        self.assertEqual(desktop.KEYS[("__app__", "Settings…")], ",")
        self.assertEqual(desktop.KEYS[("Go", "Search Problems")], "f")
        self.assertEqual([desktop.KEYS[("Go", n)] for n in ("Learn", "Today", "Browse", "Drill", "Stats")],
                         ["1", "2", "3", "4", "5"])

    def test_page_items_dispatch_into_the_page(self):
        menus, window, _ = self._menus()
        go = next(m for m in menus if m.title == "Go")
        next(i for i in go.items if getattr(i, "title", "") == "Today").function()
        window.evaluate_js.assert_called_once_with('window.Gym && window.Gym.dispatch("go", "today")')

    def test_native_items_call_python(self):
        menus, window, native = self._menus()
        win = next(m for m in menus if m.title == "Window")
        next(i for i in win.items if getattr(i, "title", "") == "Minimize").function()
        native["@minimize"].assert_called_once()
        helpm = next(m for m in menus if m.title == "Help")
        next(i for i in helpm.items if getattr(i, "title", "") == "Reveal Log").function()
        native["@reveal_log"].assert_called_once()

    def test_dispatch_is_noop_safe_and_json_escaped(self):
        js = desktop.dispatch_js('go', 'a"b')
        self.assertTrue(js.startswith("window.Gym && "))
        self.assertIn('"a\\"b"', js)
        self.assertEqual(desktop.dispatch_js("shortcuts"), 'window.Gym && window.Gym.dispatch("shortcuts", null)')

    def test_dispatch_failure_does_not_raise(self):
        window = SimpleNamespace(evaluate_js=mock.Mock(side_effect=RuntimeError("gone")))
        menus, _, _ = self._menus(window=window)
        go = next(m for m in menus if m.title == "Go")
        next(i for i in go.items if getattr(i, "title", "") == "Learn").function()  # no exception


class TestApi(unittest.TestCase):
    def test_platform_report(self):
        p = desktop._Api().platform()
        self.assertIn(p["shell"], ("mac", "win", "linux"))
        self.assertEqual(p["shell"], desktop.shell_name())
        self.assertFalse(p["frozen"])

    def test_open_path_rejects_missing(self):
        self.assertFalse(desktop._Api().open_path("/definitely/not/here"))

    def test_reveal_log_prefers_log_file(self):
        with tempfile.TemporaryDirectory() as d:
            api = desktop._Api(d)
            opened = []
            api.open_path = lambda p: opened.append(Path(p)) or True
            api.reveal_log()
            self.assertEqual(opened[-1], Path(d))
            (Path(d) / desktop.LOG_NAME).write_text("boom")
            api.reveal_log()
            self.assertEqual(opened[-1], Path(d) / desktop.LOG_NAME)


if __name__ == "__main__":
    unittest.main()
