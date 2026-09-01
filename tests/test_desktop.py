"""The GUI-free parts of the desktop launcher: where progress lives by default.

tracker.desktop must import without pywebview (it is imported lazily inside
run()), so these tests run on any machine and in CI.
"""
import os
import sys
import tempfile
import unittest
from pathlib import Path
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


if __name__ == "__main__":
    unittest.main()
