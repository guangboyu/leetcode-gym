#!/usr/bin/env python3
"""Draft data/patterns.json — the unified pattern taxonomy — from the legacy
tracker/static/curriculum.js + guide.js, plus the hand-written 0x3F mapping below.

Run once (kept for provenance; re-running reproduces the same file as long as the
legacy JS files exist). data/patterns.json is hand-curated after that: edit the
JSON directly, and let tests/test_patterns.py keep it honest.

What the file holds (see tests/test_patterns.py for the invariants):
  order        pattern ids in study order: the 17 core stages, then 4 "advanced"
               patterns that give 0x3F-only material (KMP, segment tree, ...) a home
  patterns     id -> {name, tutorial, signals, one_liner, template (lines),
                      legacy_patternOf, subtopics:[{id, name, recognize, solve,
                      template?, core_ids}]}
               A pattern WITH a tutorial carries no subtopics: the tutorial's
               shapes (data/tutorials.json) are its subtopics. Its
               `legacy_core_ids` (the old curriculum's ids) minus the tutorial's
               ids is the app's "Also core, not in the tutorial" group, so no
               core problem is lost while a tutorial is still being written.
  ox3f         topics{name:{zh, post, default}}, chapters{topic:{n: target}},
               sections{"topic||2.1.1": target}, hidden[...]
               A 0x3F membership {topic, section} resolves section -> chapter ->
               topic default; a target is "pattern" or "pattern/subtopic".
               Keys are numeric section paths, never translated names.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATIC = ROOT / "tracker" / "static"
OUT = ROOT / "data" / "patterns.json"
TUTORIALS = ROOT / "data" / "tutorials.json"
PROBLEMS = ROOT / "data" / "problems.json"

sys.path.insert(0, str(ROOT / "scripts"))
from _patternof import pattern_of  # noqa: E402

# legacy stage name -> pattern id (study order)
PATTERN_IDS = [
    ("Arrays & Hashing", "arrays-hashing"),
    ("Two Pointers", "two-pointers"),
    ("Sliding Window", "sliding-window"),
    ("Stack & Monotonic Stack", "stack"),
    ("Binary Search", "binary-search"),
    ("Linked List", "linked-list"),
    ("Trees & BSTs", "trees"),
    ("Heap / Priority Queue", "heap"),
    ("Backtracking", "backtracking"),
    ("Tries", "tries"),
    ("Graphs", "graphs"),
    ("Advanced Graphs", "advanced-graphs"),
    ("1-D Dynamic Programming", "dp-1d"),
    ("2-D Dynamic Programming", "dp-2d"),
    ("Greedy", "greedy"),
    ("Intervals", "intervals"),
    ("Math & Bit Manipulation", "math-bits"),
]
TUTORIAL_FILES = {"sliding-window": "SlidingWindow.md", "two-pointers": "TwoPointers.md"}

# (pattern id, legacy subtopic name without the "N. " prefix) -> subtopic id
SUBTOPIC_IDS = {
    ("arrays-hashing", "Hash set & map basics"): "hash-basics",
    ("arrays-hashing", "Grouping & counting"): "grouping-counting",
    ("arrays-hashing", "Prefix sums & products"): "prefix-sums",
    ("arrays-hashing", "In-place array surgery"): "in-place",
    ("arrays-hashing", "String scanning"): "string-scanning",
    ("arrays-hashing", "Sorting & simulation"): "sorting-simulation",
    ("stack", "Matching & elimination"): "matching",
    ("stack", "Expression parsing"): "expression",
    ("stack", "Monotonic stack"): "monotonic",
    ("stack", "Stack design"): "design",
    ("binary-search", "Boundary on sorted data"): "boundary",
    ("binary-search", "Rotated & mountain arrays"): "rotated-mountain",
    ("binary-search", "Binary search the answer"): "answer",
    ("binary-search", "Divide & eliminate"): "divide-eliminate",
    ("linked-list", "Reversal"): "reversal",
    ("linked-list", "Dummy head & deletion"): "dummy-head-deletion",
    ("linked-list", "Fast & slow pointers"): "fast-slow",
    ("linked-list", "Merging & divide"): "merging-divide",
    ("linked-list", "Design & copying"): "design-copying",
    ("trees", "Traversal basics"): "traversal",
    ("trees", "Top-down DFS (preorder)"): "top-down",
    ("trees", "Bottom-up DFS (postorder)"): "bottom-up",
    ("trees", "BFS by level"): "bfs",
    ("trees", "BST property"): "bst",
    ("trees", "Build & transform"): "build-transform",
    ("trees", "Paths & tree DP"): "paths-tree-dp",
    ("heap", "Top-k & k-th"): "top-k",
    ("heap", "Two heaps"): "two-heaps",
    ("heap", "Scheduling & rearranging"): "scheduling",
    ("backtracking", "Subsets & combinations"): "subsets-combos",
    ("backtracking", "Permutations & boards"): "permutations-boards",
    ("backtracking", "Partition backtracking"): "partition",
    ("backtracking", "Search with pruning"): "pruning",
    ("tries", "Build & query"): "build-query",
    ("tries", "Wildcards & board search"): "wildcards-board",
    ("tries", "Trie + DP"): "trie-dp",
    ("graphs", "Grid flood fill (DFS)"): "flood-fill",
    ("graphs", "BFS shortest steps"): "bfs",
    ("graphs", "Topological sort"): "topo",
    ("graphs", "Union-Find & graph modeling"): "union-find",   # split below
    ("advanced-graphs", "Dijkstra & minimax paths"): "dijkstra",
    ("advanced-graphs", "Minimum spanning tree"): "mst",
    ("advanced-graphs", "Special structures"): "special-structures",
    ("dp-1d", "Linear transitions"): "linear",
    ("dp-1d", "Take or skip (House Robber)"): "take-or-skip",
    ("dp-1d", "Best subarray ending here (Kadane)"): "kadane",
    ("dp-1d", "Partition & decode"): "partition-decode",
    ("dp-1d", "Knapsack on values"): "knapsack",
    ("dp-1d", "Subsequences & palindromes"): "subsequences",
    ("dp-1d", "Game DP"): "game",
    ("dp-2d", "Grid paths & submatrices"): "grid",
    ("dp-2d", "Two sequences"): "two-sequences",
    ("dp-2d", "Knapsack variants"): "knapsack",              # merged into dp-1d/knapsack
    ("dp-2d", "State machines (stock series)"): "state-machines",
    ("dp-2d", "Interval DP"): "interval",
    ("dp-2d", "Game DP on ranges"): "game-ranges",
    ("greedy", "Jump frontier"): "jump-frontier",
    ("greedy", "Running scans (Kadane family)"): "running-scans",
    ("greedy", "Partition by last occurrence"): "partition-last-occurrence",
    ("greedy", "Exchange arguments & case analysis"): "exchange-arguments",
    ("intervals", "Merge & insert"): "merge-insert",
    ("intervals", "Sort by end (scheduling)"): "sort-by-end",
    ("intervals", "Sweep with a heap"): "sweep-heap",
    ("math-bits", "Bit tricks"): "bit-tricks",
    ("math-bits", "Numbers & digits"): "numbers-digits",
    ("math-bits", "Matrix simulation"): "matrix",
    ("math-bits", "Geometry & counting"): "geometry-counting",
}

# ---------------------------------------------------------------------------
# Advanced patterns: homes for 0x3F-only material. Written fresh, standard
# algorithms only, kept short.
ADVANCED = {
    "insight": {
        "name": "Insight & Case Analysis",
        "signals": ["the constraints are tiny or huge in a way that rules out the obvious algorithm",
                    "an invariant, parity, or bound never changes no matter what you do",
                    "“minimum operations” where each operation has one clean effect"],
        "one_liner": "No template. One observation collapses the problem: find what is preserved, what is bounded, or what the extremes force, then the code is a few lines.",
        "template": ["# 1. play the smallest cases by hand",
                     "# 2. name what every operation preserves (sum? parity? order? a bound?)",
                     "# 3. the answer is usually a formula on that invariant, or a scan of the extremes"],
        "subtopics": [
            {"id": "thinking", "name": "Invariants, symmetry, extremes",
             "recognize": "The brute force is obviously too slow and there is no data structure to reach for.",
             "solve": "Work small cases, look for what never changes, and try thinking backwards from the final state. Case analysis is legitimate: split by the extreme element or by parity, solve each case cleanly.",
             "core_ids": []},
        ],
    },
    "strings": {
        "name": "String Algorithms",
        "signals": ["“find every occurrence of a pattern” or “the string repeats itself”",
                    "compare many substrings for equality, faster than O(length) each",
                    "the shortest period / longest border of a string"],
        "one_liner": "Prefix functions and rolling hashes turn substring questions into O(n): a border table answers periodicity and matching, a polynomial hash compares any two substrings in O(1).",
        "template": ["pi = [0] * len(p)             # pi[i] = longest proper border of p[:i+1]",
                     "k = 0",
                     "for i in range(1, len(p)):",
                     "    while k and p[i] != p[k]:",
                     "        k = pi[k - 1]",
                     "    if p[i] == p[k]:",
                     "        k += 1",
                     "    pi[i] = k"],
        "subtopics": [
            {"id": "kmp", "name": "KMP & the failure function",
             "recognize": "Pattern matching in linear time; “shortest string that makes it a repetition”; longest prefix that is also a suffix.",
             "solve": "Build pi on the pattern (or on pattern + '#' + text). A border of length b means the string has period n - b.",
             "template": ["def find_all(text, p):",
                          "    s = p + '#' + text",
                          "    pi = failure(s)",
                          "    return [i - 2 * len(p) for i in range(len(s)) if pi[i] == len(p)]"],
             "core_ids": []},
            {"id": "rolling-hash", "name": "Rolling hash",
             "recognize": "Many substring equality checks, longest duplicate substring, matching after edits.",
             "solve": "h[i+1] = h[i] * B + s[i] mod M; hash(l..r) = h[r+1] - h[l] * B^(r-l+1). Use a big modulus or two moduli; binary search the length when the property is monotone.",
             "template": ["B, M = 131, (1 << 61) - 1",
                          "h, pw = [0], [1]",
                          "for ch in s:",
                          "    h.append((h[-1] * B + ord(ch)) % M)",
                          "    pw.append(pw[-1] * B % M)",
                          "def get(l, r):                   # hash of s[l:r]",
                          "    return (h[r] - h[l] * pw[r - l]) % M"],
             "core_ids": []},
        ],
    },
    "number-theory": {
        "name": "Number Theory & Combinatorics",
        "signals": ["primes, divisors, gcd/lcm, modular arithmetic",
                    "“how many ways” with a closed form: C(n, k), stars and bars",
                    "answers “modulo 1e9+7”"],
        "one_liner": "A small toolkit does the work: sieve primes once, factorize by trial division up to sqrt(n), Euclid for gcd, and precomputed factorials with modular inverses for C(n, k).",
        "template": ["is_p = [True] * (n + 1)          # sieve of Eratosthenes",
                     "is_p[0] = is_p[1] = False",
                     "for i in range(2, int(n ** 0.5) + 1):",
                     "    if is_p[i]:",
                     "        for j in range(i * i, n + 1, i):",
                     "            is_p[j] = False"],
        "subtopics": [
            {"id": "number-theory", "name": "Primes, divisors, gcd",
             "recognize": "Primality, prime factors, count of divisors, gcd of an array, lcm.",
             "solve": "Sieve when many queries; trial division to sqrt(n) for one number; gcd(a, b) = gcd(b, a % b). Divisor counts come from the factorization: product of (exponent + 1).",
             "core_ids": []},
            {"id": "combinatorics", "name": "Counting with C(n, k)",
             "recognize": "Count arrangements, paths on a grid, ways to distribute identical items.",
             "solve": "Precompute fact[] and inv_fact[] mod p (Fermat inverse). Multiplication principle first, then subtract the forbidden cases (inclusion-exclusion).",
             "template": ["MOD = 10 ** 9 + 7",
                          "fact = [1] * (n + 1)",
                          "for i in range(1, n + 1):",
                          "    fact[i] = fact[i - 1] * i % MOD",
                          "inv = [1] * (n + 1)",
                          "inv[n] = pow(fact[n], MOD - 2, MOD)",
                          "for i in range(n, 0, -1):",
                          "    inv[i - 1] = inv[i] * i % MOD",
                          "def C(a, b):",
                          "    return fact[a] * inv[b] % MOD * inv[a - b] % MOD if 0 <= b <= a else 0"],
             "core_ids": []},
        ],
    },
    "fenwick-segment": {
        "name": "Fenwick & Segment Tree",
        "signals": ["point updates interleaved with prefix / range queries",
                    "“count smaller elements to the right”, inversions",
                    "range min / max / sum over an array that changes"],
        "one_liner": "Log-time range queries under updates. A Fenwick tree is ten lines and covers prefix sums and counting; a segment tree generalizes to any associative operation.",
        "template": ["tree = [0] * (n + 1)              # Fenwick, 1-indexed",
                     "def add(i, v):",
                     "    while i <= n:",
                     "        tree[i] += v",
                     "        i += i & -i",
                     "def prefix(i):                    # sum of a[1..i]",
                     "    s = 0",
                     "    while i > 0:",
                     "        s += tree[i]",
                     "        i -= i & -i",
                     "    return s"],
        "subtopics": [
            {"id": "fenwick", "name": "Fenwick tree (BIT)",
             "recognize": "Prefix sums with point updates; “how many earlier elements are smaller” (compress values, then count).",
             "solve": "i & -i walks the tree. Inversions: scan left to right, query how many seen values are larger, then insert.",
             "core_ids": []},
            {"id": "segment-tree", "name": "Segment tree",
             "recognize": "Range min/max/sum with point updates, or a query the Fenwick tree cannot express.",
             "solve": "Build over [l, r) recursively; query and update descend into the halves that overlap. Lazy propagation only when range updates are required.",
             "template": ["def build(o, l, r):",
                          "    if r - l == 1:",
                          "        t[o] = a[l]; return",
                          "    m = (l + r) // 2",
                          "    build(2 * o, l, m); build(2 * o + 1, m, r)",
                          "    t[o] = merge(t[2 * o], t[2 * o + 1])",
                          "def query(o, l, r, ql, qr):",
                          "    if ql <= l and r <= qr: return t[o]",
                          "    m = (l + r) // 2; res = IDENTITY",
                          "    if ql < m: res = merge(res, query(2 * o, l, m, ql, qr))",
                          "    if qr > m: res = merge(res, query(2 * o + 1, m, r, ql, qr))",
                          "    return res"],
             "core_ids": []},
        ],
    },
}

# ---------------------------------------------------------------------------
# 0x3F mapping. Chapter keys are the first number of a section ("§2.1.1" -> "2");
# section keys are the full numeric path ("2.1.1") or the raw name when a section
# has no number ("Part A", "Special Topic: Jump Game", "Other").
OX3F = {
    "Sliding Window & Two Pointers": {
        "default": "sliding-window",
        "chapters": {"1": "sliding-window/shape-1", "2": "sliding-window", "3": "two-pointers",
                     "4": "two-pointers/shape-3", "5": "two-pointers/shape-1",
                     "6": "arrays-hashing/string-scanning"},
        "sections": {"2.1.1": "sliding-window/shape-2", "2.1.2": "sliding-window/shape-2",
                     "2.2": "sliding-window/shape-3", "2.3.1": "sliding-window/shape-4",
                     "2.3.2": "sliding-window/shape-4", "2.3.3": "sliding-window/shape-4",
                     "3.1": "two-pointers/shape-1", "3.2": "two-pointers/shape-1",
                     "3.3": "two-pointers/shape-2a", "3.5": "two-pointers/shape-2a",
                     "4.2": "two-pointers/shape-2a"},
    },
    "Binary Search": {
        "default": "binary-search",
        "chapters": {"1": "binary-search/boundary", "2": "binary-search/answer",
                     "4": "binary-search/rotated-mountain"},
        "sections": {},
    },
    "Monotonic Stack": {
        "default": "stack",
        "chapters": {"1": "stack/monotonic", "2": "stack/monotonic", "3": "stack/monotonic",
                     "4": "stack/monotonic"},
        "sections": {},
    },
    "Grid Graph": {
        "default": "graphs",
        "chapters": {"1": "graphs/flood-fill", "2": "graphs/bfs", "5": "advanced-graphs/dijkstra"},
        "sections": {},
    },
    "Bit Manipulation": {
        "default": "math-bits",
        "chapters": {"1": "math-bits/bit-tricks", "2": "math-bits/bit-tricks",
                     "3": "math-bits/bit-contribution", "4": "math-bits/bit-contribution",
                     "5": "math-bits/bit-contribution", "8": "math-bits/bit-contribution",
                     "9": "math-bits/bit-tricks"},
        "sections": {},
    },
    "Graph Theory": {
        "default": "graphs",
        "chapters": {"1": "graphs/modeling-traversal", "2": "graphs/topo",
                     "3": "advanced-graphs/dijkstra", "4": "advanced-graphs/mst",
                     "7": "graphs/bfs", "9": "graphs"},
        "sections": {"1.3": "graphs/bfs"},
    },
    "Dynamic Programming": {
        "default": "dp-1d",
        "chapters": {"1": "dp-1d/linear", "2": "dp-2d/grid", "3": "dp-1d/knapsack",
                     "4": "dp-1d/subsequences", "5": "dp-1d/partition-decode",
                     "6": "dp-2d/state-machines", "7": "dp-1d", "8": "dp-2d/interval",
                     "9": "dp-2d/bitmask", "11": "dp-2d", "12": "trees/paths-tree-dp"},
        "sections": {"1.2": "dp-1d/take-or-skip", "1.3": "dp-1d/kadane",
                     "4.2.1": "dp-2d/two-sequences", "4.2.2": "dp-2d/two-sequences",
                     "7.1": "dp-1d/linear", "7.2": "intervals/sort-by-end", "7.3": "dp-1d/kadane",
                     "7.4": "dp-1d/subsequences", "7.5": "dp-2d/grid", "7.6": "dp-2d",
                     "7.7": "dp-1d/linear",
                     "Special Topic: Prefix-Suffix Decomposition": "arrays-hashing/prefix-sums",
                     "Special Topic: Jump Game": "greedy/jump-frontier",
                     "Special Topic: Reconstructing the Solution": "dp-1d",
                     "Other": "dp-1d"},
    },
    "Data Structures": {
        "default": "arrays-hashing",
        "chapters": {"0": "arrays-hashing/hash-basics", "1": "arrays-hashing/prefix-sums",
                     "2": "arrays-hashing/difference-arrays", "3": "stack/matching",
                     "4": "stack/design", "5": "heap/top-k", "6": "tries/build-query",
                     "7": "graphs/union-find", "8": "fenwick-segment/fenwick"},
        "sections": {"0.3": "math-bits/matrix", "3.5": "stack/expression",
                     "4.4": "sliding-window/shape-1", "5.4": "heap/scheduling",
                     "5.6": "heap/scheduling", "5.7": "heap/two-heaps",
                     "6.4": "tries/wildcards-board", "8.3": "fenwick-segment/segment-tree",
                     "Part A": "arrays-hashing/string-scanning",
                     "Part B": "linked-list/design-copying"},
    },
    "Math": {
        "default": "math-bits",
        "chapters": {"1": "number-theory/number-theory", "2": "number-theory/combinatorics",
                     "5": "math-bits/geometry-counting", "6": "math-bits/randomized",
                     "7": "math-bits/numbers-digits"},
        "sections": {"7.2": "number-theory/number-theory", "7.7": "arrays-hashing/grouping-counting"},
    },
    "Greedy & Thinking": {
        "default": "greedy",
        "chapters": {"1": "greedy/exchange-arguments", "2": "intervals/sort-by-end",
                     "3": "greedy/exchange-arguments", "4": "greedy/exchange-arguments",
                     "5": "insight/thinking", "7": "binary-search/answer", "8": "insight/thinking"},
        "sections": {"1.5": "greedy/partition-last-occurrence", "1.8": "heap/scheduling",
                     "1.9": "heap/scheduling", "2.2": "intervals/sweep-heap",
                     "2.5": "intervals/merge-insert", "2.6": "intervals/sweep-heap",
                     "3.1": "stack/monotonic", "3.2": "two-pointers/shape-1"},
    },
    "Linked List, Tree & Backtracking": {
        "default": "linked-list",
        "chapters": {"1": "linked-list/dummy-head-deletion", "2": "trees",
                     "3": "trees/paths-tree-dp", "4": "backtracking/subsets-combos",
                     "5": "linked-list/merging-divide"},
        "sections": {"1.4": "linked-list/reversal", "1.6": "linked-list/fast-slow",
                     "1.7": "linked-list/fast-slow", "1.8": "linked-list/merging-divide",
                     "1.9": "linked-list/merging-divide", "1.10": "linked-list/design-copying",
                     "1.11": "linked-list/design-copying",
                     "2.1": "trees/traversal", "2.15": "trees/traversal",
                     "2.2": "trees/top-down", "2.7": "trees/top-down",
                     "2.3": "trees/bottom-up", "2.4": "trees/bottom-up", "2.5": "trees/bottom-up",
                     "2.6": "trees/paths-tree-dp", "2.8": "trees/paths-tree-dp",
                     "2.12": "trees/paths-tree-dp", "2.9": "trees/bst",
                     "2.10": "trees/build-transform", "2.11": "trees/build-transform",
                     "2.14": "trees/build-transform", "2.13": "trees/bfs",
                     "3.6": "graphs/topo", "3.13": "trees",
                     "4.3": "backtracking/partition", "4.5": "backtracking/permutations-boards",
                     "4.7": "backtracking/pruning"},
    },
    "Strings": {
        "default": "strings",
        "chapters": {"1": "strings/kmp", "4": "strings/rolling-hash", "10": "strings"},
        "sections": {},
    },
}
# Interview-tier sections that are contest-flavoured in practice; hidden unless
# the user turns on optional subtopics (same toggle as 0x3F's "(optional)").
HIDDEN = ["Data Structures||1.3", "Data Structures||1.4", "Data Structures||3.6",
          "Data Structures||5.5", "Data Structures||Part C"]

# ---------------------------------------------------------------------------
STR = r'"((?:[^"\\]|\\.)*)"'
ENTRY = re.compile(
    r"\{\s*name:\s*" + STR + r",\s*recognize:\s*" + STR + r",\s*solve:\s*" + STR +
    r",\s*(?:tmpl:\s*`([^`]*)`,\s*)?ids:\s*\[([^\]]*)\]\s*\}", re.S)
PBLOCK = re.compile(r'^    "([^"]+)": \[\n(.*?)^    \],', re.S | re.M)
GPATTERN = re.compile(
    r'"([^"]+)": \{\s*signals:\s*\[(.*?)\],\s*intro:\s*' + STR + r",\s*tmpl:\s*`([^`]*)`,\s*\}", re.S)
GTOPIC = re.compile(r'"([^"]+)": \{\s*zh:\s*"([^"]*)",\s*post:\s*"([^"]*)",')


def unesc(s):
    return s.replace('\\"', '"')


def lines(tmpl):
    return tmpl.split("\n") if tmpl else None


def strip_num(name):
    return re.sub(r"^\d+\.\s*", "", name)


def extract_curriculum():
    text = (STATIC / "curriculum.js").read_text(encoding="utf-8")
    out = {}
    for m in PBLOCK.finditer(text):
        subs = []
        for e in ENTRY.finditer(m.group(2)):
            subs.append({"name": strip_num(unesc(e.group(1))), "recognize": unesc(e.group(2)),
                         "solve": unesc(e.group(3)), "template": lines(e.group(4)),
                         "ids": [int(x) for x in re.findall(r"\d+", e.group(5))]})
        out[m.group(1)] = subs
    return out


def extract_guide():
    text = (STATIC / "guide.js").read_text(encoding="utf-8")
    cut = text.index("const PATTERNS = {")
    topics = {m.group(1): {"zh": m.group(2), "post": m.group(3)} for m in GTOPIC.finditer(text[:cut])}
    pats = {}
    for m in GPATTERN.finditer(text[cut:]):
        signals = [unesc(s) for s in re.findall(STR, m.group(2))]
        pats[m.group(1)] = {"signals": signals, "intro": unesc(m.group(3)), "template": lines(m.group(4))}
    return topics, pats


def curate(pid, subs):
    """Hand edits on top of the legacy curriculum, kept here so the draft is reproducible."""
    if pid == "graphs":
        uf = next(s for s in subs if s["id"] == "union-find")
        uf.update({
            "name": "Union-Find",
            "recognize": "“Merge accounts / components”, “which edge creates a cycle”, connectivity as edges arrive.",
            "solve": "DSU with path compression: find(x) follows parents; union attaches one root under the other. Count components by counting roots.",
            "core_ids": [684, 721, 953],
        })
        subs.insert(subs.index(uf), {
            "id": "modeling-traversal", "name": "Graph modeling & traversal",
            "recognize": "The graph is implicit: clone a graph, ratio queries along paths (evaluate division), degree puzzles (town judge).",
            "solve": "Build the adjacency list first, then plain DFS/BFS. Some “graph” problems are only degree counting.",
            "template": ["g = defaultdict(list)", "for u, v in edges:", "    g[u].append(v); g[v].append(u)",
                         "vis = set()", "def dfs(u):", "    vis.add(u)", "    for v in g[u]:",
                         "        if v not in vis:", "            dfs(v)"],
            "core_ids": [133, 399, 997],
        })
    if pid == "dp-1d":
        k = next(s for s in subs if s["id"] == "knapsack")
        k.update({
            "name": "Knapsack",
            "recognize": "“Fewest coins / perfect squares to build n”, “split into two equal halves”, “ways to hit a target with +/− signs”. Items combined under a capacity.",
            "solve": "0-1 knapsack: loop capacity DOWNWARD (each item once). Unbounded (coins): loop capacity upward. Counting uses +=. Target Sum reduces to subset-sum via (total + target) / 2.",
            "core_ids": [279, 322, 343, 416, 494, 518, 1049],
        })
    if pid == "dp-2d":
        subs[:] = [s for s in subs if s["id"] != "knapsack"]
        subs.append({
            "id": "bitmask", "name": "Bitmask DP",
            "recognize": "n ≤ ~20 and the state is “which elements are used”.",
            "solve": "f[mask] = best over the last element added; iterate masks upward, transitions flip one bit.",
            "template": ["f = [INF] * (1 << n)", "f[0] = 0", "for mask in range(1 << n):",
                         "    for i in range(n):", "        if mask >> i & 1:",
                         "            f[mask] = min(f[mask], f[mask ^ (1 << i)] + cost(mask, i))"],
            "core_ids": [],
        })
    if pid == "advanced-graphs":
        d = next(s for s in subs if s["id"] == "dijkstra")
        d["name"] = "Dijkstra, Floyd & minimax paths"
    if pid == "stack":
        next(s for s in subs if s["id"] == "design")["name"] = "Stack & queue design"
    if pid == "arrays-hashing":
        next(s for s in subs if s["id"] == "string-scanning")["name"] = "String scanning & run grouping"
        pre = next(i for i, s in enumerate(subs) if s["id"] == "prefix-sums")
        subs.insert(pre + 1, {
            "id": "difference-arrays", "name": "Difference arrays",
            "recognize": "Many range updates (+v on [l, r]), one final read of the whole array.",
            "solve": "d[l] += v and d[r+1] -= v per update; a prefix sum over d recovers the values. Car pooling and flight bookings are this.",
            "template": ["d = [0] * (n + 1)", "for l, r, v in updates:", "    d[l] += v",
                         "    d[r + 1] -= v", "a = list(accumulate(d))[:n]"],
            "core_ids": [],
        })
    if pid == "math-bits":
        bt = next(i for i, s in enumerate(subs) if s["id"] == "bit-tricks")
        subs.insert(bt + 1, {
            "id": "bit-contribution", "name": "Bit by bit",
            "recognize": "Sums over pairs of AND/OR/XOR, “maximum XOR”, constraints on which bits can be set.",
            "solve": "Bits are independent: count how many numbers have bit b set and add its contribution separately. Maximum XOR builds the answer from the top bit down with a set or a trie.",
            "template": ["ans = 0", "for b in range(31):", "    ones = sum(x >> b & 1 for x in a)",
                         "    ans += (1 << b) * ones * (n - ones)   # pairs whose XOR has bit b"],
            "core_ids": [],
        })
        subs.append({
            "id": "randomized", "name": "Randomized algorithms",
            "recognize": "“Pick uniformly at random” from a stream or by weight, shuffle in place.",
            "solve": "Fisher-Yates shuffle; reservoir sampling keeps item i with probability 1/i; weighted pick = prefix sums + binary search.",
            "core_ids": [],
        })
    return subs


def main():
    cur = extract_curriculum()
    topics, gpats = extract_guide()
    tutorials = json.loads(TUTORIALS.read_text(encoding="utf-8"))["tutorials"] if TUTORIALS.exists() else {}
    problems = json.loads(PROBLEMS.read_text(encoding="utf-8"))["problems"]

    patterns = {}
    for legacy, pid in PATTERN_IDS:
        g = gpats[legacy]
        entry = {"name": legacy, "tutorial": TUTORIAL_FILES.get(pid),
                 "signals": g["signals"], "one_liner": g["intro"],
                 "template": g["template"], "legacy_patternOf": [legacy]}
        if pid in TUTORIAL_FILES:
            # The tutorial's shapes are the subtopics; the legacy ids are kept only
            # so build_tutorials.py can report problems the tutorial does not list.
            entry["legacy_core_ids"] = [i for s in cur[legacy] for i in s["ids"]]
            t = tutorials.get(pid)
            if t and t.get("template"):
                entry["template"] = None      # tutorials.json provides it
        else:
            subs = []
            for s in cur[legacy]:
                rec = {"id": SUBTOPIC_IDS[(pid, s["name"])], "name": s["name"],
                       "recognize": s["recognize"], "solve": s["solve"]}
                if s["template"]:
                    rec["template"] = s["template"]
                rec["core_ids"] = s["ids"]
                subs.append(rec)
            entry["subtopics"] = curate(pid, subs)
        patterns[pid] = entry

    for pid, adv in ADVANCED.items():
        patterns[pid] = {"name": adv["name"], "tutorial": None, "signals": adv["signals"],
                         "one_liner": adv["one_liner"], "template": adv["template"],
                         "legacy_patternOf": [], "subtopics": adv["subtopics"]}

    order = [pid for _, pid in PATTERN_IDS] + list(ADVANCED)

    ox = {"topics": {}, "chapters": {}, "sections": {}, "hidden": HIDDEN}
    for topic, spec in OX3F.items():
        ox["topics"][topic] = {"zh": topics[topic]["zh"], "post": topics[topic]["post"],
                               "default": spec["default"]}
        ox["chapters"][topic] = spec["chapters"]
        for k, v in spec["sections"].items():
            ox["sections"][f"{topic}||{k}"] = v

    data = {"order": order, "patterns": patterns, "ox3f": ox}
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)}: {len(order)} patterns, "
          f"{sum(len(p.get('subtopics', [])) for p in patterns.values())} subtopics")
    report(data, problems)


def sec_key(section):
    m = re.search(r"(\d+(?:\.\d+)*)", section)
    return m.group(1) if m else section


def resolve(data, topic, section):
    ox = data["ox3f"]
    key = sec_key(section)
    t = ox["sections"].get(f"{topic}||{key}")
    if t:
        return t, "section"
    t = ox["chapters"].get(topic, {}).get(key.split(".")[0])
    if t:
        return t, "chapter"
    return ox["topics"][topic]["default"], "default"


def report(data, problems):
    """Print the sections that resolve only through the topic default (curation
    candidates) and the section keys named in the mapping that do not exist."""
    present = {}
    for p in problems.values():
        for m in p["lists"].get("ox3f", []):
            if m["tier"] == "interview":
                present.setdefault((m["topic"], sec_key(m["section"])), m["section"])
    for k in data["ox3f"]["sections"]:
        topic, key = k.split("||", 1)
        if (topic, key) not in present:
            print(f"  unknown section key: {k}")
    for topic, chaps in data["ox3f"]["chapters"].items():
        have = {key.split(".")[0] for (t, key) in present if t == topic}
        for c in chaps:
            if c not in have:
                print(f"  unknown chapter: {topic}||{c}")
    via_default = [(t, s) for (t, k), s in present.items() if resolve(data, t, s)[1] == "default"]
    if via_default:
        print("  resolve only via topic default:")
        for t, s in sorted(via_default):
            print(f"    {t} :: {s}")


if __name__ == "__main__":
    main()
