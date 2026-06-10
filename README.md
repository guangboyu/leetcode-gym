# LeetCode Study Tracker

A local, dependency-free study tracker for LeetCode interview prep. It merges four curated
problem lists into one table (2,676 problems), lets you mark each problem
**Solved / Forgot / Reset**, and schedules reviews on an **Ebbinghaus forgetting curve**.

## Quick start

```bash
python3 tracker/server.py        # then open http://localhost:8765
```

Requires only python3 (stdlib) on Linux/macOS. Your progress is saved to
`data/progress.json` — a plain JSON file you can commit to keep it safe across machines.

## How reviewing works

- Mark a problem **Solved** each time you solve it (first time or on review). Reviews are
  scheduled at growing intervals: **1 → 2 → 4 → 7 → 15 → 30 days**.
- Clear all six intervals and the problem is **Mastered** (no more reviews).
- Couldn't solve it at review time? Mark **Forgot** — it becomes due immediately and the
  interval ladder restarts on your next solve.
- The **Due** tab is your daily queue; **Browse** filters by list, 0x3F topic, difficulty,
  status, or contest rating; **Stats** shows per-list progress.

## The lists

| List | Problems | Notes |
|------|----------|-------|
| [LeetCode Hot 100](source/Hot100.md) | 100 | official study plan |
| [LeetCode Top Interview 150](source/Leetcode150.md) | 150 | official study plan |
| [NeetCode 250](source/Neetcode250.md) | 250 | NeetCode 150 + 100 more |
| [灵茶山艾府 (0x3F)](source/ox3F/) | 2,346 curated | 12 topic lists, translated to English, competition-only sections omitted |

Problems are keyed by leetcode.com slug and tagged with the lists they belong to — the lists
overlap heavily, so a single review counts for all of them. Most problems carry a numeric
contest difficulty rating (~1000–3000+) for fine-grained ordering.

Sources, scraping/curation pipeline, and refresh instructions: [source/README.md](source/README.md).
Attribution: lists by [LeetCode](https://leetcode.com), [NeetCode](https://neetcode.io), and
[灵茶山艾府 / EndlessCheng](https://github.com/EndlessCheng); ratings by
[zerotrac](https://zerotrac.github.io/leetcode_problem_rating/). This repo redistributes
factual list data only (IDs, titles, slugs, grouping) — no problem statements or solutions.

## License

The code in this repo (tracker, scripts) is [MIT](LICENSE). The problem-list data remains
the work of its upstream curators (see attribution above) and is redistributed here as
factual data with attribution, not under the MIT grant.

## Development

```bash
python3 -m unittest discover -s tests   # scheduler tests
```

Data pipeline (rebuild everything from the raw snapshots): see
[source/README.md](source/README.md#regenerating-from-the-repo-root-needs-python3-no-extra-deps).
