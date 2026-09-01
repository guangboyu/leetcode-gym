# Changelog

All notable changes to LeetCode Gym. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions follow SemVer.

## [0.3.0] (2026-09-01)

### Added
- **Learn tab**: one ordered route of 21 patterns. Hand-written tutorials
  (`tutorials/*.md`, with animated GIFs) render inside the app and their problem
  tables become live tracker rows. Patterns without a tutorial fall back to a
  curated recognize/solve card and are marked "in progress".
- 0x3F's lists are an attribute now: every subtopic has an "Extend with 0x3F"
  disclosure, rating-capped, with a link to the original post.
- macOS-native shell: sidebar, hidden-inset title bar, native menu bar with
  ⌘ shortcuts, window size/position memory, light and dark themes.
- Keyboard everywhere: ⌘1–5 views, ⌘F search, ⌘, settings, ⌘/ shortcut sheet,
  j/k row cursor with s/h/f/r marks, Drill on space/r/s/h/f.
- Undo for every mark (toast + ⌘Z), stored as an append-only `undo` event so it
  merges across machines like everything else.
- Stats: activity heatmap and streaks.
- Browse: sortable columns, multi-select topic filter, filters in the URL.
- Settings view (data folder, cap, appearance, reset) and an About panel.
- Preferences live in `settings.json` next to your progress, so they sync with it.
- GitHub Actions: tests on every push; tagging `vX.Y.Z` builds the macOS DMG and
  the Windows exe and attaches them to the release.

### Changed
- Renamed to **LeetCode Gym** (app bundle, config folder migrated automatically;
  an existing `~/LeetCodeTracker` progress folder keeps being used).
- `problems.json` is served with ETag + gzip; tutorial assets are cached.
- Default progress folder for new installs is inside the OS application-support
  directory instead of the home folder.

### Removed
- The two-part study route (beginner + "go deeper") and the duplicated code
  templates that came with it; `curriculum.js`/`guide.js` moved to `scripts/legacy/`
  as the provenance of `data/patterns.json`.

## [0.2.0] (2026-07-20)
- Study route with the full 0x3F taxonomy, guide cards per chapter, Drill list/type filters,
  curated beginner route with recognize/solve subtopics.

## [0.1.0] (2026-07-22)
- First desktop release: Today / Browse / Drill / Stats, Ebbinghaus scheduling,
  Dropbox-style folder sync, macOS `.app` + DMG and Windows `.exe`.
