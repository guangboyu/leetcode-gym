# Source data — LeetCode study lists

Scraped problem lists that feed the study tracker. Fetched **2026-06-09**.

## Lists

| List | Human-readable | Machine-readable | Count | Source |
|------|----------------|------------------|-------|--------|
| **LeetCode Hot 100** | [Hot100.md](Hot100.md) | [data/hot100.json](data/hot100.json) | 100 | [leetcode.com/studyplan/top-100-liked](https://leetcode.com/studyplan/top-100-liked/) |
| **LeetCode Top Interview 150** | [Leetcode150.md](Leetcode150.md) | [data/interview150.json](data/interview150.json) | 150 | [leetcode.com/studyplan/top-interview-150](https://leetcode.com/studyplan/top-interview-150/) |
| **NeetCode 250** | [Neetcode250.md](Neetcode250.md) | [data/neetcode250.json](data/neetcode250.json) | 250 | [neetcode.io/practice](https://neetcode.io/practice) |
| **灵茶山艾府 (0x3F)** | [ox3F/](ox3F/) (12 topic files + [README](ox3F/README.md)) | — (markdown only) | 2,702 unique | [leetcode.cn discuss 3141566](https://leetcode.cn/discuss/post/3141566/) |

## Data sources & methods

- **Hot 100 / Interview 150** — pulled directly from LeetCode's official GraphQL API (`studyPlanV2Detail`). The `data/*.json` files are the raw API responses (grouped by topic; each problem has `questionFrontendId`, `title`, `titleSlug`, `difficulty`). The `.md` files are generated tables.
- **NeetCode 250** — the canonical 250 (= NeetCode 150 + 100 more), from the curated dataset [ascherj/neetcode-250-guide](https://github.com/ascherj/neetcode-250-guide) (`neetcode_250_complete.json`). Each problem has `name`, `difficulty`, `category`, `leetcode_url`, `slug`. (NeetCode's own [`.problemSiteData.json`](https://github.com/neetcode-gh/leetcode) lists ~420 problems — the full site catalog, not the 250 roadmap — so the curated dataset is used instead.)
- **0x3F** — 12 separate leetcode.cn discuss posts, scraped from each page's embedded `__NEXT_DATA__` JSON and decoded to the original markdown (section structure, problem links, inline notes, and 难度分 difficulty ratings all preserved). See [ox3F/README.md](ox3F/README.md).

## Notes for the tracker

- **Difficulty granularity differs.** LeetCode/NeetCode give Easy/Medium/Hard only. 0x3F lists embed numeric **contest ratings** (难度分, ~1000–3000) inline after most problems — much finer-grained, useful for ordering reviews. These come from the [zerotrac rating project](https://zerotrac.github.io/leetcode_problem_rating/) and could be joined onto the LeetCode/NeetCode problems too via problem slug.
- **Overlap is large.** Hot 100 and Interview 150 share many problems; NeetCode 150 ⊂ NeetCode 250; many 0x3F problems overlap all of these. The tracker should key on the **problem slug** (e.g. `two-sum`) as the canonical ID and track which lists each problem belongs to, rather than treating the lists as disjoint.
- **`.com` vs `.cn`.** LeetCode/NeetCode links use `leetcode.com/problems/<slug>/`; 0x3F links use `leetcode.cn/problems/<slug>/`. Same slug, same problem — normalize to slug.

## Regenerating

```powershell
# Hot100 / Interview150 / NeetCode250 markdown from the JSON in data/:
.\_gen_lists.ps1
```

0x3F lists: see [ox3F/README.md](ox3F/README.md).
