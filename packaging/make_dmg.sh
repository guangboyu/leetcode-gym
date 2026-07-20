#!/usr/bin/env bash
# Package dist/LeetCodeTracker.app into a drag-to-install .dmg.
#
# Prereq:  bash packaging/build_macos.sh   (produces dist/LeetCodeTracker.app)
# Run:     bash packaging/make_dmg.sh
# Output:  dist/LeetCodeTracker.dmg
#
# The disk image contains the app plus a symlink to /Applications, so the user
# opens the DMG and drags the icon onto the Applications shortcut — the standard
# macOS install gesture. Uses only the built-in `hdiutil` (no extra tooling).
set -euo pipefail

# Repo root = parent of this script's folder.
cd "$(dirname "$0")/.."

APP="dist/LeetCodeTracker.app"
VOLNAME="LeetCode Study Tracker"
DMG="dist/LeetCodeTracker.dmg"

if [ ! -d "$APP" ]; then
    echo "error: $APP not found — build it first:" >&2
    echo "       bash packaging/build_macos.sh" >&2
    exit 1
fi

# Stage the DMG contents in a temp folder: the app + an /Applications shortcut.
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT
cp -R "$APP" "$STAGE/"
ln -s /Applications "$STAGE/Applications"

# Compressed (UDZO) read-only image, overwriting any previous build.
rm -f "$DMG"
hdiutil create \
    -volname "$VOLNAME" \
    -srcfolder "$STAGE" \
    -fs HFS+ \
    -format UDZO \
    -ov \
    "$DMG" >/dev/null

echo ""
echo "Built: $(pwd)/$DMG"
echo "Share this file. Recipients: open it, drag LeetCodeTracker onto Applications."
echo "First launch (unsigned): right-click the app -> Open, then confirm once."
