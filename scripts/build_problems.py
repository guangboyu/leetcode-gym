#!/usr/bin/env python3
"""Merge all four source lists into the normalized tracker input data/problems.json.

One entry per problem, keyed by leetcode.com slug (canonical ID; leetcode.cn shares it).
Each entry carries metadata from source/data/catalog.json plus which lists it belongs to:

  "two-sum": {
    "id": 1, "title": "Two Sum", "difficulty": "Easy", "rating": null, "paid_only": false,
    "lists": {
      "hot100": {"group": "Hash Table"},
      "interview150": {"group": "Hashmap"},
      "neetcode250": {"category": "Arrays & Hashing"},
      "ox3f": [{"topic": "Data Structures", "section": "§0.1.1 Basics", "tier": "interview"}],
      "tutorial": [{"pattern": "sliding-window", "shape": "shape-1"}]
    }
  }

Notes:
  - neetcode250.json's `slug` field is the NeetCode site slug, NOT the LeetCode slug
    (differs for 74/250 problems) — the canonical slug is taken from `leetcode_url`.
  - ox3F problems exclusive to leetcode.cn (LCP/LCR/LCS/面试题 series, no .com slug)
    are excluded; they remain available in source/data/ox3f.json.
  - ox3f memberships carry the section tier (interview|competition) so the tracker
    can filter competition-only material.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "source"
OUT = ROOT / "data" / "problems.json"
TUTORIALS = ROOT / "data" / "tutorials.json"


def load(p):
    return json.loads(p.read_text(encoding="utf-8"))


def build():
    """Return {"snapshot", "problems"} (what data/problems.json holds) plus a stats dict."""
    catalog = load(SRC / "data" / "catalog.json")
    by_id = {v["id"]: k for k, v in catalog.items()}
    problems = {}

    def entry(slug):
        if slug not in catalog:
            raise KeyError(f"slug not in leetcode.com catalog: {slug}")
        if slug not in problems:
            c = catalog[slug]
            problems[slug] = {
                "id": c["id"], "title": c["title"], "difficulty": c["difficulty"],
                "rating": c["rating"], "paid_only": c["paid_only"], "lists": {},
            }
        return problems[slug]

    # Hot 100 / Interview 150 (LeetCode study plans)
    for fname, key in (("hot100.json", "hot100"), ("interview150.json", "interview150")):
        plan = load(SRC / "data" / fname)["data"]["studyPlanV2Detail"]
        for g in plan["planSubGroups"]:
            for q in g["questions"]:
                entry(q["titleSlug"])["lists"][key] = {"group": g["name"]}

    # NeetCode 250 — canonical slug comes from leetcode_url, not the `slug` field
    for p in load(SRC / "data" / "neetcode250.json")["problems"]:
        slug = p["leetcode_url"].rstrip("/").rsplit("/", 1)[-1]
        entry(slug)["lists"]["neetcode250"] = {"category": p["category"]}

    # 0x3F topic lists
    ox = load(SRC / "data" / "ox3f.json")
    meta = load(SRC / "ox3F" / "sections-meta.json")
    cn_only = 0
    for topic in ox["topics"]:
        m = meta[topic["file"]]
        for sec in topic["sections"]:
            tier = "competition" if any(m[h].get("tier") == "competition" for h in sec["path"]) else "interview"
            section_en = m[sec["path"][-1]]["en"]
            for p in sec["problems"]:
                if p["slug"] not in catalog:
                    cn_only += 1
                    continue
                memberships = entry(p["slug"])["lists"].setdefault("ox3f", [])
                rec = {"topic": topic["en"], "section": section_en, "tier": tier}
                if rec not in memberships:
                    memberships.append(rec)

    # Tutorial tables (data/tutorials.json). Problems outside the four lists are
    # pulled in from the catalog so they can be tracked.
    added = []
    if TUTORIALS.exists():
        for pid, refs in load(TUTORIALS)["by_id"].items():
            slug = by_id[int(pid)]
            if slug not in problems:
                added.append(slug)
            entry(slug)["lists"]["tutorial"] = [{"pattern": r["tutorial"], "shape": r["shape"]}
                                                for r in refs]

    problems = dict(sorted(problems.items(), key=lambda kv: kv[1]["id"]))
    return {"snapshot": ox["snapshot"], "problems": problems}, {"cn_only": cn_only, "added": added}


def main():
    data, stats = build()
    problems = data["problems"]
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    in_list = lambda key: sum(1 for v in problems.values() if key in v["lists"])
    ox_interview = sum(1 for v in problems.values()
                       if any(r["tier"] == "interview" for r in v["lists"].get("ox3f", [])))
    print(f"Wrote {OUT}")
    print(f"  total problems:   {len(problems)}")
    print(f"  hot100:           {in_list('hot100')}")
    print(f"  interview150:     {in_list('interview150')}")
    print(f"  neetcode250:      {in_list('neetcode250')}")
    print(f"  ox3f:             {in_list('ox3f')}  (interview-tier: {ox_interview})")
    print(f"  tutorial:         {in_list('tutorial')}  (added from catalog: {stats['added']})")
    print(f"  cn-only excluded: {stats['cn_only']} entries")


if __name__ == "__main__":
    main()
