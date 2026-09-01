# Third-party notices

LeetCode Gym is MIT-licensed (see `LICENSE`). It bundles or derives from the
following third-party work, reproduced here with their notices as required.

## Problem lists and categorization

- **灵茶山艾府 / EndlessCheng, algorithm problem lists** (leetcode.cn posts) and
  **codeforces-go** (https://github.com/EndlessCheng/codeforces-go), MIT License,
  Copyright (c) EndlessCheng. Parts of the problem categorization in `data/patterns.json`
  and `source/ox3F/` are derived from these lists.
- **NeetCode 250** (https://neetcode.io): list membership and categories.
- **LeetCode Hot 100 / Top Interview 150** (https://leetcode.com/studyplan/): list
  membership and groups. LeetCode is a trademark of LeetCode LLC; this project is not
  affiliated with or endorsed by LeetCode.
- **zerotrac, LeetCode problem ratings**
  (https://zerotrac.github.io/leetcode_problem_rating/).

Only ids, titles, slugs and groupings are redistributed; no problem statements or
solutions.

## Bundled software (`tracker/static/vendor/`)

- **marked** 15.0.12: MIT License, Copyright (c) 2018+ MarkedJS, (c) 2011-2018
  Christopher Jeffrey. Full text: `tracker/static/vendor/LICENSE-marked.txt`.
- **mermaid** 11.6.0: MIT License, Copyright (c) 2014-2025 Knut Sveidqvist.
  Full text: `tracker/static/vendor/LICENSE-mermaid.txt`.

## Fonts

- **JetBrains Mono**: SIL Open Font License 1.1, Copyright 2020 The JetBrains Mono
  Project Authors. Full text: `tracker/static/vendor/fonts/JetBrainsMono-OFL.txt`
  (also used by the tutorial animations in `tutorials/anim/dsaviz/fonts/`).
- **Inter**: SIL Open Font License 1.1, Copyright 2016 The Inter Project Authors.
  Used by the tutorial animations only; full text: `tutorials/anim/dsaviz/fonts/Inter-OFL.txt`.

## Build-time dependencies (not redistributed)

pywebview (BSD-3-Clause) and PyInstaller (GPL with a bootloader exception that permits
distributing bundled applications under their own license) are used to build the
desktop app; Pillow (MIT-CMU) renders the tutorial GIFs.

---

MIT License (EndlessCheng/codeforces-go, marked, mermaid)

Permission is hereby granted, free of charge, to any person obtaining a copy of this
software and associated documentation files (the "Software"), to deal in the Software
without restriction, including without limitation the rights to use, copy, modify,
merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be included in all copies
or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE
FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
