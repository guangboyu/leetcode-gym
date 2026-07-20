# LeetCode Study Tracker

A desktop study tracker for LeetCode interview prep. It merges four curated problem
lists into one searchable table of 2,676 problems, lets you mark each problem as
Solved, Forgot, or Reset, and schedules reviews on an Ebbinghaus forgetting curve so
you revisit each problem right before you would forget it.

The app runs in its own native window. There is nothing to install beyond the app itself.

## Download

Get the newest build from the [Releases page](https://github.com/guangboyu/leetcode-study-tracker/releases/latest),
or download directly:

| Platform | File | Download |
|----------|------|----------|
| macOS | `LeetCodeTracker.dmg` | [Download for macOS](https://github.com/guangboyu/leetcode-study-tracker/releases/latest/download/LeetCodeTracker.dmg) |
| Windows | `LeetCodeTracker.exe` | [Download for Windows](https://github.com/guangboyu/leetcode-study-tracker/releases/download/v0.1.0/LeetCodeTracker.exe) (v0.1.0; a rebuild on Windows is needed per release) |

## Install

### macOS

1. Open `LeetCodeTracker.dmg`.
2. Drag **LeetCodeTracker** onto the **Applications** folder.
3. In Applications, right-click **LeetCodeTracker** and choose **Open**, then confirm once.

The app is not code-signed, so the first launch needs right-click then Open. A plain
double-click will not work the first time. If macOS reports that the app is damaged,
clear the download flag once in Terminal:

```bash
xattr -dr com.apple.quarantine /Applications/LeetCodeTracker.app
```

### Windows

1. Double-click `LeetCodeTracker.exe`.
2. If SmartScreen appears, click **More info**, then **Run anyway**.

## Using the app

The app opens on the **Today** tab. Each tab covers one part of the workflow:

- **Today**: reviews that are due now, followed by the study route.
- **Browse**: filter by list, topic, difficulty, or status. Search by name and sort by rating.
- **Drill**: a random unseen problem with its topic and difficulty hidden until you answer, which trains you to recognize problem types cold. Narrow the draw by source list (for most companies Hot 100 + Top Interview 150 + NeetCode 250 is plenty) and by problem type (skip types your target companies rarely ask, or focus on one to reinforce it).
- **Stats**: per-list progress and a data-range to time-complexity reference table.

The study route has two parts, both clickable so you can practice any type at any time:

- **Beginner route**: 0x3F's 7-stage Method A order (sliding window, binary search, core data
  structures, tree DFS, grid DFS, backtracking, DP). The recommended next stage is marked.
- **Full topic lists**: all 12 of 0x3F's topic lists with every interview-tier chapter, so
  monotonic stack, bit manipulation, graph theory, greedy, math, and strings are covered too.

Inside a type, subtopics are grouped under their real chapter names (fixed-length window,
knapsack, topological sort, and so on). Selecting a subtopic shows a short guide card: what the
technique is, when to use it, a compact code template where a canonical one exists, and a link
to the original 0x3F list. Subtopics you consider irrelevant can be skipped with one click
(restorable); rarely-interviewed sections are hidden by default behind a
"show optional &amp; niche subtopics" toggle.

When you finish a problem, mark it:

- **Solved**: you solved it on your own. The next review moves further out along the curve.
- **w/ help**: you solved it after reading the editorial. It returns in 2 days and the interval does not grow.
- **Forgot**: you could not solve it at review time. It becomes due immediately and the interval restarts.

## How reviewing works

Reviews follow an Ebbinghaus forgetting curve. Each time you solve a problem on your own,
the next review moves to the next interval:

```
1 day  ->  2 days  ->  4 days  ->  7 days  ->  15 days  ->  30 days
```

Clear all six intervals and the problem becomes **Mastered**, with no more reviews.
Marking **Forgot** restarts the ladder. Marking **w/ help** holds the ladder in place and
brings the problem back in 2 days.

A **rating cap** in the header (default 1700) keeps you at one difficulty level until you
finish everything at or below it, then you raise the cap. The dynamic programming stage
widens to 2000 automatically.

## Sync progress across machines

Your progress is stored on your own computer. To sync it between machines:

1. Click the **Settings** button (top right).
2. Choose **Choose folder** and select a folder inside Dropbox, iCloud Drive, or OneDrive.
3. Repeat on your other machine and pick the same synced folder.

The two machines merge their histories without losing anything, because progress is stored
as an append-only event log. Avoid studying on two machines at the same second, or the
cloud drive may create a conflicted copy.

The chosen folder is remembered in a small config file:

- macOS: `~/Library/Application Support/LeetCodeTracker`
- Windows: `%APPDATA%\LeetCodeTracker`

Without a choice, progress is saved to `~/LeetCodeTracker`, or to the folder named in the
`LEETCODE_TRACKER_DATA` environment variable if it is set.

## The lists

| List | Problems | Notes |
|------|----------|-------|
| [LeetCode Hot 100](source/Hot100.md) | 100 | Official study plan |
| [LeetCode Top Interview 150](source/Leetcode150.md) | 150 | Official study plan |
| [NeetCode 250](source/Neetcode250.md) | 250 | NeetCode 150 plus 100 more |
| [0x3F (灵茶山艾府)](source/ox3F/) | 2,346 curated | 12 topic lists translated to English, competition-only sections omitted |

Problems are keyed by their leetcode.com slug and tagged with the lists they belong to.
The lists overlap heavily, so one review counts across all of them. Most problems carry a
numeric contest rating (roughly 1000 to 3000) for fine-grained ordering.

Sources, the curation pipeline, and refresh instructions are in [source/README.md](source/README.md).
Lists by [LeetCode](https://leetcode.com), [NeetCode](https://neetcode.io), and
[灵茶山艾府 / EndlessCheng](https://github.com/EndlessCheng); ratings by
[zerotrac](https://zerotrac.github.io/leetcode_problem_rating/). This project redistributes
factual list data only (IDs, titles, slugs, grouping), with no problem statements or solutions.

## Run from source

You can run the tracker without downloading a release. This needs Python 3, standard
library only, with no extra packages:

```bash
python3 tracker/server.py
```

Then open http://localhost:8765 in your browser. Progress is saved to `data/progress.json`.

To open the same server in a native window instead of a browser tab:

```bash
python3 -m tracker.desktop
```

## Build the desktop app

Building the standalone app needs two extra packages on the build machine only:

```bash
pip install -r packaging/requirements.txt
```

Then build for your platform. PyInstaller cannot cross-compile, so build on each operating
system separately:

```bash
# macOS: produces dist/LeetCodeTracker.app and dist/LeetCodeTracker.dmg
bash packaging/build_macos.sh

# Windows: produces dist\LeetCodeTracker.exe
powershell -ExecutionPolicy Bypass -File packaging\build_windows.ps1
```

The app wraps the same standard-library server in a native window using
[pywebview](https://pywebview.flowlib.com), which uses the built-in OS webview: WebView2 on
Windows 10 and 11, WKWebView on macOS. There is nothing extra for users to install.

## Back up your progress

Your progress files are gitignored, so they are never committed to this repository, and the
repository can be published without exposing what you have solved. To keep a version-controlled
backup, point the tracker at a separate private repository:

```bash
git clone git@github.com:you/leetcode-progress.git ~/leetcode-progress
python3 tracker/server.py --data-dir ~/leetcode-progress --autocommit --push
```

`--autocommit` commits the event log a minute after each study session and on shutdown.
`--push` also pushes it. Nothing touches this repository.

## Storage

Every action is appended to `data/reviews.jsonl`, which is the source of truth. It is
append-only, so it is safe against crashes and merges cleanly across machines.
`data/progress.json` is a snapshot rebuilt from the log when the server starts.

## Development

```bash
python3 -m unittest discover -s tests
```

The data pipeline that rebuilds everything from raw snapshots is documented in
[source/README.md](source/README.md#regenerating-from-the-repo-root-needs-python3-no-extra-deps).

## License

The code, meaning the tracker and scripts, is [MIT](LICENSE). The problem-list data remains
the work of its upstream curators and is redistributed here as factual data with attribution,
not under the MIT grant.
