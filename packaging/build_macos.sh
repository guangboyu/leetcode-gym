#!/usr/bin/env bash
# Build the standalone macOS desktop app.
#
# Prereqs (once):  pip3 install -r packaging/requirements.txt
# Run:             bash packaging/build_macos.sh
# Output:          dist/LeetCodeTracker.app   (double-click to run)
set -euo pipefail

# Repo root = parent of this script's folder.
cd "$(dirname "$0")/.."

pyinstaller --noconfirm --clean --distpath dist --workpath build/pyi \
    packaging/LeetCodeTracker.spec

echo ""
echo "Built: $(pwd)/dist/LeetCodeTracker.app"
echo "First launch: right-click -> Open (unsigned app; Gatekeeper asks once)."

# Package it into a drag-to-install .dmg for handing out to other people.
bash packaging/make_dmg.sh
