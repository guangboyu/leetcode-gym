# LeetCode Study Tracker

A local, dependency-free study tracker for LeetCode interview prep. It merges four curated
problem lists into one table (2,676 problems), lets you mark each problem
**Solved / Forgot / Reset**, and schedules reviews on an **Ebbinghaus forgetting curve**.

## Quick start

```bash
python3 tracker/server.py        # then open http://localhost:8765
```

Requires only python3 (stdlib) on Linux, macOS, or Windows. Your progress is saved to
`data/progress.json` — a plain JSON file you can commit to keep it safe across machines.

## Desktop app (Windows & macOS)

Prefer a double-click app in its own window instead of a browser tab? Build a standalone
executable — no Python needed on the machine that runs it.

```bash
pip install -r packaging/requirements.txt      # pywebview + pyinstaller (build machine only)

# Windows:
powershell -ExecutionPolicy Bypass -File packaging\build_windows.ps1   # -> dist\LeetCodeTracker.exe
# macOS:
bash packaging/build_macos.sh                                          # -> dist/LeetCodeTracker.app + .dmg
```

PyInstaller can't cross-compile, so build once on each OS. The app wraps the same stdlib
server in a native window (via [pywebview](https://pywebview.flowlib.com); it uses the OS
webview — WebView2 on Windows 10/11, WKWebView on macOS — so there's nothing extra to install).

- **Windows** builds a single-file `LeetCodeTracker.exe`.
- **macOS** builds a folder-based `LeetCodeTracker.app` (onedir — the runtime ships
  unpacked, so it launches fast) with a custom app icon, then packages it into
  `dist/LeetCodeTracker.dmg` for handing out. Regenerate the icon with
  `python3 packaging/make_icon.py`; rebuild just the DMG with `bash packaging/make_dmg.sh`.

Run from source without building: `python -m tracker.desktop`.

### Installing (macOS) — for people you share the DMG with

The app is **unsigned** (no paid Apple Developer ID), so macOS Gatekeeper needs a one-time
nudge. Send recipients the `.dmg` and these steps:

1. Open `LeetCodeTracker.dmg` and drag **LeetCodeTracker** onto the **Applications** shortcut.
2. In `/Applications`, **right-click the app → Open**, then confirm once. (Double-clicking a
   downloaded, unsigned app just bounces — right-click → Open is what lets it through.)
3. If macOS instead says the app is *"damaged and can't be opened"* (the quarantine flag on
   a downloaded DMG), clear it once in Terminal:
   ```bash
   xattr -dr com.apple.quarantine /Applications/LeetCodeTracker.app
   ```

On first launch the app creates `~/LeetCodeTracker/` and starts saving progress there on the
first action — no setup. To remove all these warnings for a wide/non-technical audience,
code-sign + notarize with an Apple Developer ID ($99/yr).

### Syncing progress across machines

Click the **⚙ button** (top-right) → **Choose folder…** and pick a folder inside **Dropbox /
iCloud Drive / OneDrive**. Your progress moves there and the app remembers it. Do the same on
your other machine, pointing at the *same* synced folder — the histories **merge losslessly**
(the append-only event log is unioned, so adopting a folder that already has history keeps
both sides). Only caveat: don't study on two machines in the same instant, or the cloud drive
makes a "conflicted copy".

The chosen folder is remembered in a small config file (`%APPDATA%\LeetCodeTracker` on Windows,
`~/Library/Application Support/LeetCodeTracker` on macOS). Without a choice, progress defaults
to `$LEETCODE_TRACKER_DATA` if set, else `~/LeetCodeTracker`.

Verify a build without opening a window: set `LEETCODE_TRACKER_SELFTEST=report.json` and run
the app; it checks the bundle and exits 0/1.

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
derived snapshot rebuilt on server start.

### Backing up your progress

Your progress files are **gitignored** in this repo, so they're never committed here and
this repo can be published without exposing what you've solved. To keep a git-backed,
off-machine backup anyway, point the tracker at a **separate private repo**:

```bash
# one-time: a private repo just for your progress (set it Private on GitHub)
git clone git@github.com:you/leetcode-progress.git ~/leetcode-progress

python3 tracker/server.py --data-dir ~/leetcode-progress --autocommit --push
```

`--autocommit` commits the event log in that data dir a minute after each study burst and on
shutdown; `--push` also pushes it. Nothing touches this (public) repo. Note: GitHub
visibility is per-repository — a public repo has no "private branch", so a separate private
repo is the way to keep code public and progress private.

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
