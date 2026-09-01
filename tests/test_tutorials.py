"""data/tutorials.json is generated from tutorials/*.md by scripts/build_tutorials.py.
These tests keep the committed file fresh and the tutorials' tables, anchors and
assets valid, and pin the parser's grammar with small inline fixtures."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import build_tutorials as bt  # noqa: E402

TUTORIALS_JSON = ROOT / "data" / "tutorials.json"
PROBLEMS_JSON = ROOT / "data" / "problems.json"
PATTERNS_JSON = ROOT / "data" / "patterns.json"

FIXTURE = """# Fixture Pattern

## Contents

- [Shape 1: alpha](#shape-1-alpha)
- [2a. Read and write](#2a-read-and-write)

## The one idea

Prose.

## Which shape

```python
pattern_template = True
```

## Shape 1: alpha

Alpha blurb.

```python
shape_template = 1
```

### Two Sum (LC 1)

```python
worked = True
```

### Alpha problems

| LC | Title | Diff | Freq | Note |
|---|---|---|---|---|
| 1 | Two Sum | Easy | 🔥🔥🔥 | the base case |
| 15 | 3Sum | Med | 🔥🔥 | see [contents](#contents) |

## Shape 2: chasing

Both pointers move left to right.

### 2a. Read and write

Read-write blurb.

#### Read and write problems

| LC | Title | Diff | State | Freq | Note |
|---|---|---|---|---|---|
| 283 | Move Zeroes | Easy | write idx | 🔥🔥🔥 | |

### 2b. Slow and fast

#### Floyd's cycle detection (LC 142)

#### Slow and fast problems

| LC | Title | Diff | Freq | Note |
|---|---|---|---|---|
| 141 | Linked List Cycle | Easy | 🔥🔥🔥 | phase 1 only |

## Pitfalls

## Drills

## Reference card
"""


def parse_fixture(text):
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "FixturePattern.md"
        path.write_text(text, encoding="utf-8")
        return bt.Parser(path, bt.load_catalog()).parse()


class TestGrammarFixture(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p = parse_fixture(FIXTURE)

    def test_no_errors(self):
        self.assertEqual(self.p.errors, [])

    def test_shape_ids_and_parents(self):
        shapes = {s["id"]: s for s in self.p.shapes}
        self.assertEqual(list(shapes), ["shape-1", "shape-2", "shape-2a", "shape-2b"])
        self.assertIsNone(shapes["shape-1"]["parent"])
        self.assertEqual(shapes["shape-2a"]["parent"], "shape-2")
        self.assertEqual(shapes["shape-2a"]["name"], "chasing: Read and write")

    def test_tables_attach_to_innermost_shape(self):
        shapes = {s["id"]: s for s in self.p.shapes}
        self.assertEqual([r["id"] for r in shapes["shape-1"]["problems"]], [1, 15])
        self.assertEqual(shapes["shape-2"]["problems"], [])       # parent owns no table
        self.assertEqual([r["id"] for r in shapes["shape-2a"]["problems"]], [283])
        self.assertEqual([r["id"] for r in shapes["shape-2b"]["problems"]], [141])

    def test_row_fields(self):
        row = self.p.shapes[0]["problems"][1]
        self.assertEqual(row["slug"], "3sum")
        self.assertEqual(row["diff"], "Medium")
        self.assertEqual(row["freq"], 2)
        self.assertEqual(row["note_md"], "see [contents](#contents)")
        self.assertIsNone(row["state"])
        rw = next(s for s in self.p.shapes if s["id"] == "shape-2a")["problems"][0]
        self.assertEqual(rw["state"], "write idx")
        self.assertEqual(rw["note_md"], "")

    def test_templates_blurb_worked(self):
        shapes = {s["id"]: s for s in self.p.shapes}
        self.assertEqual(self.p.pattern_template, "pattern_template = True")
        self.assertEqual(shapes["shape-1"]["template"], "shape_template = 1")
        self.assertEqual(shapes["shape-1"]["blurb"], "Alpha blurb.")
        self.assertEqual([w["id"] for w in shapes["shape-1"]["worked"]], [1])
        self.assertEqual([w["id"] for w in shapes["shape-2b"]["worked"]], [142])
        self.assertIsNone(shapes["shape-2a"]["template"])

    def test_pattern_id(self):
        self.assertEqual(self.p.pid, "fixture-pattern")
        self.assertEqual(bt.pattern_id("SlidingWindow"), "sliding-window")
        self.assertEqual(bt.pattern_id("DP2D"), "dp2-d")


class TestGrammarErrors(unittest.TestCase):
    def _errors(self, text):
        return parse_fixture(text).errors

    def test_unknown_column(self):
        errs = self._errors(FIXTURE.replace("| LC | Title | Diff | Freq | Note |",
                                            "| LC | Title | Diff | Freq | Company |", 1))
        self.assertTrue(any("unknown column" in e for e in errs), errs)

    def test_bad_freq(self):
        errs = self._errors(FIXTURE.replace("| 🔥🔥🔥 | the base case", "| 🔥🔥🔥🔥 | the base case"))
        self.assertTrue(any("Freq" in e and "LC 1" in e for e in errs), errs)

    def test_bad_diff_value(self):
        errs = self._errors(FIXTURE.replace("| 1 | Two Sum | Easy |", "| 1 | Two Sum | Hrd |"))
        self.assertTrue(any("bad Diff" in e for e in errs), errs)

    def test_diff_mismatch_is_a_warning(self):
        p = parse_fixture(FIXTURE.replace("| 1 | Two Sum | Easy |", "| 1 | Two Sum | Hard |"))
        self.assertEqual(p.errors, [])
        self.assertTrue(any("catalog says Easy" in w for w in p.warnings), p.warnings)

    def test_unknown_id(self):
        errs = self._errors(FIXTURE.replace("| 1 | Two Sum |", "| 999999 | Two Sum |"))
        self.assertTrue(any("not in the leetcode.com catalog" in e for e in errs), errs)

    def test_duplicate_id_within_tutorial(self):
        errs = self._errors(FIXTURE.replace("| 141 | Linked List Cycle | Easy |",
                                            "| 1 | Two Sum | Easy |"))
        self.assertTrue(any("already listed" in e for e in errs), errs)

    def test_unresolved_anchor(self):
        errs = self._errors(FIXTURE.replace("(#contents)", "(#nowhere)"))
        self.assertTrue(any("unresolved anchor #nowhere" in e for e in errs), errs)

    def test_table_outside_shape(self):
        bad = FIXTURE.replace("## Pitfalls", "## Pitfalls\n\n### Extra problems\n\n| LC | Title | Diff | Freq | Note |\n|---|---|---|---|---|\n| 2 | Add Two Numbers | Med | 🔥 | |\n")
        errs = self._errors(bad)
        self.assertTrue(any("outside any Shape" in e for e in errs), errs)

    def test_missing_required_section(self):
        errs = self._errors(FIXTURE.replace("## Drills", "## Exercises"))
        self.assertTrue(any("'## Drills'" in e for e in errs), errs)

    def test_parent_with_children_and_own_table(self):
        bad = FIXTURE.replace("Both pointers move left to right.",
                              "Both pointers move left to right.\n\n### Chasing problems\n\n| LC | Title | Diff | Freq | Note |\n|---|---|---|---|---|\n| 2 | Add Two Numbers | Med | 🔥 | |\n")
        errs = self._errors(bad)
        self.assertTrue(any("sub-shapes and its own problem table" in e for e in errs), errs)


class TestSlugRule(unittest.TestCase):
    def test_examples(self):
        self.assertEqual(bt.slugify("Shift, don't shrink (LC 424)"), "shift-dont-shrink-lc-424")
        self.assertEqual(bt.slugify("2a. Read and write"), "2a-read-and-write")
        self.assertEqual(bt.slugify("When sliding window breaks"), "when-sliding-window-breaks")
        self.assertEqual(bt.slugify("Merge Sorted Array (LC 88), backward"),
                         "merge-sorted-array-lc-88-backward")

    def test_duplicates_get_suffix(self):
        seen = set()
        self.assertEqual(bt.slugify("Template", seen), "template")
        self.assertEqual(bt.slugify("Template", seen), "template-1")
        self.assertEqual(bt.slugify("Template", seen), "template-2")


class TestCommittedTutorials(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(TUTORIALS_JSON.read_text(encoding="utf-8"))
        cls.problems = json.loads(PROBLEMS_JSON.read_text(encoding="utf-8"))["problems"]
        cls.patterns = json.loads(PATTERNS_JSON.read_text(encoding="utf-8"))

    def test_build_is_fresh(self):
        fresh = bt.build(strict=True, log=lambda *_: None)
        self.assertEqual(bt.dumps(fresh), TUTORIALS_JSON.read_text(encoding="utf-8"),
                         "data/tutorials.json is stale: run python3 scripts/build_tutorials.py")

    def test_every_tutorial_file_is_parsed(self):
        files = {p.name for p in bt.tutorial_files()}
        self.assertEqual(files, {t["file"] for t in self.data["tutorials"].values()})

    def test_every_table_id_resolves(self):
        by_id = {v["id"]: (slug, v) for slug, v in self.problems.items()}
        for pid, t in self.data["tutorials"].items():
            for s in t["shapes"]:
                for row in s["problems"]:
                    self.assertIn(row["id"], by_id, f"{pid}/{s['id']}: LC {row['id']} not in problems.json")
                    slug, p = by_id[row["id"]]
                    self.assertEqual(row["slug"], slug)
                    self.assertIn("tutorial", p["lists"], f"{slug} lacks a tutorial membership")
                    self.assertIn({"pattern": pid, "shape": s["id"]}, p["lists"]["tutorial"])

    def test_by_id_matches_shapes(self):
        seen = {}
        for pid, t in self.data["tutorials"].items():
            for s in t["shapes"]:
                for row in s["problems"]:
                    seen.setdefault(str(row["id"]), []).append({"tutorial": pid, "shape": s["id"]})
        self.assertEqual(self.data["by_id"], seen)

    def test_gifs_exist_and_are_small(self):
        for t in self.data["tutorials"].values():
            for g in t["gifs"]:
                path = ROOT / "tutorials" / g["src"]
                self.assertTrue(path.is_file(), g["src"])
                self.assertLessEqual(path.stat().st_size, bt.MAX_GIF_BYTES, g["src"])

    def test_anchors_resolve(self):
        for t in self.data["tutorials"].values():
            text = (ROOT / "tutorials" / t["file"]).read_text(encoding="utf-8")
            anchors = {h["anchor"] for h in t["headings"]}
            for m in bt.LINK_ANCHOR.finditer(text):
                self.assertIn(m.group("a"), anchors, f"{t['file']}: #{m.group('a')}")
            for s in t["shapes"]:
                self.assertIn(s["anchor"], anchors)
                for w in s["worked"]:
                    self.assertIn(w["anchor"], anchors)

    def test_no_duplicate_id_within_a_tutorial(self):
        for pid, t in self.data["tutorials"].items():
            ids = [r["id"] for s in t["shapes"] for r in s["problems"]]
            self.assertEqual(len(ids), len(set(ids)), pid)

    def test_tutorial_patterns_exist_and_carry_no_subtopics(self):
        for pid, t in self.data["tutorials"].items():
            self.assertIn(pid, self.patterns["patterns"], pid)
            p = self.patterns["patterns"][pid]
            self.assertEqual(p["tutorial"], t["file"])
            self.assertNotIn("subtopics", p, f"{pid}: the tutorial's shapes are its subtopics")
            if t["template"]:
                self.assertIsNone(p["template"], f"{pid}: template must come from the tutorial")
            else:
                self.assertTrue(p["template"], f"{pid}: no template anywhere")

    def test_readme_lists_every_tutorial(self):
        readme = (ROOT / "tutorials" / "README.md").read_text(encoding="utf-8")
        for t in self.data["tutorials"].values():
            self.assertIn(t["file"], readme)
        self.assertIn(bt.README_START, readme)
        self.assertEqual(bt.readme_table(self.data, self.patterns).strip(),
                         readme[readme.index(bt.README_START):
                                readme.index(bt.README_END) + len(bt.README_END)].strip(),
                         "tutorials/README.md status table is stale: "
                         "run python3 scripts/build_tutorials.py --readme-table")


if __name__ == "__main__":
    unittest.main()
