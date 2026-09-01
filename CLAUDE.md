# LeetCode Gym

A LeetCode interview-prep app: **Learn** one pattern at a time from pattern
tutorials, **Drill** random type-blind problems, and review on an **Ebbinghaus
forgetting curve**. Stdlib-only Python server + vanilla-JS SPA, packaged as a native
macOS/Windows app with pywebview + PyInstaller. Formerly "LeetCode Study Tracker".

## Status

- **Phase 1 — scrape source lists: DONE** (snapshot 2026-06-09), `source/`.
- **Phase 1.5 — normalize & curate: DONE.** `scripts/` pipeline → `data/problems.json`
  (2,678 problems keyed by slug, list memberships incl. `tutorial`).
- **Phase 2 — tracker: DONE.** Server, event-log storage, scheduler, folder sync.
- **Phase 2.5 — desktop packaging: DONE.** `tracker/desktop.py`, `packaging/`.
- **Phase 3 — LeetCode Gym (Aug 31–Sep 1 2026): DONE on branch `gym`.**
  Rename; design system from the tutorial GIF palette; sidebar shell with hash routes;
  Learn tab driven by `tutorials/*.md`; one unified 21-pattern route with 0x3F as a
  per-subtopic "Extend" attribute; undo; settings.json; heatmap; native menu/title bar;
  CI + tag-triggered release builds. Details in `CHANGELOG.md`.
- Next: more tutorials (user writes them; the pipeline picks them up), Windows build
  verification via CI, code-signing if ever wanted.

## Run / test

```bash
python3 tracker/server.py [--port 8765] [--data-dir DIR] [--autocommit] [--push]
python3 -m tracker.desktop                  # native window (pywebview)
python3 -m unittest discover -s tests       # Python + JS (JS via macOS jsc, or node)
python3 scripts/build_tutorials.py --check  # data/tutorials.json fresh?
```

No build step. `node` is not installed on the dev Mac; JS tests run on
`/System/Library/Frameworks/JavaScriptCore.framework/.../jsc -m` (see `tests/js/README.md`).
Headless Chrome is available for screenshots:
`"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --screenshot=… "http://127.0.0.1:8765/?shell=mac#/learn"`.

## Repository layout

