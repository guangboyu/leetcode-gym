# LeetCode Gym

Learn a pattern, drill it cold, keep it on a forgetting curve.

A native macOS / Windows app for LeetCode interview prep:

- 2,678 problems from Hot 100, Top Interview 150, NeetCode 250 and 0x3F's topic lists
- pattern tutorials with animations
- a spaced-repetition scheduler that brings each problem back before you forget it

> **Under construction.** The app works end to end. Tutorials are being written one
> pattern at a time (2 of 21 so far: Sliding Window and Two Pointers). See
> [tutorials/README.md](tutorials/README.md) for the current list.

![Learn tab](docs/screenshots/learn.png)

[![CI](https://github.com/guangboyu/leetcode-gym/actions/workflows/ci.yml/badge.svg)](https://github.com/guangboyu/leetcode-gym/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/guangboyu/leetcode-gym?display_name=tag)](https://github.com/guangboyu/leetcode-gym/releases/latest)
[![MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## Install

| | | |
|---|---|---|
| macOS 11+ | `LeetCode-Gym.dmg` | [Download](https://github.com/guangboyu/leetcode-gym/releases/latest/download/LeetCode-Gym.dmg) |
| Windows 10/11 | `LeetCode Gym.exe` | [Download](https://github.com/guangboyu/leetcode-gym/releases/latest/download/LeetCode.Gym.exe) |

- macOS: drag the app to Applications, then right-click and choose **Open** the first time
  (the app is not code-signed). If macOS says it is damaged, run
  `xattr -dr com.apple.quarantine "/Applications/LeetCode Gym.app"` once.
- Windows: if SmartScreen appears, choose *More info*, then *Run anyway*.
- From source, with nothing but Python 3: `python3 tracker/server.py`, then open
  http://localhost:8765. For the native window: `pip install pywebview` and
  `python3 -m tracker.desktop`.

## How to use it

**1. Learn one pattern at a time**

- Open *Learn*. Patterns run from foundations to advanced; take the next one.
- Read its tutorial: how to recognize the pattern, the template, worked examples with
  animations, the pitfalls.
- Solve the problems in the order the tutorial lists them. Every table is live: mark
  **Solved**, **Help** (solved after reading a solution) or **Forgot** right there.

**2. Drill by rating, type hidden**

- Open *Drill*, set a rating range around your level, pick the lists. Hot 100 +
  Interview 150 + NeetCode 250 covers most interviews.
- Press space. You get one untouched problem with its pattern hidden.
- Decide the approach before you reveal or mark. That is the skill interviews test.
- Raise the range as your hit rate goes up.

**3. Review on the forgetting curve**

- Reviews follow the Ebbinghaus forgetting curve: a problem comes back in *Today*
  right before you would forget it, at 1, 2, 4, 7, 15, then 30 days after each clean
  solve. After that it is mastered.
- **Forgot** restarts the ladder. **Help** holds it and brings the problem back in two days.
- Any mark can be undone (⌘Z).

| | |
|---|---|
| ![Reading a tutorial](docs/screenshots/read.png) | ![Today](docs/screenshots/today.png) |
| ![Browse](docs/screenshots/browse.png) | ![Stats](docs/screenshots/stats.png) |

Also in the app:

- *Browse*: every problem, with filters, sorting and search (⌘F)
- *Stats*: activity heatmap, streaks, coverage per list
- *Settings*: rating cap, light or dark theme, progress folder
- Keyboard: ⌘1 to ⌘5 switch views, ⌘, opens Settings, ⌘/ lists every shortcut;
  in tables `j`/`k` move, `s`/`h`/`f` mark, `Enter` opens the problem on LeetCode

## Where progress lives

Progress is an append-only log in one folder, plus a settings file next to it.

- By default the folder is local (the application-support directory on macOS and
  Windows). That is all you need on a single machine.
- To sync machines, open Settings and *Choose folder*, then pick the same Dropbox,
  iCloud or OneDrive folder on each machine. Histories merge; nothing is lost.
- For a git-backed copy: `python3 tracker/server.py --data-dir ~/leetcode-progress --autocommit --push`

## Data

| List | Problems |
|---|---|
| [LeetCode Hot 100](source/Hot100.md) | 100 |
| [LeetCode Top Interview 150](source/Leetcode150.md) | 150 |
| [NeetCode 250](source/Neetcode250.md) | 250 |
| [0x3F topic lists](source/ox3F/) | 2,346 (12 lists, interview-tier sections) |

- One table keyed by leetcode.com slug; a problem in several lists is reviewed once.
- Ratings are contest ratings from zerotrac. Unrated problems get an estimate, shown as `≈`.
- Only ids, titles and groupings are stored. No statements, no solutions.
- Snapshot: 2026-06-09. Refresh instructions: [source/README.md](source/README.md).

## Develop

```bash
python3 -m unittest discover -s tests      # Python + JS tests, no install needed
python3 scripts/build_tutorials.py         # after editing tutorials/*.md
bash packaging/build_macos.sh              # dist/LeetCode Gym.app and .dmg
```

[CONTRIBUTING.md](CONTRIBUTING.md) covers the layout, how to add a tutorial, and the
data invariants. Releases are built by GitHub Actions from a `vX.Y.Z` tag.
Changes are listed in [CHANGELOG.md](CHANGELOG.md).

## Acknowledgements

The learning path and problem selection are informed by:

- [灵茶山艾府 (EndlessCheng)](https://github.com/EndlessCheng)'s problem lists and the
  MIT-licensed [codeforces-go](https://github.com/EndlessCheng/codeforces-go) repository;
  parts of the problem categorization are derived from them
- [NeetCode 250](https://neetcode.io)
- LeetCode's [Hot 100 and Top Interview 150](https://leetcode.com/studyplan/)
- [zerotrac](https://zerotrac.github.io/leetcode_problem_rating/)'s problem ratings

The tutorials, animations and the interface are written for LeetCode Gym.
Third-party licenses: [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## License

[MIT](LICENSE). Problem-list data stays the work of its curators and is redistributed
as factual data with attribution. Not affiliated with LeetCode LLC.
