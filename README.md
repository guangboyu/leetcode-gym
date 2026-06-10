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
- Solved it only after reading the editorial? Mark **w/ help** — it comes back in 2 days
  and the interval ladder doesn't climb.
- Couldn't solve it at review time? Mark **Forgot** — it becomes due immediately and the
  interval ladder restarts on your next solve.

## Practice methodology (after 0x3F's "how to practice scientifically")

- **Today** tab: reviews due now, then the **study route** — 0x3F's 7-stage beginner path
  (sliding window → binary search → core data structures → binary tree DFS → grid DFS →
  backtracking → DP ch. 1–6) suggesting the next problems in his recommended order.
- **Rating cap** (header, default **1700**): spiral learning — finish everything at or
  below the cap before raising it. The DP stage automatically widens to 2000.
- **Drill** tab: random already-unseen problem in a rating range with its topic and
  difficulty hidden until you mark it — trains recognizing problem types cold.
- **Browse**: filter by list, 0x3F topic, difficulty, status, ≤cap; search; sort by rating.
- **Stats**: per-list progress (incl. within-cap %) and the data-range → complexity table.

## Storage

Every action is appended to `data/reviews.jsonl` (the source of truth — append-only, so
it's crash-proof and merges trivially across machines via git); `data/progress.json` is a
derived snapshot rebuilt on server start. Run with `--autocommit` to git-commit your
progress automatically a minute after each study burst and on shutdown (it never pushes).

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
