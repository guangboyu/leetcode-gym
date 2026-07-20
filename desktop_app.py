#!/usr/bin/env python3
"""PyInstaller entry point for the desktop app.

Kept at the repository root (not inside the `tracker` package) so that
`from tracker.desktop import main` resolves cleanly both from source and when
frozen. Build with: pyinstaller packaging/LeetCodeTracker.spec
"""
from tracker.desktop import main

if __name__ == "__main__":
    main()
