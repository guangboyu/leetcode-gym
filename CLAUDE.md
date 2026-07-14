# LeetCode Study Tracker

A study tracker that pulls problems from four curated LeetCode lists, lets you mark each
problem **Solved / Unsolved / Forgotten**, and schedules spaced-repetition reviews using an
**Ebbinghaus forgetting curve**.

## Status

- **Phase 1 — scrape source lists: DONE** (snapshot 2026-06-09). All four lists under `source/`.
- **Phase 1.5 — normalize & curate: DONE.** Python pipeline in `scripts/` (no extra deps);
  0x3F lists translated to English and curated for interviews; everything merged into
  `data/problems.json` (2,676 problems keyed by slug with list-membership tags).
- **Phase 2 — tracker: DONE** (MVP + 0x3F-methodology features). Local web app, stdlib
  only: `python3 tracker/server.py [--autocommit]` → http://localhost:8765.
  Tabs: Today (due reviews + 7-stage 0x3F study route), Browse, Drill (type-blind random
  practice), Stats (+ complexity cheat-sheet). Global rating cap (default 1700, DP widens
  to 2000). Actions: Solved / w-help (+2d, ladder paused) / Forgot / Reset.
  Storage: append-only `data/reviews.jsonl` is the source of truth (git-mergeable);
  `data/progress.json` is a derived snapshot. Both gitignored (don't leak progress from
  a public repo); `--data-dir` puts them in a separate private repo that `--autocommit`
  / `--push` backs up off-machine.
  Possible next steps: review-history charts/heatmap, import of LeetCode submissions.
- **Phase 2.5 — desktop packaging: DONE.** Optional native-window app for
  Windows & macOS via `pywebview` + `PyInstaller` (`tracker/desktop.py`,
  `desktop_app.py`, `packaging/`). Wraps the *same* stdlib server (imported
  lazily, so the server stays dependency-free) in an OS webview window; builds
  to a single double-click executable. Desktop progress lives in a persistent
  per-user dir (`$LEETCODE_TRACKER_DATA` or `~/LeetCodeTracker`) — point it at a
  cloud-synced folder to sync machines. Build per-OS (no cross-compile).

## Environment

Linux/macOS/Windows with python3 (stdlib only) to run the server; network needed
only to refresh snapshots. The optional desktop app additionally needs `pywebview`
+ `pyinstaller` (see `packaging/requirements.txt`) on the build machine only.

## Repository layout

```
tracker/               # Phase 2 app (no deps)
  server.py            #   ThreadingHTTPServer: static files, GET /api/progress,
                       #   POST /api/review {slug, action}; --autocommit
  scheduler.py         #   Ebbinghaus ladder 1/2/4/7/15/30d; 6 successes -> mastered;
                       #   solved_help -> +2d ladder paused; forgotten -> due now,
                       #   ladder restarts; reset -> untouched
  store.py             #   data/reviews.jsonl event log (truth) -> replay -> snapshot
  resources.py         #   resolve bundled assets (repo root, or _MEIPASS when frozen)
  desktop.py           #   optional pywebview native window over the same server
  static/              #   vanilla JS SPA (Today+route / Browse / Drill / Stats);
                       #   route.js = pure 0x3F-route logic, node-testable
desktop_app.py         # PyInstaller entry point (repo root so `tracker` imports clean)
packaging/             # desktop build: LeetCodeTracker.spec, build_windows.ps1,
                       #   build_macos.sh, requirements.txt (pywebview + pyinstaller)
tests/                 # python3 -m unittest discover -s tests
scripts/               # data pipeline (run from repo root, in this order to fully rebuild)
  fetch_catalog.py     #   leetcode.com API + zerotrac ratings -> source/data/catalog.json
  gen_lists.py         #   source/data/*.json -> the 3 western .md tables
  extract_0x3f.py      #   saved leetcode.cn post HTML -> raw Chinese markdown
  parse_0x3f.py        #   source/ox3F/raw-zh/*.md -> source/data/ox3f.json
  gen_0x3f_md.py       #   ox3f.json + catalog + sections-meta -> English ox3F lists
  build_problems.py    #   merge all four lists -> data/problems.json
data/
  problems.json        # THE TRACKER INPUT: slug -> {id, title, difficulty, rating,
                       #   paid_only, lists{hot100, interview150, neetcode250, ox3f[]}}
  progress.json        # user review state (derived snapshot; gitignored — see below)
source/
  README.md            # map of all four lists + data-source details + attribution
  Hot100.md            # LeetCode Hot 100 (100)        generated table
  Leetcode150.md       # LeetCode Top Interview 150 (150)
  Neetcode250.md       # NeetCode 250 (250)
  data/                # machine-readable JSON
    hot100.json        #   raw LeetCode GraphQL response (grouped by topic)
    interview150.json  #   raw LeetCode GraphQL response
    neetcode250.json   #   curated 250 dataset (⚠ its `slug` field is the NeetCode slug;
                       #   canonical slug comes from `leetcode_url` — differs for 74/250)
    catalog.json       #   all 3,958 leetcode.com problems: title/difficulty/premium/rating
    ox3f.json          #   full parsed 0x3F lists (sections, tiers, incl. cn-only problems)
  ox3F/                # 灵茶山艾府 (0x3F) lists, curated English editions
    README.md          #   pipeline, curation rules, attribution
    sections-meta.json #   hand-curated zh header -> {en, tier: interview|competition}
    01-…12-*.md        #   12 English topic lists (competition sections & cn-only omitted)
    raw-zh/            #   unmodified Chinese snapshots (12 posts + syllabus.md)
```

## Design decisions for the tracker

- **Canonical ID = leetcode.com problem slug** (e.g. `two-sum`); `.com`/`.cn` share slugs.
  The four lists overlap heavily — problems are one table with list-membership tags
  (see `data/problems.json`), not four disjoint sets.
- **Difficulty**: Easy/Medium/Hard everywhere, plus numeric **contest ratings**
  (~1000–3000+, from zerotrac, in `catalog.json` and `problems.json`) — finer-grained,
  good for ordering reviews. ~63% of problems have one.
- **Interview curation**: every 0x3F section is tiered `interview` or `competition` in
  `sections-meta.json` (judgment call, editable). Competition-only sections are excluded
  from the English lists but kept in `ox3f.json`, and carried as `tier` on ox3f memberships
  in `problems.json` so the tracker can filter.
- **Ebbinghaus scheduling**: on a Solved review, push the next review out along the curve
  (e.g. 1d → 2d → 4d → 7d → 15d → 30d); on Forgotten, reset the interval.
- Upstream lists are actively maintained; all data is a 2026-06-09 snapshot. Refresh
  instructions: `source/README.md` and `source/ox3F/README.md`.
