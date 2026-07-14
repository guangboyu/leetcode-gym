# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec: build a standalone desktop app for the study tracker.

Run from the REPO ROOT (paths below are repo-relative):
    pyinstaller --noconfirm packaging/LeetCodeTracker.spec

Produces a one-file executable in dist/:
    Windows -> dist/LeetCodeTracker.exe
    macOS   -> dist/LeetCodeTracker  (+ dist/LeetCodeTracker.app bundle)
PyInstaller can't cross-compile: build once on Windows, once on macOS.
"""
import os
import sys

from PyInstaller.utils.hooks import collect_all

# Anchor every path to the repo root (parent of this spec's folder) so the build
# works regardless of the current directory. SPECPATH is injected by PyInstaller.
REPO = os.path.dirname(SPECPATH)

# Read-only assets the server serves, as (source, dest-dir-inside-bundle).
# Layout must match tracker.resources.resource_root(): <root>/tracker/static
# and <root>/data/problems.json.
datas = [
    (os.path.join(REPO, "tracker", "static"), "tracker/static"),
    (os.path.join(REPO, "data", "problems.json"), "data"),
]

# pywebview picks its GUI backend at runtime (EdgeChromium/pythonnet on Windows,
# WKWebView on macOS), so collect the whole package rather than guess imports.
wv_datas, wv_binaries, wv_hiddenimports = collect_all("webview")
datas += wv_datas

a = Analysis(
    [os.path.join(REPO, "desktop_app.py")],
    pathex=[REPO],
    binaries=wv_binaries,
    datas=datas,
    hiddenimports=wv_hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="LeetCodeTracker",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,           # UPX often flags AV false-positives on Windows; skip it
    runtime_tmpdir=None,
    console=False,       # windowed app: no terminal window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

# On macOS, wrap the executable in a .app bundle so it launches like a native app.
if sys.platform == "darwin":
    app = BUNDLE(
        exe,
        name="LeetCodeTracker.app",
        icon=None,
        bundle_identifier="io.github.leetcode-study-tracker",
        info_plist={
            "NSHighResolutionCapable": True,
            "LSBackgroundOnly": False,
        },
    )
