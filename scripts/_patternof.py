"""Python mirror of `Route.patternOf` in tracker/static/route.js.

The build scripts and tests need to know which core pattern stage a problem
belongs to (NeetCode category first, then Hot 100 group, then Interview 150
group, plus two overrides). The dict literals below MUST stay textually equal
to the JS ones — tests/test_patterns.py parses route.js and compares.
"""

NC_PATTERN = {
    "Arrays & Hashing": "Arrays & Hashing",
    "Two Pointers": "Two Pointers",
    "Sliding Window": "Sliding Window",
    "Stack": "Stack & Monotonic Stack",
    "Binary Search": "Binary Search",
    "Linked List": "Linked List",
    "Trees": "Trees & BSTs",
    "Heap / Priority Queue": "Heap / Priority Queue",
    "Backtracking": "Backtracking",
    "Tries": "Tries",
    "Graphs": "Graphs",
    "Advanced Graphs": "Advanced Graphs",
    "1-D Dynamic Programming": "1-D Dynamic Programming",
    "2-D Dynamic Programming": "2-D Dynamic Programming",
    "Greedy": "Greedy",
    "Intervals": "Intervals",
    "Math & Geometry": "Math & Bit Manipulation",
    "Bit Manipulation": "Math & Bit Manipulation",
}
H1_PATTERN = {
    "Hashing": "Arrays & Hashing",
    "Misc": "Arrays & Hashing",
    "Two Pointers": "Two Pointers",
    "Sliding Window": "Sliding Window",
    "Stack": "Stack & Monotonic Stack",
    "Binary Search": "Binary Search",
    "Linked Lists": "Linked List",
    "Binary Tree": "Trees & BSTs",
    "Heap": "Heap / Priority Queue",
    "Backtracking": "Backtracking",
    "Trie": "Tries",
    "Graph": "Graphs",
    "Dynamic Programming": "1-D Dynamic Programming",
    "Greedy": "Greedy",
    "Matrix": "Math & Bit Manipulation",
}
I150_PATTERN = {
    "Hashmap": "Arrays & Hashing",
    "Array / String": "Arrays & Hashing",
    "Divide & Conquer": "Arrays & Hashing",
    "Two Pointers": "Two Pointers",
    "Sliding Window": "Sliding Window",
    "Stack": "Stack & Monotonic Stack",
    "Binary Search": "Binary Search",
    "Linked List": "Linked List",
    "Binary Tree General": "Trees & BSTs",
    "Binary Tree BFS": "Trees & BSTs",
    "Binary Search Tree": "Trees & BSTs",
    "Heap": "Heap / Priority Queue",
    "Backtracking": "Backtracking",
    "Trie": "Tries",
    "Graph General": "Graphs",
    "Graph BFS": "Graphs",
    "1D DP": "1-D Dynamic Programming",
    "Kadane's Algorithm": "1-D Dynamic Programming",
    "Multidimensional DP": "2-D Dynamic Programming",
    "Intervals": "Intervals",
    "Math": "Math & Bit Manipulation",
    "Bit Manipulation": "Math & Bit Manipulation",
    "Matrix": "Math & Bit Manipulation",
}
PATTERN_OVERRIDES = {
    31: "Two Pointers",
    240: "Binary Search",
}


def pattern_of(p):
    """p: a data/problems.json entry -> legacy pattern-stage name or None."""
    if p["id"] in PATTERN_OVERRIDES:
        return PATTERN_OVERRIDES[p["id"]]
    lists = p["lists"]
    if "neetcode250" in lists:
        return NC_PATTERN.get(lists["neetcode250"]["category"])
    if "hot100" in lists:
        return H1_PATTERN.get(lists["hot100"]["group"])
    if "interview150" in lists:
        return I150_PATTERN.get(lists["interview150"]["group"])
    return None
