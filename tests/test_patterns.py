"""Invariants of data/patterns.json (the unified pattern taxonomy) against
data/problems.json and data/tutorials.json.

The old rule was "every core problem belongs to exactly one subtopic". Tutorials
legitimately list the same problem under two patterns (LC 42 is two pointers AND
prefix maxima), so the rule is now COVERAGE: every problem in the Hot 100 /
Interview 150 / NeetCode 250 union has a home in some subtopic or tutorial table.
"""
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import _patternof  # noqa: E402
from draft_patterns import resolve, sec_key  # noqa: E402

DATA = ROOT / "data"


def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


class TestPatterns(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pat = load("patterns.json")
        cls.problems = load("problems.json")["problems"]
        cls.tut = load("tutorials.json")
        cls.by_id = {v["id"]: k for k, v in cls.problems.items()}
        cls.subtopic_ids = {}
        for pid, p in cls.pat["patterns"].items():
            ids = [s["id"] for s in p.get("subtopics", [])]
            if pid in cls.tut["tutorials"]:
                ids += [s["id"] for s in cls.tut["tutorials"][pid]["shapes"]]
            cls.subtopic_ids[pid] = ids

    # ---- shape ---------------------------------------------------------
    def test_order_matches_patterns(self):
        self.assertEqual(sorted(self.pat["order"]), sorted(self.pat["patterns"]))
        self.assertEqual(len(self.pat["order"]), len(set(self.pat["order"])))

    def test_every_pattern_has_guide_content(self):
        for pid, p in self.pat["patterns"].items():
            self.assertTrue(p["name"], pid)
            self.assertGreaterEqual(len(p["signals"]), 2, pid)
            self.assertTrue(p["one_liner"], pid)
            has_tutorial_template = bool(self.tut["tutorials"].get(pid, {}).get("template"))
            self.assertTrue(p["template"] or has_tutorial_template, f"{pid}: no template source")
            if p["template"]:
                self.assertIsInstance(p["template"], list)
            self.assertIsInstance(p["legacy_patternOf"], list)

    def test_subtopics_well_formed(self):
        for pid, p in self.pat["patterns"].items():
            subs = p.get("subtopics", [])
            ids = [s["id"] for s in subs]
            self.assertEqual(len(ids), len(set(ids)), pid)
            all_ids = []
            for s in subs:
                self.assertRegex(s["id"], r"^[a-z0-9]+(-[a-z0-9]+)*$", f"{pid}/{s['id']}")
                self.assertTrue(s["name"] and s["recognize"] and s["solve"], f"{pid}/{s['id']}")
                self.assertNotRegex(s["name"], r"^\d+\.", f"{pid}/{s['id']}: numbered name")
                if "template" in s:
                    self.assertIsInstance(s["template"], list)
                all_ids += s["core_ids"]
                for i in s["core_ids"]:
                    self.assertIn(i, self.by_id, f"{pid}/{s['id']}: LC {i} not in problems.json")
            self.assertEqual(len(all_ids), len(set(all_ids)), f"{pid}: id in two subtopics")

    def test_tutorial_patterns(self):
        for pid, p in self.pat["patterns"].items():
            if p["tutorial"]:
                self.assertTrue((ROOT / "tutorials" / p["tutorial"]).is_file(), p["tutorial"])
                self.assertIn(pid, self.tut["tutorials"])
                self.assertNotIn("subtopics", p, pid)
            else:
                self.assertIn("subtopics", p, pid)
                self.assertNotIn(pid, self.tut["tutorials"])

    # ---- legacy patternOf mirror ----------------------------------------
    def test_patternof_dicts_match_route_js(self):
        js = (ROOT / "tracker" / "static" / "route.js").read_text(encoding="utf-8")

        def js_dict(name):
            m = re.search(r"const %s = \{(.*?)\};" % name, js, re.S)
            self.assertIsNotNone(m, name)
            body = re.sub(r"//[^\n]*", "", m.group(1))
            pairs = re.findall(r'(?:"([^"]+)"|(\d+)):\s*"([^"]+)"', body)
            return {(k or int(n)): v for k, n, v in pairs}

        self.assertEqual(js_dict("NC_PATTERN"), _patternof.NC_PATTERN)
        self.assertEqual(js_dict("H1_PATTERN"), _patternof.H1_PATTERN)
        self.assertEqual(js_dict("I150_PATTERN"), _patternof.I150_PATTERN)
        self.assertEqual(js_dict("PATTERN_OVERRIDES"), _patternof.PATTERN_OVERRIDES)

    def test_legacy_patternof_names_are_known(self):
        known = set(_patternof.NC_PATTERN.values()) | set(_patternof.H1_PATTERN.values()) \
            | set(_patternof.I150_PATTERN.values()) | set(_patternof.PATTERN_OVERRIDES.values())
        claimed = [n for p in self.pat["patterns"].values() for n in p["legacy_patternOf"]]
        self.assertEqual(sorted(claimed), sorted(known))     # each legacy stage owned once

    # ---- coverage: replaces the old partition invariant ------------------
    def test_every_core_problem_has_a_home(self):
        covered = set()
        for p in self.pat["patterns"].values():
            for s in p.get("subtopics", []):
                covered.update(s["core_ids"])
            # tutorial patterns: ids the tutorial does not list still show up in
            # the app's "Also core, not in the tutorial" group
            covered.update(p.get("legacy_core_ids", []))
        covered.update(int(i) for i in self.tut["by_id"])
        missing = []
        for slug, p in self.problems.items():
            if p["paid_only"] or _patternof.pattern_of(p) is None:
                continue
            if p["id"] not in covered:
                missing.append((p["id"], slug, _patternof.pattern_of(p)))
        self.assertEqual(missing, [], "core problems without a subtopic or tutorial table")

    def test_core_ids_are_core_problems(self):
        for pid, p in self.pat["patterns"].items():
            for s in p.get("subtopics", []):
                for i in s["core_ids"]:
                    prob = self.problems[self.by_id[i]]
                    self.assertIsNotNone(_patternof.pattern_of(prob),
                                         f"{pid}/{s['id']}: LC {i} is not in the core union")

    # ---- 0x3F mapping ----------------------------------------------------
    def _target_ok(self, target):
        pid, _, sid = target.partition("/")
        if pid not in self.pat["patterns"]:
            return False
        return not sid or sid in self.subtopic_ids[pid]

    def test_mapping_targets_resolve(self):
        ox = self.pat["ox3f"]
        for topic, t in ox["topics"].items():
            self.assertTrue(self._target_ok(t["default"]), f"{topic}: default {t['default']}")
            self.assertTrue(t["post"].startswith("https://"), topic)
            self.assertTrue(t["zh"], topic)
        for topic, chaps in ox["chapters"].items():
            self.assertIn(topic, ox["topics"])
            for c, target in chaps.items():
                self.assertRegex(c, r"^\d+$", f"{topic}||{c}")
                self.assertTrue(self._target_ok(target), f"{topic}||{c} -> {target}")
        for key, target in ox["sections"].items():
            topic = key.split("||", 1)[0]
            self.assertIn(topic, ox["topics"], key)
            self.assertTrue(self._target_ok(target), f"{key} -> {target}")

    def test_mapping_keys_exist_in_data(self):
        present = set()
        for p in self.problems.values():
            for m in p["lists"].get("ox3f", []):
                if m["tier"] == "interview":
                    present.add((m["topic"], sec_key(m["section"])))
        chapters = {(t, k.split(".")[0]) for t, k in present}
        ox = self.pat["ox3f"]
        for key in ox["sections"]:
            topic, sec = key.split("||", 1)
            self.assertIn((topic, sec), present, f"unknown section key {key}")
        for topic, chaps in ox["chapters"].items():
            for c in chaps:
                self.assertIn((topic, c), chapters, f"unknown chapter {topic}||{c}")
        for key in ox["hidden"]:
            topic, sec = key.split("||", 1)
            self.assertIn((topic, sec), present, f"unknown hidden key {key}")

    def test_every_interview_section_resolves(self):
        ox = self.pat["ox3f"]
        topics = {m["topic"] for p in self.problems.values()
                  for m in p["lists"].get("ox3f", []) if m["tier"] == "interview"}
        self.assertEqual(topics, set(ox["topics"]))
        via_default = set()
        for p in self.problems.values():
            for m in p["lists"].get("ox3f", []):
                if m["tier"] != "interview":
                    continue
                target, how = resolve(self.pat, m["topic"], m["section"])
                self.assertTrue(self._target_ok(target), f"{m} -> {target}")
                if how == "default":
                    via_default.add(f"{m['topic']}||{sec_key(m['section'])}")
        # Only hidden sections may fall through to the topic default.
        self.assertTrue(via_default <= set(ox["hidden"]),
                        f"sections mapped only by topic default: {sorted(via_default - set(ox['hidden']))}")


if __name__ == "__main__":
    unittest.main()
