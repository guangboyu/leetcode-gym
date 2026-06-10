#!/usr/bin/env python3
"""Regenerate the three western list markdown files from source/data/*.json:

  source/Hot100.md        <- source/data/hot100.json
  source/Leetcode150.md   <- source/data/interview150.json
  source/Neetcode250.md   <- source/data/neetcode250.json
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "source"
SNAPSHOT_DATE = "2026-06-09"


def write_md(path: Path, lines):
    path.write_text("\n".join(lines), encoding="utf-8")


def build_study_plan(raw_path: Path, out_path: Path, heading: str, source_url: str):
    d = json.loads(raw_path.read_text(encoding="utf-8"))["data"]["studyPlanV2Detail"]
    groups = d["planSubGroups"]
    total = sum(len(g["questions"]) for g in groups)
    lines = [
        f"# {heading}",
        "",
        f"> Source: [{source_url}]({source_url}) - fetched via LeetCode GraphQL API on {SNAPSHOT_DATE}.",
        f"> Total: **{total}** problems across **{len(groups)}** topic groups.",
        "",
    ]
    n = 0
    for g in groups:
        lines += [
            f"## {g['name']} ({len(g['questions'])})",
            "",
            "| # | ID | Problem | Difficulty | Link |",
            "|---|----|---------|------------|------|",
        ]
        for q in g["questions"]:
            n += 1
            url = f"https://leetcode.com/problems/{q['titleSlug']}/"
            lines.append(
                f"| {n} | {q['questionFrontendId']} | {q['title']} | {q['difficulty']} | [link]({url}) |"
            )
        lines.append("")
    write_md(out_path, lines)
    print(f"Wrote {out_path}  ({total} problems)")


def build_neetcode250():
    problems = json.loads((SRC / "data" / "neetcode250.json").read_text(encoding="utf-8"))["problems"]
    lines = [
        "# NeetCode 250",
        "",
        "> Source: [neetcode.io/practice](https://neetcode.io/practice) (list=neetcode250), "
        "via dataset [ascherj/neetcode-250-guide](https://github.com/ascherj/neetcode-250-guide) "
        f"- fetched {SNAPSHOT_DATE}.",
        f"> Total: **{len(problems)}** problems. NeetCode 250 = NeetCode 150 + 100 additional problems.",
        "",
    ]
    categories = list(dict.fromkeys(p["category"] for p in problems))
    n = 0
    for c in categories:
        items = [p for p in problems if p["category"] == c]
        lines += [
            f"## {c} ({len(items)})",
            "",
            "| # | Problem | Difficulty | LeetCode |",
            "|---|---------|------------|----------|",
        ]
        for p in items:
            n += 1
            lines.append(f"| {n} | {p['name']} | {p['difficulty']} | [link]({p['leetcode_url']}) |")
        lines.append("")
    write_md(SRC / "Neetcode250.md", lines)
    print(f"Wrote {SRC / 'Neetcode250.md'}  ({len(problems)} problems)")


if __name__ == "__main__":
    build_study_plan(
        SRC / "data" / "hot100.json", SRC / "Hot100.md",
        "LeetCode Hot 100 (Top 100 Liked)", "https://leetcode.com/studyplan/top-100-liked/",
    )
    build_study_plan(
        SRC / "data" / "interview150.json", SRC / "Leetcode150.md",
        "LeetCode Top Interview 150", "https://leetcode.com/studyplan/top-interview-150/",
    )
    build_neetcode250()
