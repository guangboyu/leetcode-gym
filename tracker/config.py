"""Per-user app config — currently just the chosen data (sync) folder.

Stored OUTSIDE the data dir so the setting survives when the data dir is
repointed at a fresh/cloud folder. Location follows OS convention:

    Windows : %APPDATA%\\LeetCodeTracker\\config.json
    macOS   : ~/Library/Application Support/LeetCodeTracker/config.json
    else    : $XDG_CONFIG_HOME/LeetCodeTracker  (or ~/.config/LeetCodeTracker)

Set $LEETCODE_TRACKER_CONFIG_DIR to override the location (used by tests).
Stdlib only, like the rest of the server.
"""
import json
import os
import sys
from pathlib import Path

APP = "LeetCodeTracker"


def config_dir():
    override = os.environ.get("LEETCODE_TRACKER_CONFIG_DIR")
    if override:
        return Path(override).expanduser()
    if sys.platform == "win32":
        base = os.environ.get("APPDATA") or (Path.home() / "AppData" / "Roaming")
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = os.environ.get("XDG_CONFIG_HOME") or (Path.home() / ".config")
    return Path(base) / APP


def config_file():
    return config_dir() / "config.json"


def load():
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
