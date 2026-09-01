"""Per-user config: location, legacy migration, window geometry."""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tracker import config


class TestConfig(unittest.TestCase):
    def setUp(self):
        self._cfg = tempfile.TemporaryDirectory()
        os.environ["LEETCODE_TRACKER_CONFIG_DIR"] = self._cfg.name

    def tearDown(self):
        self._cfg.cleanup()
        os.environ.pop("LEETCODE_TRACKER_CONFIG_DIR", None)

    def test_names(self):
        self.assertEqual(config.APP_NAME, "LeetCode Gym")
        self.assertEqual(config.APP, "LeetCode Gym")
        self.assertEqual(config.LEGACY_APP, "LeetCodeTracker")

    def test_override_wins_and_disables_legacy_lookup(self):
        self.assertEqual(config.config_dir(), Path(self._cfg.name))
        self.assertIsNone(config.legacy_config_dir())

    def test_default_dirs_per_platform(self):
        os.environ.pop("LEETCODE_TRACKER_CONFIG_DIR")
        with mock.patch.object(config.sys, "platform", "darwin"), \
             mock.patch.object(config.Path, "home", return_value=Path("/Users/u")):
            self.assertEqual(config.config_dir(),
                             Path("/Users/u/Library/Application Support/LeetCode Gym"))
            self.assertEqual(config.legacy_config_dir(),
                             Path("/Users/u/Library/Application Support/LeetCodeTracker"))
        with mock.patch.object(config.sys, "platform", "win32"), \
             mock.patch.dict(os.environ, {"APPDATA": r"C:\Users\u\AppData\Roaming"}):
            self.assertEqual(config.config_dir(),
                             Path(r"C:\Users\u\AppData\Roaming") / "LeetCode Gym")
        with mock.patch.object(config.sys, "platform", "linux"), \
             mock.patch.dict(os.environ, {"XDG_CONFIG_HOME": "/x/cfg"}):
            self.assertEqual(config.config_dir(), Path("/x/cfg/LeetCode Gym"))

    def test_legacy_migration_copies_once_and_never_overwrites(self):
        with tempfile.TemporaryDirectory() as legacy:
            old = Path(legacy) / "config.json"
            old.write_text(json.dumps({"data_dir": "/old/data"}))
            with mock.patch.object(config, "legacy_config_dir", return_value=Path(legacy)):
                self.assertTrue(config.migrate_legacy())
                self.assertEqual(config.get_data_dir(), "/old/data")
                self.assertTrue(old.exists())                     # the old file is kept
                # A second call is a no-op, and the new file wins from now on.
                config.set_data_dir("/new/data")
                old.write_text(json.dumps({"data_dir": "/older/data"}))
                self.assertFalse(config.migrate_legacy())
                self.assertEqual(config.get_data_dir(), "/new/data")

    def test_no_legacy_means_empty_config(self):
        with mock.patch.object(config, "legacy_config_dir", return_value=Path("/nonexistent/x")):
            self.assertFalse(config.migrate_legacy())
            self.assertEqual(config.load(), {})
            self.assertIsNone(config.get_data_dir())

    def test_window_get_set(self):
        self.assertIsNone(config.get_window())
        config.set_window({"x": 10.0, "y": 20, "width": 1180, "height": 800, "extra": 1})
        self.assertEqual(config.get_window(), {"x": 10, "y": 20, "width": 1180, "height": 800})
        self.assertNotIn("extra", config.load()["window"])
        config.set_data_dir("/d")                                   # other keys survive
        self.assertEqual(config.get_window()["width"], 1180)
        cfg = config.load()
        cfg["window"] = {"x": 1, "y": 2}                            # corrupt -> None
        config.save(cfg)
        self.assertIsNone(config.get_window())
        cfg["window"] = {"x": 1, "y": 2, "width": 0, "height": 5}
        config.save(cfg)
        self.assertIsNone(config.get_window())


if __name__ == "__main__":
    unittest.main()
