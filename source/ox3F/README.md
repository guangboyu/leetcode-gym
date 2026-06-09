# 灵茶山艾府 (0x3F / EndlessCheng) — Curated Problem Lists

Source author: **灵茶山艾府 (0x3F)**. Master post "如何科学刷题" (How to study algorithms scientifically):
https://leetcode.cn/discuss/post/3141566/

- [`syllabus.md`](syllabus.md) — the master article (study methodology: methods A/B/C, learning order, time-complexity-vs-data-range table). Text-only reference, no problem links.
- The 12 files below are the **完整题单 (complete problem lists)**, one per topic. Each was fetched from its leetcode.cn discuss post on **2026-06-09** and contains the original section structure (§ headers), problem links, and 0x3F's inline notes.

**Difficulty ratings** (难度分 / LeetCode-contest rating) are embedded inline after most problems, e.g. `746. 使用最小花费爬楼梯 ... 约 1500`. Ratings originate from the [zerotrac rating project](https://zerotrac.github.io/leetcode_problem_rating/); problems without an official contest rating have none.

> Note: problems are organized by 0x3F into a recommended order — within each section, easier (lower-rated) problems come first ("螺旋上升式学习": clear all problems rated ≤1700 before tackling harder ones).

| # | File | Topic (中文) | Topic (EN) | Source post | Unique problems |
|---|------|-------------|------------|-------------|-----------------|
| 1 | [01-sliding-window-two-pointers.md](01-sliding-window-two-pointers.md) | 滑动窗口与双指针 | Sliding Window & Two Pointers | [0viNMK](https://leetcode.cn/discuss/post/0viNMK/) | 264 |
| 2 | [02-binary-search.md](02-binary-search.md) | 二分算法 | Binary Search | [SqopEo](https://leetcode.cn/discuss/post/SqopEo/) | 133 |
| 3 | [03-monotonic-stack.md](03-monotonic-stack.md) | 单调栈 | Monotonic Stack | [9oZFK9](https://leetcode.cn/discuss/post/9oZFK9/) | 62 |
| 4 | [04-grid-graph.md](04-grid-graph.md) | 网格图 | Grid Graph | [YiXPXW](https://leetcode.cn/discuss/post/YiXPXW/) | 69 |
| 5 | [05-bit-manipulation.md](05-bit-manipulation.md) | 位运算 | Bit Manipulation | [dHn9Vk](https://leetcode.cn/discuss/post/dHn9Vk/) | 121 |
| 6 | [06-graph-theory.md](06-graph-theory.md) | 图论算法 | Graph Theory | [01LUak](https://leetcode.cn/discuss/post/01LUak/) | 169 |
| 7 | [07-dynamic-programming.md](07-dynamic-programming.md) | 动态规划 | Dynamic Programming | [tXLS3i](https://leetcode.cn/discuss/post/tXLS3i/) | 611 |
| 8 | [08-data-structures.md](08-data-structures.md) | 常用数据结构 | Data Structures | [mOr1u6](https://leetcode.cn/discuss/post/mOr1u6/) | 587 |
| 9 | [09-math.md](09-math.md) | 数学算法 | Math | [IYT3ss](https://leetcode.cn/discuss/post/IYT3ss/) | 308 |
| 10 | [10-greedy-thinking.md](10-greedy-thinking.md) | 贪心与思维 | Greedy & Thinking | [g6KTKL](https://leetcode.cn/discuss/post/g6KTKL/) | 495 |
| 11 | [11-linkedlist-tree-backtracking.md](11-linkedlist-tree-backtracking.md) | 链表、树与回溯 | Linked List, Tree & Backtracking | [K0n2gO](https://leetcode.cn/discuss/post/K0n2gO/) | 404 |
| 12 | [12-strings.md](12-strings.md) | 字符串 | Strings | [SJFwQI](https://leetcode.cn/discuss/post/SJFwQI/) | 80 |

**Total: 2,702 unique problems** (deduped across all 12 lists; a problem can appear in several topics).

## Re-fetching / updating

These lists are actively maintained by 0x3F and change over time. To refresh, re-run the extractor (it pulls the post HTML's embedded `__NEXT_DATA__` JSON and decodes the markdown body):

```powershell
# Example for the binary-search post:
curl -sL "https://leetcode.cn/discuss/post/SqopEo/" -o post.html
.\_extract.ps1 -HtmlPath post.html -OutPath 02-binary-search.md
```

See [`_extract.ps1`](_extract.ps1) for the extraction logic.
