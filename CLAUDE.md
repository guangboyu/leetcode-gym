# LeetCode Study Tracker

A study tracker that pulls problems from four curated LeetCode lists, lets you mark each
problem **Solved / Unsolved / Forgotten**, and schedules spaced-repetition reviews using an
**Ebbinghaus forgetting curve**.

## Status

- **Phase 1 — scrape source lists: DONE** (snapshot 2026-06-09). All four lists are under `source/`.
- **Phase 2 — build the tracker: NOT STARTED.** Next step: merge all sources into one
  normalized `problems.json` keyed by problem slug, then build the status + review-scheduler UI.

## Cross-platform note

Phase 1 was done on **Windows** (this machine has **no python/node/jq** — only PowerShell and git),
which is why the helper scripts are `.ps1`. The repo is being moved to a **Linux** machine for
Phase 2, where python3 / node / jq are available. **On Linux, ignore the `.ps1` scripts** — re-implement
data processing in python or node. The scraped data in `source/` is platform-neutral and ready to use.

## Repository layout

```
source/
  README.md            # map of all four lists + data-source details
  Hot100.md            # LeetCode Hot 100 (100)        human-readable table
  Leetcode150.md       # LeetCode Top Interview 150 (150)
  Neetcode250.md       # NeetCode 250 (250)
  data/                # machine-readable JSON — the real tracker input
    hot100.json        #   raw LeetCode GraphQL response (grouped by topic)
    interview150.json  #   raw LeetCode GraphQL response
    neetcode250.json   #   curated 250 dataset ({problems:[{name,difficulty,category,leetcode_url,slug}]})
  ox3F/                # 灵茶山艾府 (0x3F) curated lists — 2,702 unique problems
    README.md          #   index of the 12 topic files + source URLs + counts
    syllabus.md        #   his "how to study" methodology article (no problem links)
    01-...12-*.md      #   12 topic lists; markdown with problem links + 难度分 ratings inline
    _extract.ps1       #   (Windows-only) re-scraper for 0x3F posts
  _gen_lists.ps1       # (Windows-only) regenerates the 3 western .md files from data/*.json
```

## Data sources (for refreshing)

| List | Source | Notes |
|------|--------|-------|
| Hot 100 | LeetCode GraphQL `studyPlanV2Detail`, planSlug `top-100-liked` | POST https://leetcode.com/graphql, no auth |
| Interview 150 | same API, planSlug `top-interview-150` | |
| NeetCode 250 | `ascherj/neetcode-250-guide/neetcode_250_complete.json` | canonical 250 = NeetCode 150 + 100 |
| 0x3F | 12 leetcode.cn discuss posts (master index = post 3141566) | content is in each page's `__NEXT_DATA__` JSON; `circle/discuss/<id>` 308-redirects to `/discuss/post/<id>/` |

These lists (esp. 0x3F) are actively maintained and change over time — current data is a 2026-06-09 snapshot.

## Design decisions for the tracker

- **Canonical ID = problem slug** (e.g. `two-sum`). The four lists overlap heavily
  (Hot100 ∩ Interview150; NeetCode150 ⊂ 250; 0x3F covers most). Model problems as one table
  with list-membership tags, NOT four disjoint sets. `leetcode.com/.cn` links share the same slug.
- **Difficulty granularity differs.** LeetCode/NeetCode give only Easy/Medium/Hard. 0x3F embeds
  numeric **contest ratings** (难度分, ~1000–3000) inline — finer-grained, good for ordering reviews.
  Ratings come from the zerotrac rating project and can be joined onto any problem by slug.
- **Ebbinghaus scheduling**: on a Solved review, push the next review out along the curve
  (e.g. 1d → 2d → 4d → 7d → 15d → 30d); on Forgotten, reset the interval.
