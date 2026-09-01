"""Run the JavaScript unit tests (tests/js/*.test.js) as part of the Python
suite, using macOS's built-in JavaScriptCore so no node install is needed
locally. CI additionally runs the same files with `node --test tests/js`.
Skipped where jsc is absent (Linux/Windows without node)."""
import os
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JSC = Path(os.environ.get(
    "JSC", "/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc"))


@unittest.skipUnless(JSC.exists(), "JavaScriptCore (jsc) not available")
class TestJavaScript(unittest.TestCase):
    def test_js_suite_passes_under_jsc(self):
        r = subprocess.run(["bash", str(ROOT / "tests" / "js" / "run_jsc.sh")],
                           cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, "JS tests failed:\n" + r.stdout + r.stderr)
        self.assertIn("0 failed", r.stdout)
