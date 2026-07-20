/* Chapter guide for the 12 0x3F (灵茶山艾府 / EndlessCheng) topic lists: a short
 * intro + code template per chapter, shown in the study route when a subtopic is
 * selected. Chapter names/numbers mirror his lists (source/ox3F); `post` links go
 * to his original leetcode.cn posts. Templates paraphrase his well-known patterns
 * in compact Python. Only interview-tier chapters that actually carry problems in
 * data/problems.json need entries. Pure data, no DOM — loadable from node.
 */
(function (global) {
  "use strict";

  const G = {
    "Sliding Window & Two Pointers": {
      zh: "滑动窗口与双指针",
      post: "https://leetcode.cn/discuss/post/0viNMK/",
      chapters: {
        1: { name: "Fixed-Length Sliding Window", zh: "定长滑动窗口",
          intro: "The window size k is given. Maintain window stats incrementally with 0x3F's add / update / remove rhythm — never recompute a window from scratch.",
          tmpl: `# one pass, O(n): add -> (window full?) update -> remove
for i, x in enumerate(a):
    # 1. add a[i] into the window stats
    if i < k - 1:
        continue            # window not full yet
    # 2. update the answer with the current window
    # 3. remove a[i - k + 1] from the window stats` },
        2: { name: "Variable-Length Sliding Window", zh: "不定长滑动窗口",
          intro: "Grow the right end one step at a time; shrink from the left while the window is broken (for longest) or while it is still valid (for shortest / counting). Needs monotonicity: extending the window only pushes it one way. Count \"exactly k\" via atMost(k) - atMost(k-1).",
          tmpl: `l = 0
for r, x in enumerate(a):
    add(x)
    while window_broken():      # longest: shrink only when broken
        remove(a[l]); l += 1
    ans = max(ans, r - l + 1)   # counting: ans += r - l + 1` },
        3: { name: "Two Pointers on One Sequence", zh: "单序列双指针",
          intro: "Opposite-direction: start at both ends of a sorted array and move the pointer that improves the sum (two-sum II, container with most water). Same-direction slow/fast: overwrite in place, find middles, detect cycles. Each pointer moves O(n) in total.",
          tmpl: `l, r = 0, len(a) - 1        # opposite-direction
while l < r:
    s = a[l] + a[r]
    if s == target: ...
    elif s < target: l += 1
    else: r -= 1` },
        4: { name: "Two Pointers on Two Sequences", zh: "双序列双指针",
          intro: "One pointer per sequence, always advancing the one that lags: merge two sorted arrays, check whether s is a subsequence of t.",
          tmpl: `i = j = 0                    # is s a subsequence of t?
while i < len(s) and j < len(t):
    if s[i] == t[j]:
        i += 1
    j += 1
ok = (i == len(s))` },
        5: { name: "Three Pointers", zh: "三指针",
          intro: "3-sum style: sort, fix one index, then run opposite-direction two pointers on the rest; or three synchronized scan pointers over one array." },
        6: { name: "Group-by-Group Iteration", zh: "分组循环",
          intro: "The array splits into maximal runs sharing a property (equal values, increasing, same parity). Outer loop marks a run's start, inner loop extends it to the end; still O(n) overall and no off-by-one soup.",
          tmpl: `i, n = 0, len(a)
while i < n:
    st = i
    i += 1
    while i < n and same_run(i - 1, i):
        i += 1
    # a[st:i] is one maximal run` },
      },
    },

    "Binary Search": {
      zh: "二分算法",
      post: "https://leetcode.cn/discuss/post/SqopEo/",
      chapters: {
        1: { name: "Binary Search on Arrays", zh: "二分查找",
          intro: "Everything reduces to lower_bound: the first index with a[i] >= x in a sorted array. \"> x\" is \">= x+1\"; \"last < x\" is lower_bound minus one. Keep one invariant (half-open interval) and the edge cases solve themselves.",
          tmpl: `# first i with a[i] >= x  (bisect_left)
lo, hi = 0, len(a)          # answer lives in [lo, hi]
while lo < hi:
    mid = (lo + hi) // 2
    if a[mid] >= x:
        hi = mid
    else:
        lo = mid + 1
# lo = the answer (len(a) if no such i)` },
        2: { name: "Binary Search on the Answer", zh: "二分答案",
          intro: "When \"is answer m feasible?\" is monotone in m, binary search m itself and write a greedy check(m). One template covers minimize / maximize, minimize-the-maximum, maximize-the-minimum, and k-th smallest (count how many values <= m).",
          tmpl: `lo, hi = min_ans, max_ans    # minimizing the answer
while lo < hi:
    mid = (lo + hi) // 2
    if check(mid):           # feasible -> try smaller
        hi = mid
    else:
        lo = mid + 1` },
        4: { name: "Other", zh: "其他",
          intro: "Binary search in disguise: rotated sorted arrays, peak finding, searching on an index transform rather than raw values." },
      },
    },

    "Monotonic Stack": {
      zh: "单调栈",
      post: "https://leetcode.cn/discuss/post/9oZFK9/",
      chapters: {
        1: { name: "Monotonic Stack", zh: "单调栈",
          intro: "Answers \"next/previous greater (or smaller) element\" for every index in O(n): the stack keeps indices whose values stay monotone; each index is pushed and popped at most once.",
          tmpl: `st = []                      # indices, values decreasing
for i, x in enumerate(a):
    while st and a[st[-1]] < x:
        nxt[st.pop()] = i    # x is the next greater
    st.append(i)` },
        2: { name: "Rectangles", zh: "矩形",
          intro: "Largest rectangle in a histogram: each bar's rectangle extends to its previous/next smaller bar (one monotonic-stack pass). Matrix versions build a histogram per row and reuse it." },
        3: { name: "Contribution Technique", zh: "贡献法",
          intro: "Sum of subarray minimums: instead of enumerating subarrays, count how many subarrays each a[i] dominates — (i - prev_smaller) * (next_smaller - i) — and sum contributions." },
        4: { name: "Lexicographically Smallest", zh: "最小字典序",
          intro: "Build the answer as a stack: pop while the top is worse than the incoming char and you can still afford to drop it (remove k digits, remove duplicate letters)." },
      },
    },

    "Grid Graph": {
      zh: "网格图",
      post: "https://leetcode.cn/discuss/post/YiXPXW/",
      chapters: {
        1: { name: "Grid DFS", zh: "网格图 DFS",
          intro: "Flood-fill connected cells (islands, regions): recurse in 4 directions, mark visited by overwriting the cell so no extra visited set is needed.",
          tmpl: `def dfs(i, j):
    if not (0 <= i < m and 0 <= j < n) or grid[i][j] != LAND:
        return 0
    grid[i][j] = SEEN
    return 1 + sum(dfs(i + di, j + dj)
                   for di, dj in ((1,0),(-1,0),(0,1),(0,-1)))` },
        2: { name: "Grid BFS", zh: "网格图 BFS",
          intro: "Shortest paths / simultaneous spreading in unweighted grids. Process the queue one layer at a time (layer = distance); multi-source BFS just enqueues every source first (rotting oranges, 01-matrix).",
          tmpl: `q = deque(sources); d = 0
while q:
    for _ in range(len(q)):  # one layer = one distance
        i, j = q.popleft()
        for ni, nj in nbrs(i, j):
            if fresh(ni, nj):
                mark(ni, nj); q.append((ni, nj))
    d += 1` },
        5: { name: "Comprehensive Applications", zh: "综合应用",
          intro: "Grid search combined with something else: binary search on the answer, a heap (swim in rising water), union-find, or extra state such as keys carried." },
      },
    },

    "Bit Manipulation": {
      zh: "位运算",
      post: "https://leetcode.cn/discuss/post/dHn9Vk/",
      chapters: {
        1: { name: "Basics", zh: "基础题",
          intro: "Single-number tricks: x & (x-1) clears the lowest set bit (power-of-two test, popcount loop); x & -x isolates it; shifts multiply/divide by 2." },
        2: { name: "Properties of XOR", zh: "异或的性质",
          intro: "a ^ a = 0 and a ^ 0 = a, so pairs cancel: find the single number, missing number. Prefix XOR turns any range XOR into two prefix values." },
        3: { name: "Properties of AND/OR", zh: "与或的性质",
          intro: "Extending a subarray can only clear bits under AND and only set bits under OR — so each right endpoint sees at most O(log U) distinct AND/OR values, and feasibility is monotone." },
        4: { name: "Bit-by-Bit / Contribution", zh: "拆位 / 贡献法",
          intro: "Bits are independent: for each bit position, count how many numbers (or pairs) have it set and add its contribution to the total separately." },
        5: { name: "Greedy Bit Filling", zh: "试填法",
          intro: "Construct the answer from the highest bit down: tentatively set the bit, check if some choice still achieves it (often with a hash set or trie, as in maximum XOR of two numbers), keep it if so." },
        8: { name: "Insight Problems", zh: "思维题",
          intro: "Puzzles where the key is an invariant of the bitwise operation — parity of set bits, what XOR of everything preserves, bounds that AND/OR cannot escape." },
        9: { name: "Other", zh: "其他",
          intro: "Everything else bitwise: simulating arithmetic with logic ops, bit tricks inside other algorithms." },
      },
    },

    "Graph Theory": {
      zh: "图论算法",
      post: "https://leetcode.cn/discuss/post/01LUak/",
      chapters: {
        1: { name: "Graph Traversal", zh: "图的遍历",
          intro: "Build an adjacency list, then DFS/BFS for connected components, reachability, and cycle detection. This chapter also covers 基环树 (a cycle with trees hanging off it) from his taxonomy.",
          tmpl: `g = defaultdict(list)
for u, v in edges:
    g[u].append(v); g[v].append(u)
vis = set()
def dfs(u):
    vis.add(u)
    for v in g[u]:
        if v not in vis:
            dfs(v)` },
        2: { name: "Topological Sort", zh: "拓扑排序",
          intro: "Order a DAG so every edge points forward (course schedule). Kahn's algorithm repeatedly removes 0-indegree nodes; if the order ends up shorter than n, there is a cycle.",
          tmpl: `q = deque(u for u in range(n) if indeg[u] == 0)
order = []
while q:
    u = q.popleft(); order.append(u)
    for v in g[u]:
        indeg[v] -= 1
        if indeg[v] == 0:
            q.append(v)
# cycle iff len(order) < n` },
        3: { name: "Shortest Paths", zh: "最短路",
          intro: "Unweighted: plain BFS. Non-negative weights: Dijkstra with a lazy-deletion heap. Dense/small graphs or all-pairs: Floyd. Negative edges (rare in interviews): Bellman-Ford.",
          tmpl: `dist = [inf] * n; dist[s] = 0
h = [(0, s)]
while h:
    d, u = heappop(h)
    if d > dist[u]:
        continue             # stale entry
    for v, w in g[u]:
        if d + w < dist[v]:
            dist[v] = d + w
            heappush(h, (dist[v], v))` },
        4: { name: "Minimum Spanning Tree", zh: "最小生成树",
          intro: "Connect all nodes at minimum total cost. Kruskal: sort edges, take one whenever it links two different components (union-find). Prim: grow one tree with a heap." },
        7: { name: "Bipartite Graph Coloring", zh: "二分图染色",
          intro: "2-color the graph with BFS/DFS, giving neighbors opposite colors; a conflict means an odd cycle, so bipartition is impossible (possible bipartition, is graph bipartite)." },
        9: { name: "Other", zh: "其他",
          intro: "Graph modeling odds and ends: cloning a graph, safe states via reverse topological sort, converting implicit relations into edges." },
      },
    },

    "Dynamic Programming": {
      zh: "动态规划",
      post: "https://leetcode.cn/discuss/post/tXLS3i/",
      chapters: {
        1: { name: "Introductory DP", zh: "入门 DP",
          intro: "From memoized recursion to bottom-up arrays: climbing stairs (f[i] = f[i-1] + f[i-2]), house robber (rob or skip), maximum subarray. State = answer for a prefix; write the recurrence, then flatten.",
          tmpl: `f = [0] * (n + 1)            # climbing stairs
f[0] = f[1] = 1
for i in range(2, n + 1):
    f[i] = f[i - 1] + f[i - 2]` },
        2: { name: "Grid DP", zh: "网格图 DP",
          intro: "f[i][j] depends on the cell above and the cell to the left: unique paths, minimum path sum, triangle. Often compressible to one row." },
        3: { name: "Knapsack", zh: "背包",
          intro: "0-1 knapsack (each item once): iterate capacity downward. Unbounded (items reusable): iterate upward. Subset sum, target sum and coin change are knapsacks in disguise.",
          tmpl: `for w, v in items:           # 0-1: capacity goes DOWN
    for c in range(C, w - 1, -1):
        f[c] = max(f[c], f[c - w] + v)
# unbounded: for c in range(w, C + 1)  (upward)` },
        4: { name: "Classic Linear DP", zh: "经典线性 DP",
          intro: "The two classics: LCS-family on two sequences (f[i][j] over prefix pairs — edit distance included) and LIS (patience sorting: keep the smallest possible tail for each length, binary search insert).",
          tmpl: `g = []                       # LIS, O(n log n)
for x in a:
    i = bisect_left(g, x)
    if i == len(g): g.append(x)
    else: g[i] = x
# len(g) = LIS length` },
        5: { name: "Partition DP", zh: "划分型 DP",
          intro: "Cut the array into pieces: f[i] = best over all last-piece starts j of f[j] + cost(j, i). Word break, palindrome partitioning, and the feasibility / count-constrained variants." },
        6: { name: "State Machine DP", zh: "状态机 DP",
          intro: "A small automaton per position: holding / not holding for stock problems (with cooldown or fee as extra states), taken / skipped. Draw the states, write one transition per arrow." },
        7: { name: "Other Linear DP", zh: "其他线性 DP",
          intro: "One-dimensional scans with a custom transition — the biggest grab-bag chapter: longest arithmetic chains, DP over digits of positions, DP with hash maps." },
        8: { name: "Interval DP", zh: "区间 DP",
          intro: "f[l][r] built from strictly smaller intervals: iterate by length (burst balloons, longest palindromic subsequence, merging stones).",
          tmpl: `for length in range(2, n + 1):
    for l in range(n - length + 1):
        r = l + length - 1
        f[l][r] = best(f[l][k], f[k + 1][r], ...)` },
        9: { name: "Bitmask DP", zh: "状压 DP",
          intro: "n <= ~20: a subset fits in an int. f[mask] = best over the last element added; iterate all masks upward, transitions flip one bit. Assignment and TSP-style problems." },
        11: { name: "DP Optimizations", zh: "优化 DP",
          intro: "The transition, not the state, is the bottleneck: replace inner loops with a running prefix max/min, a monotonic queue, or a Fenwick/segment tree lookup." },
        12: { name: "Tree DP", zh: "树形 DP",
          intro: "Post-order DFS combines children's answers: house robber III (rob/skip per node), tree diameter. Rerooting technique extends one answer to every root." },
        "Special Topic: Reconstructing the Solution": {
          name: "Reconstructing the Solution", zh: "输出具体方案",
          intro: "Store, for each state, which choice achieved the optimum (or re-derive it by checking which transition matches), then walk backwards from the final state to print the actual plan." },
        "Special Topic: Prefix-Suffix Decomposition": {
          name: "Prefix-Suffix Decomposition", zh: "前后缀分解",
          intro: "Precompute an answer for every prefix and every suffix, then combine at each split point: trapping rain water (max-left / max-right), product of array except self. Turns a nested loop into three linear passes." },
        "Special Topic: Jump Game": { name: "Jump Game", zh: "跳跃游戏",
          intro: "Reach/coverage problems: greedily maintain the furthest reachable index (or BFS by layers of reach). DP view: can-reach is a rolling reachability bound." },
        "Other": { name: "Other DP", zh: "其他",
          intro: "DP that fits no earlier chapter — unusual states or transitions." },
      },
    },

    "Data Structures": {
      zh: "常用数据结构",
      post: "https://leetcode.cn/discuss/post/mOr1u6/",
      chapters: {
        0: { name: "Enumerate Right, Maintain Left", zh: "常用枚举技巧",
          intro: "Two-sum pattern: enumerate the RIGHT element of a pair and keep a hash map summarizing everything to its left (values seen, counts, best-so-far). One pass, O(n).",
          tmpl: `seen = {}
for j, x in enumerate(a):    # x = right element
    if target - x in seen:
        ...                  # pair (seen[target-x], j)
    seen[x] = j              # x joins the "left" side` },
        1: { name: "Prefix Sums", zh: "前缀和",
          intro: "s[i+1] = s[i] + a[i]; any subarray sum is s[r+1] - s[l]. Combined with a hash map of seen prefix values, it counts subarrays with sum k in one pass.",
          tmpl: `cnt = {0: 1}
s = ans = 0
for x in a:                  # subarrays summing to k
    s += x
    ans += cnt.get(s - k, 0)
    cnt[s] = cnt.get(s, 0) + 1` },
        2: { name: "Difference Arrays", zh: "差分",
          intro: "Many range updates, one final read: d[l] += v and d[r+1] -= v per update, then prefix-sum d to recover the values (corporate flight bookings, car pooling)." },
        3: { name: "Stack", zh: "栈",
          intro: "LIFO: bracket matching, adjacent-pair elimination (remove all adjacent duplicates), undo semantics, and expression parsing with a number stack + operator stack." },
        4: { name: "Queue", zh: "队列",
          intro: "FIFO and deques. Star pattern: sliding-window maximum with a monotonic deque — front holds the current max's index, back pops smaller elements before pushing." },
        5: { name: "Heap (Priority Queue)", zh: "堆",
          intro: "Always pop the best: top-k, merge k sorted lists, scheduling/simulation. Two heaps maintain a running median; lazy deletion postpones removals until they surface at the top." },
        6: { name: "Trie", zh: "字典树",
          intro: "A tree keyed by characters: shared prefixes stored once. Word dictionaries, autocomplete, and — on bits — maximum XOR of two numbers." },
        7: { name: "Union-Find (DSU)", zh: "并查集",
          intro: "Merge sets and query \"same set?\" in near-O(1): connectivity as edges arrive, accounts merge, counting components without building explicit graphs.",
          tmpl: `fa = list(range(n))
def find(x):
    while fa[x] != x:
        fa[x] = fa[fa[x]]    # path halving
        x = fa[x]
    return x
def union(a, b):
    fa[find(a)] = find(b)` },
        8: { name: "Fenwick Tree & Segment Tree", zh: "树状数组和线段树",
          intro: "Point update + prefix/range query in O(log n). Fenwick (BIT) is 10 lines and counts inversions; a segment tree generalizes to range min/max/sum and lazy range updates." },
      },
    },

    "Math": {
      zh: "数学算法",
      post: "https://leetcode.cn/discuss/post/IYT3ss/",
      chapters: {
        1: { name: "Number Theory", zh: "数论",
          intro: "gcd/lcm (Euclid), primality, the sieve of Eratosthenes, factorization, and modular arithmetic — the recurring toolkit behind count-primes and ugly-number problems.",
          tmpl: `is_p = [True] * n            # sieve of Eratosthenes
is_p[0] = is_p[1] = False
for i in range(2, int(n ** 0.5) + 1):
    if is_p[i]:
        for j in range(i * i, n, i):
            is_p[j] = False` },
        2: { name: "Combinatorics", zh: "组合数学",
          intro: "Counting with C(n, k): precompute factorials and inverse factorials mod p, then multiply. Stars-and-bars, path counting, inclusion-exclusion basics." },
        5: { name: "Computational Geometry", zh: "计算几何",
          intro: "Points and vectors: cross products give orientation (left/right turn), dot products give angles; distances and simple intersections." },
        6: { name: "Randomized Algorithms", zh: "随机算法",
          intro: "Fisher-Yates shuffle, reservoir sampling for streams, weighted random pick via prefix sums + binary search." },
        7: { name: "Miscellaneous", zh: "杂项",
          intro: "Everything else mathematical: digit manipulation, bases, simulate-the-formula problems." },
      },
    },

    "Greedy & Thinking": {
      zh: "贪心与思维",
      post: "https://leetcode.cn/discuss/post/g6KTKL/",
      chapters: {
        1: { name: "Greedy Strategies", zh: "贪心策略",
          intro: "Sort, then take the locally best choice — and justify it with an exchange argument (\"swapping any other choice never improves the answer\"). Includes 反悔贪心 (regret greedy: commit, but keep a heap to undo the worst commitment)." },
        2: { name: "Interval Greedy", zh: "区间贪心",
          intro: "Sort intervals by END for max non-overlapping count / min arrows; sort by START for merging overlaps. Choosing the earliest-ending compatible interval is never wrong." },
        3: { name: "String Greedy", zh: "字符串贪心",
          intro: "Build lexicographically-best strings: compare candidate characters (often with a stack), match from both ends, prefer the choice that keeps the most freedom later." },
        4: { name: "Math Greedy", zh: "数学贪心",
          intro: "Greedy justified by arithmetic: the median minimizes sum of absolute distances, pairing largest with smallest, parity arguments." },
        5: { name: "Insight Problems", zh: "思维题",
          intro: "One observation collapses the problem: an invariant that never changes, a bound that must be tight, symmetry, or looking only at extremes. (0x3F's 脑筋急转弯 category lives here.)" },
        7: { name: "Interactive Problems", zh: "交互题",
          intro: "You query an API instead of reading input (guess number higher or lower): usually binary search or careful state elimination against the judge." },
        8: { name: "Other", zh: "其他",
          intro: "Constructive and ad-hoc problems: build any valid arrangement satisfying constraints." },
      },
    },

    "Linked List, Tree & Backtracking": {
      zh: "链表、树与回溯",
      post: "https://leetcode.cn/discuss/post/K0n2gO/",
      chapters: {
        1: { name: "Linked List", zh: "链表",
          intro: "Dummy head + prev/curr pointers make splicing safe (0x3F's 前后指针); slow/fast pointers (快慢指针) find the middle and detect cycles; in-place reversal is the core micro-skill.",
          tmpl: `pre, cur = None, head        # reverse a linked list
while cur:
    nxt = cur.next
    cur.next = pre
    pre, cur = cur, nxt
return pre` },
        2: { name: "Binary Tree", zh: "二叉树",
          intro: "Two recursion styles: top-down (pass state as parameters — path sums) and bottom-up (return info from subtrees — depth, diameter, LCA). BST bonus: inorder traversal is sorted. BFS handles level-order and views.",
          tmpl: `def dfs(node):               # bottom-up skeleton
    if not node:
        return BASE
    left = dfs(node.left)
    right = dfs(node.right)
    update answer with (left, right, node)
    return combine(left, right, node)` },
        3: { name: "General Trees", zh: "一般树",
          intro: "N-ary trees and trees given as edge/parent arrays: build children lists, DFS with a parent argument instead of a visited set, diameters via two passes or per-node top-two depths." },
        4: { name: "Backtracking", zh: "回溯",
          intro: "Choose, recurse, un-choose over a decision tree: subsets (pick/skip each element), combinations (start index prevents reuse), permutations (used set), N-queens style constraint search. Prune as early as possible.",
          tmpl: `def dfs(i, path):
    if complete(i):
        ans.append(path[:])
        return
    for c in choices(i):
        path.append(c)
        dfs(i + 1, path)
        path.pop()           # undo = backtrack` },
        5: { name: "Recursion / Divide & Conquer", zh: "其他递归/分治",
          intro: "Split, solve halves, merge: sort a linked list, count inversions with merge sort, quickselect for the k-th element in O(n) average." },
      },
    },

    "Strings": {
      zh: "字符串",
      post: "https://leetcode.cn/discuss/post/SJFwQI/",
      chapters: {
        1: { name: "KMP", zh: "KMP（前缀的后缀）",
          intro: "The failure function pi[i] = length of the longest proper border (prefix that is also a suffix) of the prefix ending at i. Substring search in O(n + m), repeated-pattern detection.",
          tmpl: `pi = [0] * m                 # failure function of pattern p
k = 0
for i in range(1, m):
    while k and p[i] != p[k]:
        k = pi[k - 1]
    if p[i] == p[k]:
        k += 1
    pi[i] = k` },
        4: { name: "String Hashing", zh: "字符串哈希",
          intro: "Polynomial rolling hash: after O(n) preprocessing, compare any two substrings in O(1). Use a large modulus (or double hashing) to make collisions negligible." },
        10: { name: "Other", zh: "其他",
          intro: "String problems that need no heavy machinery — clever scanning, counting, or reuse of earlier toolkits." },
      },
    },
  };

  const api = {
    topic(t) { return G[t] || null; },
    /* Look up a chapter by number, falling back to the raw section name for
     * 0x3F's un-numbered "Special Topic" sections. */
    chapter(t, num, sectionName) {
      const g = G[t];
      if (!g) return null;
      if (num != null && g.chapters[num]) return g.chapters[num];
      if (sectionName && g.chapters[sectionName]) return g.chapters[sectionName];
      return null;
    },
  };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else global.Guide = api;
})(this);
