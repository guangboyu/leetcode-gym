"""Per-user app config: the chosen data (sync) folder and the window geometry.

Stored OUTSIDE the data dir so the settings survive when the data dir is
repointed at a fresh/cloud folder. Location follows OS convention:

    Windows : %APPDATA%\\LeetCode Gym\\config.json
    macOS   : ~/Library/Application Support/LeetCode Gym/config.json
    else    : $XDG_CONFIG_HOME/LeetCode Gym  (or ~/.config/LeetCode Gym)

Migration: the app used to be "LeetCodeTracker". The first time the new config
file is missing and the old one exists, it is copied over (the old file is
left untouched, so downgrading still works).

Set $LEETCODE_TRACKER_CONFIG_DIR to override the location (used by tests; the
legacy migration is skipped under the override so tests never read a real
user's config). Stdlib only, like the rest of the server.
"""
import json
import os
import shutil
import sys
from pathlib import Path

APP_NAME = "LeetCode Gym"      # product name: window title, menus, About
APP = APP_NAME                 # config directory name
LEGACY_APP = "LeetCodeTracker"  # pre-0.2 config directory name
ENV_OVERRIDE = "LEETCODE_TRACKER_CONFIG_DIR"


def _base_dir():
    if sys.platform == "win32":
        return Path(os.environ.get("APPDATA") or (Path.home() / "AppData" / "Roaming"))
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support"
    return Path(os.environ.get("XDG_CONFIG_HOME") or (Path.home() / ".config"))


def config_dir():
    override = os.environ.get(ENV_OVERRIDE)
    if override:
        return Path(override).expanduser()
    return _base_dir() / APP


def legacy_config_dir():
    """Where a pre-0.2 install kept its config, or None under the test override."""
    if os.environ.get(ENV_OVERRIDE):
        return None
    return _base_dir() / LEGACY_APP


def config_file():
    return config_dir() / "config.json"


def migrate_legacy():
    """One-time copy of the old LeetCodeTracker config.json. Returns True if a
    copy happened. Never overwrites an existing new-style config."""
    new = config_file()
    if new.exists():
        return False
    legacy_dir = legacy_config_dir()
    if not legacy_dir:
        return False
    old = legacy_dir / "config.json"
    if not old.is_file():
        return False
    try:
        new.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(old, new)
        return True
    except OSError:
        return False


def load():
    migrate_legacy()
    try:
        return json.loads(config_file().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def save(cfg):
    d = config_dir()
    d.mkdir(parents=True, exist_ok=True)
    tmp = config_file().with_suffix(".json.tmp")
    tmp.write_text(json.dumps(cfg, indent=1), encoding="utf-8")
    os.replace(tmp, config_file())


def get_data_dir():
    """The saved data-dir path, or None if the user hasn't chosen one."""
    return load().get("data_dir") or None


def set_data_dir(path):
    cfg = load()
    cfg["data_dir"] = str(path)
    save(cfg)


WINDOW_KEYS = ("x", "y", "width", "height")


def get_window():
    """Last saved window rect {x, y, width, height} (ints), or None."""
    rect = load().get("window")
    if not isinstance(rect, dict):
        return None
    try:
        out = {k: int(rect[k]) for k in WINDOW_KEYS}
    except (KeyError, TypeError, ValueError):
        return None
    if out["width"] <= 0 or out["height"] <= 0:
        return None
    return out


def set_window(rect):
    """Remember the window rect. Only the four geometry keys are stored."""
    cfg = load()
    cfg["window"] = {k: int(rect[k]) for k in WINDOW_KEYS}
    save(cfg)
