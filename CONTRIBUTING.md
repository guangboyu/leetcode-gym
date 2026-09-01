# Contributing

Thanks for helping. This file is the short version of how the repo is put
together and how to check your change before opening a pull request.

## Run it

```bash
python3 tracker/server.py            # http://localhost:8765, stdlib only, no install
python3 -m tracker.desktop           # same app in a native window (needs pywebview)
python3 -m unittest discover -s tests
```

The Python suite also runs the JavaScript tests: on macOS through the system
JavaScriptCore shell (`jsc`), elsewhere through `node` if present (see
`tests/js/README.md`). Nothing needs a build step: `tracker/static/js/` is
served as plain ES modules.

## Where things live

| Path | What |
|---|---|
| `tracker/server.py` | HTTP server: static files, `/api/*`, `/data/*.json`, `/tutorials/*` |
| `tracker/store.py`, `scheduler.py` | append-only event log → progress snapshot; the Ebbinghaus ladder |
| `tracker/desktop.py` | pywebview window, native menu, window memory (macOS polish) |
| `tracker/static/js/` | the app: `main.js` shell, `views/*.js` one per sidebar item, `components/` shared row/table, core modules (`store`, `router`, `keys`, `toast`, `md`, `pyhl`, `heatmap`) |
| `tracker/static/css/` | design tokens (`tokens.css`, derived from `tutorials/anim/dsaviz/theme.py`), base, components, shell, views |
| `tracker/static/route.js` | pure learn/drill logic (`learnState`, `nextUp`, `drillPool`), classic script so it is testable without a bundler |
| `data/problems.json` | 2,678 problems keyed by slug with list memberships (generated) |
| `data/patterns.json` | the 21-pattern taxonomy + the 0x3F chapter/section mapping (hand-curated, drafted by `scripts/draft_patterns.py`) |
| `data/tutorials.json` | parsed from `tutorials/*.md` by `scripts/build_tutorials.py` (generated, never edit by hand) |
| `tutorials/` | the hand-written pattern tutorials, their GIFs, and the animation generator |
| `scripts/` | the data pipeline (see `source/README.md` for the full refresh) |
| `packaging/` | PyInstaller spec, build scripts, icon |

## Writing or editing a tutorial

1. Add `tutorials/<PatternName>.md`. The file name in CamelCase becomes the
   pattern id (`SlidingWindow.md` → `sliding-window`), which must exist in
   `data/patterns.json` `order`.
2. Follow the structure the parser expects (see `SlidingWindow.md`):
   `## Shape N: name` sections, optional `### Na. name` sub-shapes, worked
   examples as `### Title (LC 123)`, and one problem table per (sub)shape under a
   `### … problems` heading with columns `LC | Title | Diff | [State] | Freq | Note`.
   Required sections: Contents, The one idea, Which shape, at least one Shape,
   Pitfalls, Drills, Reference card. Add ` (draft)` to the H1 to publish it as a draft.
3. Put GIFs under `tutorials/assets/<pattern-id>/` and reference them as
   `assets/<pattern-id>/lcNNNN-*.gif`. Regenerate with `tutorials/anim/render_all.py`
   (see `tutorials/anim/README.md`).
4. Rebuild and check:
   ```bash
   python3 scripts/build_tutorials.py           # → data/tutorials.json + tutorials/README.md status table
   python3 scripts/build_problems.py            # tags the table problems in data/problems.json
   python3 -m unittest discover -s tests        # ids resolve, GIFs exist, anchors resolve, coverage holds
   ```
   Warnings (a difficulty that disagrees with LeetCode, a core problem the tutorial
   does not list) are printed; errors fail the build.
5. Commit the markdown, the GIFs and the regenerated JSON together; CI fails
   if `data/tutorials.json` is stale.

## Changing the taxonomy

`data/patterns.json` is hand-curated. Keep these invariants (the tests enforce
them): every problem in Hot 100 ∪ Interview 150 ∪ NeetCode 250 belongs to some
pattern's core list or tutorial table; every 0x3F interview-tier section resolves
through `ox3f.sections` → `ox3f.chapters` → `ox3f.topics[].default`; patterns with
a tutorial carry no `subtopics` (the tutorial's shapes are the subtopics).

## Style

- Python: stdlib only in `tracker/` and `scripts/`; docstrings say *why*.
- JavaScript: ES modules, no framework, no build. Build DOM with `html\`\`` from
  `h.js` (auto-escaping); style through tokens; every clickable thing is a
  `<button>` or `<a>`; keyboard paths for anything the mouse can do.
- CSS: tokens only, never a literal color outside `tokens.css`; both themes.
- Commit messages explain the reason, not just the change.

## Releasing

Bump `tracker/__init__.py`, add a `CHANGELOG.md` entry, tag `vX.Y.Z` and push the
tag. GitHub Actions builds the macOS DMG and the Windows exe and attaches them to
the release.
