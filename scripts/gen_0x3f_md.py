#!/usr/bin/env python3
"""Generate the curated English 0x3F topic lists (source/ox3F/*.md) from:

  source/data/ox3f.json          parsed section structure (scripts/parse_0x3f.py)
  source/data/catalog.json       English titles / difficulty / ratings (scripts/fetch_catalog.py)
  source/ox3F/sections-meta.json hand-curated English section names + tier

Curation rules (interview prep focus):
  - sections tagged tier="competition" are omitted (listed at the bottom of each file)
  - problems that don't exist on leetcode.com (LCP/LCR/LCS/面试题 series) are omitted
  - premium problems are kept, marked with 🔒
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "source"
OX = SRC / "ox3F"


def main():
    ox = json.loads((SRC / "data" / "ox3f.json").read_text(encoding="utf-8"))
    catalog = json.loads((SRC / "data" / "catalog.json").read_text(encoding="utf-8"))
    meta = json.loads((OX / "sections-meta.json").read_text(encoding="utf-8"))

    grand_kept = set()
    summary = []
    for topic in ox["topics"]:
        m = meta[topic["file"]]
        lines = [
            f"# {topic['en']} — 0x3F list",
            "",
            f"> Curated from 灵茶山艾府 (0x3F)'s problem list: [{topic['post']}]({topic['post']}) "
            f"(snapshot {ox['snapshot']}). Section structure and problem order follow the original.",
            "> Competition-only sections and leetcode.cn-exclusive problems are omitted (see the end of this file).",
            "> **Rating** = LeetCode contest difficulty rating (~1000–3000+) from the "
            "[zerotrac project](https://zerotrac.github.io/leetcode_problem_rating/); 🔒 = premium.",
            "",
        ]
        kept_slugs, cn_skipped = set(), set()
        omitted = []          # competition sections (en names, with counts)
        emitted_headers = []  # path components already printed
        n = 0

        for sec in topic["sections"]:
            if any(m[h].get("tier") == "competition" for h in sec["path"]):
                top = next(h for h in sec["path"] if m[h].get("tier") == "competition")
                if not omitted or omitted[-1][0] != m[top]["en"]:
                    omitted.append([m[top]["en"], 0])
                omitted[-1][1] += len(sec["problems"])
                continue

            rows = []
            for p in sec["problems"]:
                c = catalog.get(p["slug"])
                if c is None:
                    cn_skipped.add(p["slug"])
                    continue
                n += 1
                kept_slugs.add(p["slug"])
                lock = " 🔒" if (c["paid_only"] or p["premium"]) else ""
                rating = c["rating"] if c["rating"] is not None else ""
                url = f"https://leetcode.com/problems/{p['slug']}/"
                rows.append(f"| {n} | {c['id']} | [{c['title']}]({url}){lock} | {c['difficulty']} | {rating} |")
            if not rows:
                continue

            for i, h in enumerate(sec["path"]):
                if emitted_headers[: i + 1] != sec["path"][: i + 1]:
                    emitted_headers = sec["path"][: i + 1]
                    lines += ["#" * (i + 2) + " " + m[h]["en"], ""]
            lines += ["| # | ID | Problem | Difficulty | Rating |",
                      "|---|----|---------|------------|--------|"]
            lines += rows
            lines.append("")

        if omitted or cn_skipped:
            lines += ["---", "", "## Omitted from this list", ""]
            if omitted:
                lines.append("Competition-oriented sections (see the original post or "
                             "`source/data/ox3f.json` for their problems):")
                lines.append("")
                lines += [f"- {name} ({cnt} problem{'s' if cnt != 1 else ''})" for name, cnt in omitted]
                lines.append("")
            if cn_skipped:
                lines.append(f"Also omitted: {len(cn_skipped)} problems exclusive to leetcode.cn "
                             "(LCP / LCR / LCS / 面试题 series).")
                lines.append("")

        out = OX / f"{topic['file']}.md"
        out.write_text("\n".join(lines), encoding="utf-8")
        grand_kept |= kept_slugs
        n_omitted = sum(c for _, c in omitted)
        summary.append((topic["file"], topic["en"], len(kept_slugs), n_omitted, len(cn_skipped)))
        print(f"{topic['file']}: kept {len(kept_slugs)} unique, omitted {n_omitted} competition entries, "
              f"{len(cn_skipped)} cn-only")

    print(f"\nTotal unique problems kept across topics: {len(grand_kept)}")
    return summary


if __name__ == "__main__":
    main()
