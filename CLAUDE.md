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
  Tabs: Today (due reviews + study route), Browse, Drill (type-blind random
  practice; filters by source list pool and 0x3F type), Stats (+ complexity cheat-sheet).
  Study route part 1 = curated beginner route: 17 pattern stages partitioning the union of
  Hot 100 + Interview 150 + NeetCode 250 (302 problems; one pattern per problem via
  NC category → H1 group → I150 group priority + 2 overrides, see route.js patternOf).
  Stages split into ~70 hand-curated semantic subtopics (curriculum.js: name + recognize +
  solve + template + explicit id list; every union problem assigned exactly once — keep the
  partition complete when the data snapshot changes; unassigned ids fall into a visible
  "99. More practice" section). Two guide cards per stage: pattern mental map (guide.js
  PATTERNS: signals + intro) and the selected subtopic's recognize/solve/template.
  Cap does NOT apply here.
  Part 2 = all 12 full 0x3F topic lists, every stage/subtopic freely clickable. Subtopic
  chips are grouped under real 0x3F chapter names; selecting one shows a guide card
  (intro + code template + link to his post) from `static/guide.js`. Sections 0x3F marks
  "(optional)" and a small curated NICHE set (route.js) hide behind a toggle; any
  subtopic can be skipped/restored (localStorage).
  Global rating cap (default 1700, DP widens to 2000) applies to the 0x3F lists only.
  Unrated problems get difficulty-based rating estimates (route.js effRating:
  E 1250 / M 1650 / H 2150) used by Drill's range filter and sort; shown as ≈ in tables.
  Actions: Solved / w-help (+2d, ladder paused) / Forgot / Reset.
  Storage: append-only `data/reviews.jsonl` is the source of truth (git-mergeable);
  `data/progress.json` is a derived snapshot. Both gitignored (don't leak progress from
  a public repo); `--data-dir` puts them in a separate private repo that `--autocommit`
  / `--push` backs up off-machine.
  Possible next steps: review-history charts/heatmap, import of LeetCode submissions.
- **Phase 2.5 — desktop packaging: DONE.** Optional native-window app for
  Windows & macOS via `pywebview` + `PyInstaller` (`tracker/desktop.py`,
  `desktop_app.py`, `packaging/`). Wraps the *same* stdlib server (imported
  lazily, so the server stays dependency-free) in an OS webview window. The spec
  branches per-OS: Windows -> single-file `LeetCodeTracker.exe`; macOS -> onedir
  `LeetCodeTracker.app` (runtime shipped unpacked = fast launch, folder-based)
  with a custom icon (`packaging/AppIcon.icns`, drawn by `make_icon.py`), then
  wrapped into a drag-to-install `dist/LeetCodeTracker.dmg` (`make_dmg.sh`, via
  built-in `hdiutil`). Both unsigned — macOS recipients need right-click->Open
  and, if the DMG is quarantined, `xattr -dr com.apple.quarantine` (README has
  the install steps). Desktop progress lives in a persistent
  per-user dir; the in-app **⚙ Settings** dialog lets the user pick the folder
  (native picker via pywebview's `js_api`), stored in `tracker/config.py`
  (`%APPDATA%`/`Application Support`). Point it at a cloud-synced folder to sync
  machines — `GET/POST /api/data-dir` + `server.switch_data_dir()` merge the two
  logs losslessly (`store.merge_events`). Data-dir precedence: `--data-dir` >
  config (UI choice) > `$LEETCODE_TRACKER_DATA` > `~/LeetCodeTracker`. Build
  per-OS (no cross-compile).

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
  store.py             #   data/reviews.jsonl event log (truth) -> replay -> snapshot;
                       #   merge_events/write_events for lossless folder switching
  config.py            #   per-user config (chosen sync folder) in the OS config dir
  resources.py         #   resolve bundled assets (repo root, or _MEIPASS when frozen)
  desktop.py           #   optional pywebview native window over the same server;
                       #   native folder picker (js_api) + config-based data dir
  static/              #   vanilla JS SPA (Today+route / Browse / Drill / Stats);
                       #   route.js = pure route/drill logic (pattern route + 0x3F
                       #   lists + effRating fallbacks), node-testable;
                       #   curriculum.js = beginner-route subtopics: recognize/solve/
                       #   template + explicit problem-id partition (global, no UMD);
                       #   guide.js = pattern mental maps (PATTERNS) and per-chapter
                       #   0x3F intro + template data (all 12 lists)
desktop_app.py         # PyInstaller entry point (repo root so `tracker` imports clean)
packaging/             # desktop build: LeetCodeTracker.spec (branches per-OS),
                       #   build_windows.ps1, build_macos.sh (app -> icon -> dmg),
                       #   make_icon.py (-> AppIcon.icns), make_dmg.sh (hdiutil),
                       #   requirements.txt (pywebview + pyinstaller)
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
