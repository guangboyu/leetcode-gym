#!/usr/bin/env bash
# Run the frontend module tests locally on macOS without node, using the
# JavaScriptCore shell that ships with the OS. CI uses `node tests/js/run.mjs`.
set -euo pipefail
cd "$(dirname "$0")/../.."
JSC="${JSC:-/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc}"
if [ ! -x "$JSC" ]; then
  echo "jsc not found at $JSC (set JSC=…)" >&2
  exit 2
fi
exec "$JSC" -m tests/js/run.mjs