```
tracker/
  server.py            ThreadingHTTPServer: static, /api/{progress,review,settings,activity,about,data-dir},
                       /data/{problems,tutorials,patterns}.json (in-memory, ETag+gzip),
                       /tutorials/<Name>.md + /tutorials/assets/** (whitelisted, cached)
  store.py             reviews.jsonl (truth, append-only, events carry ts; "undo" pops the
                       slug's last effective event) -> replay -> progress.json; settings.json;
                       merge_events for lossless folder switching; activity() for the heatmap
  scheduler.py         ladder 1/2/4/7/15/30d; 6 successes -> mastered; solved_help +2d paused;
                       forgotten -> due now, restart; reset -> untouched (pure, no undo here)
  config.py            APP_NAME="LeetCode Gym"; per-user config dir (migrates from LeetCodeTracker);
                       window geometry
  desktop.py           pywebview window: private_mode=False, text_select, ?shell=mac|win,
                       hidden-inset title bar (NSToolbar UnifiedCompact via AppKit on `loaded`),
                       geometry memory, native menus (MENU_SPEC) dispatching window.Gym.dispatch(),
                       _Api {choose_folder, zoom, open_path, reveal_log, platform}, selftest
  resources.py         resource_root(): repo root or sys._MEIPASS
  static/
    index.html         shell skeleton + inline icon sprite; loads vendor/marked.umd.js, route.js
                       (classic) then js/main.js (module)
    route.js           pure logic, global `Route`: effRating, patternOf, resolveOx3f (section ->
                       chapter -> topic default), learnState(patterns, tutorials, rows, isDone, cap,
                       opts), nextUp, drillPool/inPool. Tested by tests/js/route.test.js
    css/               tokens.css (from tutorials/anim/dsaviz/theme.py; light+dark+data-theme),
                       base, components, shell, views
    js/                main.js (boot, router wiring, mark()+undo toast, shortcuts, Gym.dispatch),
                       store/api/router/keys/toast/format/heatmap/pyhl/md/h/desktop,
                       components/{status,problem-table}.js, views/{learn,learn-read,today,browse,
                       drill,stats,settings}.js  (view contract: id/title/routes/deps/mount/render/
                       toolbar/unmount; ctx = store, api, navigate, toast, keys, mark, patchRows,
                       settings, learn(), effRating)
    vendor/            marked 15.0.12, mermaid 11.6.0 (lazy), JetBrains Mono — README has checksums
data/
  problems.json        generated (build_problems.py); slug -> {id,title,difficulty,rating,paid_only,
                       lists{hot100,interview150,neetcode250,ox3f[],tutorial[]}}
  patterns.json        HAND-CURATED taxonomy: order (17 + insight/strings/number-theory/
                       fenwick-segment), per-pattern signals/one_liner/template/subtopics(core_ids)/
                       legacy_core_ids; ox3f {topics{zh,post,default}, chapters, sections
                       ("topic||2.1.1" numeric keys), hidden}. Drafted once by scripts/draft_patterns.py
                       from scripts/legacy/{curriculum,guide}.js
  tutorials.json       GENERATED by scripts/build_tutorials.py from tutorials/*.md — never edit
tutorials/             the user's tutorials (SlidingWindow.md, TwoPointers.md), GIFs in
                       assets/<pattern>/, generator in anim/ (Pillow; not bundled). README.md carries
                       the auto-generated status table
scripts/               fetch_catalog, gen_lists, extract/parse/gen_0x3f, build_tutorials,
                       build_problems (in that order), draft_patterns (one-shot), _patternof (mirror
                       of route.js patternOf), legacy/
tests/                 unittest: server/store/scheduler/config/desktop/tutorials/patterns/pyhl parity;
                       test_js.py + test_js_modules.py run tests/js/* on jsc (node fallback)
packaging/             LeetCodeGym.spec (datas: static, data/*.json, tutorials/*.md, tutorials/assets),
                       build_macos.sh -> "LeetCode Gym.app" + LeetCode-Gym.dmg, build_windows.ps1,
                       make_icon.py -> AppIcon.icns + static/favicon.svg
.github/workflows/     ci.yml (ubuntu+macos, py3.12/3.13, node), release.yml (tag v* -> DMG + exe)
docs/screenshots/      README images (1280×820, taken with headless Chrome + seeded data)
```

## Design decisions & invariants

- **Canonical id = leetcode.com slug.** Lists overlap; one table with membership tags.
- **Tutorial = source of truth for its pattern.** `build_tutorials.py` parses heading text
  (`## Shape N:`, `### Na.`, `### Title (LC n)`, `### … problems` + `| LC | Title | Diff |
  [State] | Freq | Note |`). Shape ids (`shape-2`, `shape-2a`) are the subtopic ids. The
  user writes the prose — **do not edit tutorial text**; report problems instead.
- **Coverage invariant** (tests/test_patterns.py): every Hot100 ∪ I150 ∪ NC250 problem is in
  some pattern's `core_ids`, `legacy_core_ids`, or a tutorial table. Patterns with a
  tutorial have no `subtopics`. Every 0x3F interview-tier section resolves via the three
  tiers; only `hidden` keys may fall through to the topic default.
- **Keep `data/tutorials.json` and `data/problems.json` fresh** after touching tutorials
  (`build_tutorials.py` then `build_problems.py`); CI checks freshness.
- **0x3F stays as-is with attribution** (user's decision after discussing compilation
  copyright); his chapter intros were retired, only names/post links remain.
- **Storage:** append-only log is truth; `undo` is an event, never a client-side inverse;
  dedupe key `(date, slug, action, ts)`. Preferences in `settings.json` next to progress.
- **Rating cap** applies to the 0x3F extension only; unrated problems use estimates
  (E 1250 / M 1650 / H 2150) for Drill and sort, shown as `≈`.
- **UI:** tokens only (no literal colors outside tokens.css); status = verdict axis
  (blue/amber/red/purple), difficulty = pointer family (teal/indigo/pink); every clickable
  is a `<button>`/`<a>`; views render only their own section; marks patch rows.
- Desktop data dir precedence: `--data-dir` > config (UI choice) > `$LEETCODE_TRACKER_DATA`
  > existing `~/LeetCodeTracker` > `<app support>/LeetCode Gym/data`.
