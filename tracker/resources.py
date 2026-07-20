"""Locating bundled, read-only assets (static files + problems.json).

Works both when running from source and when packaged by PyInstaller. In a
frozen one-file build the bundled data is unpacked to a temp dir exposed as
``sys._MEIPASS``; from source it lives at the repository root.

Note: this is only for READ-ONLY assets shipped inside the app. Writable
progress data (reviews.jsonl / progress.json) must never live here — under a
frozen build ``resource_root()`` is a temp dir that is wiped on exit. The
desktop launcher points those at a persistent per-user directory instead
(see ``tracker.desktop.default_data_dir``).
"""
import sys
from pathlib import Path


def is_frozen() -> bool:
    """True when running inside a PyInstaller (or similar) bundle."""
    return getattr(sys, "frozen", False)


def resource_root() -> Path:
    """Directory holding shipped assets: ``tracker/static`` and ``data/problems.json``."""
    if is_frozen():
        return Path(sys._MEIPASS)  # type: ignore[attr-defined]
    return Path(__file__).resolve().parent.parent
