"""tracker/static/js/pyhl.js must stay a faithful port of the GIF renderer's
Python tokenizer (tutorials/anim/dsaviz/draw.py): same keyword and builtin
sets, same token regex. Both files are read as text — draw.py imports PIL,
which the tracker deliberately does not depend on.
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DRAW = ROOT / "tutorials" / "anim" / "dsaviz" / "draw.py"
PYHL = ROOT / "tracker" / "static" / "js" / "pyhl.js"


def _py_set(src, name):
    m = re.search(name + r"\s*=\s*\{(.*?)\}", src, re.S)
    assert m, f"{name} not found in draw.py"
    return set(re.findall(r'"([^"]+)"', m.group(1)))


def _js_set(src, name):
    m = re.search(r"export const " + name + r"\s*=\s*new Set\(\[(.*?)\]\);", src, re.S)
    assert m, f"{name} not found in pyhl.js"
    return set(re.findall(r'"([^"]+)"', m.group(1)))


class PyhlParity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.py = DRAW.read_text(encoding="utf-8")
        cls.js = PYHL.read_text(encoding="utf-8")

    def test_keywords_match(self):
        self.assertEqual(_js_set(self.js, "KEYWORDS"), _py_set(self.py, "KEYWORDS"))

    def test_builtins_match(self):
        self.assertEqual(_js_set(self.js, "BUILTINS"), _py_set(self.py, "BUILTINS"))

    def test_token_alternation_order(self):
        """The JS regex keeps draw.py's group order: comment, string, number, word, op, ws."""
        m = re.search(r"const TOKEN_RE = /(.*)/g;", self.js)
        self.assertIsNotNone(m)
        js_re = m.group(1)
        expected = [r"(#.*$)", "(\"[^\"]*\"|'[^']*')", r"(\b\d+(?:\.\d+)?\b)",
                    r"([A-Za-z_][A-Za-z_0-9]*)", r"([^A-Za-z_0-9\s]+)", r"(\s+)"]
        self.assertEqual(js_re, "|".join(expected))
        for group in ("com", "str", "num", "word", "op", "ws"):
            self.assertIn(f"(?P<{group}>", self.py)


if __name__ == "__main__":
    unittest.main()
