#!/usr/bin/env bash
# Run the JS unit tests with macOS's built-in JavaScriptCore (no node needed).
#   tests/js/run_jsc.sh            all tests
#   tests/js/run_jsc.sh route      only tests/js/route.test.js
# Exit code is non-zero if any test fails. CI runs the same files with
# `node --test tests/js`.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
JSC="${JSC:-/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc}"
if [ ! -x "$JSC" ]; then
  echo "jsc not found at $JSC (macOS only; use: node --test tests/js)" >&2
  exit 2
fi
status=0
for t in "$ROOT"/tests/js/${1:-*}.test.js; do
  echo "$(basename "$t")"
  # One global scope: harness, then the code under test, then the test file,
  # then a one-line summary that throws (-> non-zero exit) on any failure.
  if ! "$JSC" "$ROOT/tests/js/harness.js" "$ROOT/tracker/static/route.js" "$t" \
        -e "__summary()" -- "$ROOT"; then
    status=1
  fi
done
exit $status
