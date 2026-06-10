#!/usr/bin/env python3
"""Parse the raw 0x3F Chinese topic lists (source/ox3F/raw-zh/*.md) into
structured JSON at source/data/ox3f.json.

Captures the section hierarchy and, per section, the ordered problem list
(slug, numeric/string id, Chinese title, premium flag). Ratings and English
titles are NOT taken from here — they are joined from source/data/catalog.json
(LeetCode API + zerotrac) downstream.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "source" / "ox3F" / "raw-zh"
OUT = ROOT / "source" / "data" / "ox3f.json"

# file stem -> (zh topic, en topic, source post url)
TOPICS = {
    "01-sliding-window-two-pointers": ("滑动窗口与双指针", "Sliding Window & Two Pointers", "https://leetcode.cn/discuss/post/0viNMK/"),
    "02-binary-search": ("二分算法", "Binary Search", "https://leetcode.cn/discuss/post/SqopEo/"),
    "03-monotonic-stack": ("单调栈", "Monotonic Stack", "https://leetcode.cn/discuss/post/9oZFK9/"),
    "04-grid-graph": ("网格图", "Grid Graph", "https://leetcode.cn/discuss/post/YiXPXW/"),
    "05-bit-manipulation": ("位运算", "Bit Manipulation", "https://leetcode.cn/discuss/post/dHn9Vk/"),
    "06-graph-theory": ("图论算法", "Graph Theory", "https://leetcode.cn/discuss/post/01LUak/"),
    "07-dynamic-programming": ("动态规划", "Dynamic Programming", "https://leetcode.cn/discuss/post/tXLS3i/"),
    "08-data-structures": ("常用数据结构", "Data Structures", "https://leetcode.cn/discuss/post/mOr1u6/"),
    "09-math": ("数学算法", "Math", "https://leetcode.cn/discuss/post/IYT3ss/"),
    "10-greedy-thinking": ("贪心与思维", "Greedy & Thinking", "https://leetcode.cn/discuss/post/g6KTKL/"),
    "11-linkedlist-tree-backtracking": ("链表、树与回溯", "Linked List, Tree & Backtracking", "https://leetcode.cn/discuss/post/K0n2gO/"),
    "12-strings": ("字符串", "Strings", "https://leetcode.cn/discuss/post/SJFwQI/"),
}

HEADER_RE = re.compile(r"^(#{2,6})\s+(.*?)\s*$")
ITEM_RE = re.compile(
    r"^\s*[-*]\s*\[(?P<text>[^\]]+)\]\(https://leetcode\.(?:cn|com)/problems/(?P<slug>[^/)?#]+)/?[^)]*\)(?P<rest>.*)$"
)
ID_RE = re.compile(r"^(?P<id>(?:\d+|LCP \d+|LCS \d+|LCR \d+|面试题 [\d.]+|剑指 Offer [\dIV. -]+?))[.、]?\s+(?P<title>.+)$")

# Prose-only headers: do not open a new section; problems after them still
# belong to the enclosing section (e.g. "#### 答疑" inside "§2.1 求最小").
IGNORE_HEADERS = {"答疑", "前言", "思考", "思考题", "总结"}
# Trailing cross-link sections (links to his other lists, no problems).
STOP_HEADERS = {"关联题单", "算法题单"}


def parse_file(path: Path):
    stack = []          # [(level, header text)]
    sections = []       # flattened sections that directly contain problems
    current = None      # section dict problems are appended to
    in_code = False

    for line in path.read_text(encoding="utf-8").splitlines():
        if line.lstrip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue

        m = HEADER_RE.match(line)
        if m:
            level, text = len(m.group(1)), m.group(2)
            if text in IGNORE_HEADERS or text.startswith("⚠"):
                continue
            while stack and stack[-1][0] >= level:
                stack.pop()
            stack.append((level, text))
            current = None  # a new section starts on its first problem
            continue

        m = ITEM_RE.match(line)
        if not m:
            continue
        path_now = [t for _, t in stack]
        if any(t in STOP_HEADERS for t in path_now):
            continue
        text, rest = m.group("text"), m.group("rest")
        idm = ID_RE.match(text)
        prob = {
            "slug": m.group("slug"),
            "id": idm.group("id") if idm else None,
            "zh_title": idm.group("title") if idm else text,
            "premium": "会员题" in rest,
        }
        if current is None or current["path"] != path_now:
            current = {"path": path_now, "problems": []}
            sections.append(current)
        current["problems"].append(prob)

    return sections


def main():
    topics = []
    all_slugs = set()
    for stem, (zh, en, post) in TOPICS.items():
        sections = parse_file(RAW / f"{stem}.md")
        n = sum(len(s["problems"]) for s in sections)
        slugs = {p["slug"] for s in sections for p in s["problems"]}
        all_slugs |= slugs
        topics.append({"file": stem, "zh": zh, "en": en, "post": post, "sections": sections})
        print(f"{stem}: {len(sections)} sections, {n} entries, {len(slugs)} unique slugs")

    OUT.write_text(json.dumps({"snapshot": "2026-06-09", "topics": topics},
                              ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"\nWrote {OUT}  ({len(all_slugs)} unique slugs across all topics)")


if __name__ == "__main__":
    main()
