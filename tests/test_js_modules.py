"""Run the frontend module tests (tests/js/*.test.mjs) from the Python suite.

Locally on macOS they run on the JavaScriptCore shell that ships with the OS;
in CI they run on node (see tests/js/README.md). When neither engine is
available the test is skipped rather than failed, so the Python suite stays
runnable on any machine.
"""
import os
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JSC = Path(os.environ.get(
    "JSC", "/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc"))


def _runner():
    if JSC.is_file() and os.access(JSC, os.X_OK):
        return [str(JSC), "-m", "tests/js/run.mjs"]
    node = shutil.which("node")
    if node:
        return [node, "tests/js/run.mjs"]
    return None


class JsModuleTests(unittest.TestCase):
    def test_js_modules(self):
        cmd = _runner()
        if not cmd:
            self.skipTest("neither jsc nor node is available")
        proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=120)
        output = proc.stdout + proc.stderr
        self.assertEqual(proc.returncode, 0, "JS module tests failed:\n" + output)
        self.assertNotIn("FAIL ", output)
        self.assertRegex(output, r"(\d+)/\1 passed")


if __name__ == "__main__":
    unittest.main()
