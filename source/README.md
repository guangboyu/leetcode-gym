# Source data — LeetCode study lists

Scraped problem lists that feed the study tracker. Snapshot date: **2026-06-09**.

## Lists

| List | Human-readable | Machine-readable | Count | Source |
|------|----------------|------------------|-------|--------|
| **LeetCode Hot 100** | [Hot100.md](Hot100.md) | [data/hot100.json](data/hot100.json) | 100 | [leetcode.com/studyplan/top-100-liked](https://leetcode.com/studyplan/top-100-liked/) |
| **LeetCode Top Interview 150** | [Leetcode150.md](Leetcode150.md) | [data/interview150.json](data/interview150.json) | 150 | [leetcode.com/studyplan/top-interview-150](https://leetcode.com/studyplan/top-interview-150/) |
| **NeetCode 250** | [Neetcode250.md](Neetcode250.md) | [data/neetcode250.json](data/neetcode250.json) | 250 | [neetcode.io/practice](https://neetcode.io/practice) |
| **灵茶山艾府 (0x3F)** | [ox3F/](ox3F/) (12 English topic lists + [README](ox3F/README.md)) | [data/ox3f.json](data/ox3f.json) | 2,723 unique (2,346 after interview curation) | [leetcode.cn discuss 3141566](https://leetcode.cn/discuss/post/3141566/) |

Supporting data:

- [data/catalog.json](data/catalog.json) — every leetcode.com problem (3,958): slug → id,
  English title, difficulty, premium flag, and contest rating where one exists (2,501 problems,
  from the [zerotrac rating project](https://zerotrac.github.io/leetcode_problem_rating/)).

## Data sources & methods

- **Hot 100 / Interview 150** — pulled from LeetCode's official GraphQL API
  (`studyPlanV2Detail`, POST https://leetcode.com/graphql, no auth; planSlugs `top-100-liked`
  and `top-interview-150`). The `data/*.json` files are the raw API responses (grouped by
  topic; each problem has `questionFrontendId`, `title`, `titleSlug`, `difficulty`).
  The `.md` files are generated tables.
- **NeetCode 250** — the canonical 250 (= NeetCode 150 + 100 more), from the curated dataset
  [ascherj/neetcode-250-guide](https://github.com/ascherj/neetcode-250-guide)
  (`neetcode_250_complete.json`). Each problem has `name`, `difficulty`, `category`,
  `leetcode_url`, `slug`. ⚠ The `slug` field is the **NeetCode site slug**, which differs from
  the LeetCode slug for 74 of 250 problems — always derive the canonical slug from
  `leetcode_url`. (NeetCode's own `.problemSiteData.json` lists ~420 problems — the full site
  catalog, not the 250 roadmap — so the curated dataset is used instead.)
- **0x3F** — 12 leetcode.cn discuss posts, scraped from each page's embedded `__NEXT_DATA__`
  JSON (original Chinese markdown preserved under [ox3F/raw-zh/](ox3F/raw-zh/)), parsed into
  [data/ox3f.json](data/ox3f.json), and rendered as curated English lists.
  See [ox3F/README.md](ox3F/README.md) for the pipeline and curation rules.

## Notes for the tracker

- **Canonical ID = leetcode.com problem slug** (e.g. `two-sum`). `leetcode.com` and
  `leetcode.cn` share slugs. The lists overlap heavily (Hot 100 ∩ Interview 150;
  NeetCode 150 ⊂ 250; 0x3F covers most of all three) — model problems as one table with
  list-membership tags, not four disjoint sets. The merged table is built by
  `scripts/build_problems.py` → [`../data/problems.json`](../data/problems.json).
- **Difficulty granularity differs.** LeetCode/NeetCode give Easy/Medium/Hard only; contest
  ratings in `catalog.json` are much finer-grained (~1000–3000+) — useful for ordering reviews.

## Regenerating (from the repo root; needs python3, no extra deps)

```bash
python3 scripts/fetch_catalog.py     # refresh data/catalog.json (titles + ratings)
python3 scripts/gen_lists.py         # data/*.json -> Hot100.md, Leetcode150.md, Neetcode250.md
python3 scripts/parse_0x3f.py        # ox3F/raw-zh/*.md -> data/ox3f.json
python3 scripts/gen_0x3f_md.py       # data/ox3f.json + catalog -> ox3F/*.md (English)
python3 scripts/build_problems.py    # everything -> ../data/problems.json
```

Refreshing the raw inputs themselves (LeetCode GraphQL, the ascherj dataset, the 0x3F posts —
all actively maintained upstream) is documented above and in [ox3F/README.md](ox3F/README.md).

## Attribution / licensing notes

This directory redistributes only **factual list data** (problem IDs, titles, slugs, list
membership, ratings); problem statements and authors' explanatory content are not included.

- 0x3F lists: curation by [灵茶山艾府 / EndlessCheng](https://github.com/EndlessCheng) — see
  [ox3F/README.md](ox3F/README.md).
- NeetCode 250 selection: [neetcode.io](https://neetcode.io); dataset via
  [ascherj/neetcode-250-guide](https://github.com/ascherj/neetcode-250-guide) (no license file —
  treated as factual data with attribution).
- Contest ratings: [zerotrac/leetcode_problem_rating](https://zerotrac.github.io/leetcode_problem_rating/).
- Hot 100 / Top Interview 150 grouping: LeetCode study plans.
