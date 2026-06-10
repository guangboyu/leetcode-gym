# 灵茶山艾府 (0x3F / EndlessCheng) — Curated Problem Lists

Curated **English** editions of the problem lists by **灵茶山艾府 (0x3F)**, organized for
interview preparation. Master post "如何科学刷题" (How to practice algorithms scientifically):
https://leetcode.cn/discuss/post/3141566/

## Files

| # | English list | Topic | Problems kept |
|---|--------------|-------|---------------|
| 1 | [01-sliding-window-two-pointers.md](01-sliding-window-two-pointers.md) | Sliding Window & Two Pointers | 259 |
| 2 | [02-binary-search.md](02-binary-search.md) | Binary Search | 130 |
| 3 | [03-monotonic-stack.md](03-monotonic-stack.md) | Monotonic Stack | 62 |
| 4 | [04-grid-graph.md](04-grid-graph.md) | Grid Graph | 58 |
| 5 | [05-bit-manipulation.md](05-bit-manipulation.md) | Bit Manipulation | 104 |
| 6 | [06-graph-theory.md](06-graph-theory.md) | Graph Theory | 132 |
| 7 | [07-dynamic-programming.md](07-dynamic-programming.md) | Dynamic Programming | 474 |
| 8 | [08-data-structures.md](08-data-structures.md) | Data Structures | 514 |
| 9 | [09-math.md](09-math.md) | Math | 120 |
| 10 | [10-greedy-thinking.md](10-greedy-thinking.md) | Greedy & Thinking | 456 |
| 11 | [11-linkedlist-tree-backtracking.md](11-linkedlist-tree-backtracking.md) | Linked List, Tree & Backtracking | 370 |
| 12 | [12-strings.md](12-strings.md) | Strings | 35 |

**2,346 unique problems** across all 12 lists (a problem can appear in several topics).
Snapshot date: **2026-06-09** — the original lists are actively maintained and change over time.

- [`raw-zh/`](raw-zh/) — the original Chinese markdown of each list as scraped from leetcode.cn
  (12 topic posts + [`syllabus.md`](raw-zh/syllabus.md), 0x3F's study-methodology article).
  These are the unmodified upstream snapshots; everything else is derived from them.
- [`sections-meta.json`](sections-meta.json) — hand-curated map: Chinese section header →
  English name + tier (`interview` / `competition`).

## Curation rules

The English lists keep 0x3F's section structure and recommended problem order
("螺旋上升式学习" — within each section, lower-rated problems come first), but:

- **Competition-only sections are omitted** (tagged `tier: competition` in
  `sections-meta.json`): network flow, suffix automata, persistent segment trees, digit DP,
  rerooting DP, computational geometry, generating functions, etc. Each list ends with an
  "Omitted from this list" inventory. The full data, including these sections, is in
  [`../data/ox3f.json`](../data/ox3f.json).
- **leetcode.cn-exclusive problems are omitted** (LCP / LCR / LCS / 面试题 series — no
  leetcode.com equivalent; 89 problems total).
- **Premium problems are kept**, marked 🔒.
- **Difficulty ratings** (难度分, ~1000–3000+) come from the
  [zerotrac rating project](https://zerotrac.github.io/leetcode_problem_rating/), joined by
  problem slug; problems that never appeared in a rated contest have none.

## Re-fetching / regenerating

```bash
# 1. refresh a raw Chinese snapshot (the post body is embedded in the page's __NEXT_DATA__ JSON;
#    circle/discuss/<id> URLs 308-redirect to /discuss/post/<id>/):
curl -sL "https://leetcode.cn/discuss/post/SqopEo/" -o post.html
python3 scripts/extract_0x3f.py post.html source/ox3F/raw-zh/02-binary-search.md

# 2. re-parse, refresh titles/ratings, regenerate the English lists (from the repo root):
python3 scripts/parse_0x3f.py
python3 scripts/fetch_catalog.py
python3 scripts/gen_0x3f_md.py
```

Post URLs per topic are listed in each English file's header and in `scripts/parse_0x3f.py`.
If a refreshed list adds new section headers, `gen_0x3f_md.py` will fail until they are added
to `sections-meta.json` (translate + classify them).

## Attribution

The problem selection, ordering, and section structure are the work of
**灵茶山艾府 (0x3F / [EndlessCheng](https://github.com/EndlessCheng))**, published on
leetcode.cn. This repo stores only the factual list structure (problem IDs, slugs, section
grouping) plus unmodified snapshots of the source posts for reproducibility; his explanatory
prose, solutions, and videos are not reproduced — see the original posts for those.
Difficulty ratings are by [zerotrac](https://zerotrac.github.io/leetcode_problem_rating/).
