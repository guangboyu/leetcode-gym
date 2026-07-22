/* Subtopic curriculum for the beginner route: each pattern stage splits into
 * semantic subtopics ("shrink-when-invalid window", "binary search the answer"),
 * each with a recognize -> solve mini-guide and an explicit problem list.
 * Problems are assigned by hand (informed by their 0x3F section memberships);
 * every id is a problem in the Hot 100 / Top Interview 150 / NeetCode 250 union.
 * Pure data + one lookup helper, no DOM. Sets global.Curriculum (no module
 * branch on purpose: keeps it loadable in one shared scope for JSC tests).
 */
(function (global) {
  "use strict";

  const SUB = {
    "Arrays & Hashing": [
      { name: "1. Hash set & map basics",
        recognize: "“Have I seen this before?”, “does a pair exist?”, O(1) membership or key→value bookkeeping.",
        solve: "One pass; query the map before inserting the current element so each pair is seen exactly once.",
        tmpl: `seen = {}                   # value -> index
for i, x in enumerate(a):
    if target - x in seen:
        return [seen[target - x], i]
    seen[x] = i`,
        ids: [1, 217, 242, 383, 205, 290, 705, 706, 1929] },
      { name: "2. Grouping & counting",
        recognize: "“Group the equivalent items”, “most frequent”, “appears more than n/k times”.",
        solve: "Map from a canonical key (sorted string, count signature) to a bucket; counts via Counter. Majority element has the O(1)-space Boyer-Moore vote.",
        ids: [49, 347, 169, 229, 274, 128] },
      { name: "3. Prefix sums & products",
        recognize: "Many range-sum queries, “subarray summing to k” (negatives allowed!), “product of everything except me”.",
        solve: "pre[i+1] = pre[i] + a[i], so sum(i..j) = pre[j+1] - pre[i]. Count subarrays with a map of previously seen prefix values; “except self” = prefix pass × suffix pass.",
        tmpl: `# subarrays summing to k (works with negatives)
cnt = {0: 1}
s = ans = 0
for x in a:
    s += x
    ans += cnt.get(s - k, 0)
    cnt[s] = cnt.get(s, 0) + 1`,
        ids: [238, 304, 560] },
      { name: "4. In-place array surgery",
        recognize: "“Do it in O(1) extra space”: remove/keep elements, partition by value, find the missing one by using the array itself.",
        solve: "Slow writer + fast reader, or cyclic swaps that park value v at index v. Sort Colors is a 3-way partition with two boundaries.",
        ids: [27, 41, 75, 80] },
      { name: "5. String scanning",
        recognize: "Format, split, align, or match strings; no algorithmic depth, all edge cases.",
        solve: "Walk the string once with clear state; build results in a list and join. Rehearse these — interviewers use them to check clean code speed.",
        ids: [6, 12, 14, 28, 58, 68, 151] },
      { name: "6. Sorting & simulation",
        recognize: "“Design a structure”, “validate a board”, or a scan where sorting first makes the logic trivial.",
        solve: "Pick the invariant, then simulate carefully. GetRandom O(1) pairs a list with an index map; swap-with-last makes deletion O(1).",
        ids: [36, 122, 380, 912] },
    ],

    "Two Pointers": [
      { name: "1. Opposite ends",
        recognize: "Sorted array (or sortable) + “find a pair/triple with a target property”; palindrome checks; “container/trap water”.",
        solve: "l and r start at the ends; each step, the pointer whose element is provably useless moves inward. For 3Sum, fix one element and run the two-pointer scan on the rest.",
        tmpl: `l, r = 0, len(a) - 1
while l < r:
    s = a[l] + a[r]
    if s == target: ...
    elif s < target: l += 1     # a[l] can pair with nothing -> drop it
    else: r -= 1`,
        ids: [11, 15, 18, 42, 125, 167, 680, 881] },
      { name: "2. Slow-fast writer",
        recognize: "“Remove/compact in place”, “move zeroes”, “rotate”, “next permutation” — reorder within the same array.",
        solve: "Fast pointer reads every element; slow pointer marks where the next kept element is written. Rotate = reverse whole, then reverse both halves.",
        ids: [26, 31, 88, 189, 283, 344] },
      { name: "3. Two sequences in lockstep",
        recognize: "“Is s a subsequence of t?”, merge/interleave two strings or arrays.",
        solve: "One pointer per sequence; advance the appropriate one each step. Greedy matching is optimal for subsequence checks.",
        ids: [392, 1768] },
    ],

    "Sliding Window": [
      { name: "1. Fixed-size window",
        recognize: "The problem hands you a k: “window of size k”, “within distance k”, “find anagrams” (window size = pattern length).",
        solve: "No shrink logic — add a[i], remove a[i-k], record once the window is full. Anagram windows keep a count map plus a matched counter.",
        tmpl: `for i, x in enumerate(a):
    # add x to window stats
    if i < k - 1: continue      # window not full yet
    # update answer with window [i-k+1, i]
    # remove a[i - k + 1] from window stats`,
        ids: [219, 438, 567, 30, 658] },
      { name: "2. Longest window (shrink when invalid)",
        recognize: "“LONGEST substring/subarray such that <constraint holds>”.",
        solve: "Extend right greedily; while the window is broken, shrink from the left; measure AFTER the while (window is valid there). Needs monotonicity: growing only makes it worse.",
        tmpl: `l = 0
for r, x in enumerate(a):
    add(x)
    while window_invalid():
        remove(a[l]); l += 1
    ans = max(ans, r - l + 1)   # measure while valid`,
        ids: [3, 121, 424] },
      { name: "3. Shortest window (shrink while valid)",
        recognize: "“SHORTEST/minimum subarray that satisfies <constraint>”.",
        solve: "The flip of longest: while the window is VALID, record the answer then shrink to find the tightest fit. Measure INSIDE the while — getting this backwards fails every test.",
        tmpl: `l = 0
for r, x in enumerate(a):
    add(x)
    while window_valid():
        ans = min(ans, r - l + 1)   # measure BEFORE shrinking
        remove(a[l]); l += 1`,
        ids: [76, 209] },
      { name: "4. Window max/min (monotonic deque)",
        recognize: "“Max/min of every window”, or window constrained by max−min ≤ limit.",
        solve: "Deque of indices, values kept monotonic: pop the back while dominated by the new element, pop the front when it slides out. O(n) amortized.",
        tmpl: `from collections import deque
q = deque()                     # indices, a[q] decreasing
for i, x in enumerate(a):
    while q and a[q[-1]] <= x: q.pop()
    q.append(i)
    if q[0] <= i - k: q.popleft()
    if i >= k - 1: ans.append(a[q[0]])`,
        ids: [239] },
    ],

    "Stack & Monotonic Stack": [
      { name: "1. Matching & elimination",
        recognize: "Nested/paired symbols, collisions that cancel adjacent items, “generate all valid parentheses”.",
        solve: "Push what is unresolved; the stack top is always the most recent open item. Asteroid-style problems pop while the new element destroys the top. Generate Parentheses is backtracking on open/close counts.",
        ids: [20, 22, 71, 682, 735] },
      { name: "2. Expression parsing",
        recognize: "Evaluate or decode a string with operators, brackets, or repeat counts.",
        solve: "One stack for numbers and one for pending operators/context; on '(' push state, on ')' pop and combine. RPN is the pure form: push operands, apply operators.",
        ids: [150, 224, 394] },
      { name: "3. Monotonic stack",
        recognize: "“Next/previous greater (or smaller) element”, “days until warmer”, “largest rectangle”, spans.",
        solve: "Keep indices whose values are monotonic; each pop resolves one element's answer. Every element pushes and pops once: O(n).",
        tmpl: `st = []                     # indices, a[st] decreasing
for i, x in enumerate(a):
    while st and a[st[-1]] < x:
        j = st.pop()            # x is a[j]'s next greater element
        ans[j] = i - j
    st.append(i)`,
        ids: [84, 739, 853, 901] },
      { name: "4. Stack design",
        recognize: "“Design a stack/queue with an extra O(1) query” (min, max frequency), or build one container from another.",
        solve: "Store the auxiliary answer alongside each element (value, min-so-far), so pop restores it for free.",
        ids: [155, 225, 232, 895] },
    ],

    "Binary Search": [
      { name: "1. Boundary on sorted data",
        recognize: "Sorted input + “find the position / first / last occurrence”, or a store queried by timestamp.",
        solve: "Frame every variant as lower_bound: the first index where check() is true. Then first occurrence, insert position, and ranges are all the same code.",
        tmpl: `lo, hi = 0, n               # first index with check true
while lo < hi:
    mid = (lo + hi) // 2
    if check(mid): hi = mid
    else: lo = mid + 1
return lo`,
        ids: [704, 35, 34, 74, 374, 981] },
      { name: "2. Rotated & mountain arrays",
        recognize: "“Sorted then rotated”, “peak element”, “mountain array” — piecewise-sorted data.",
        solve: "Compare mid against an endpoint to decide which half is normally sorted, then decide which half can contain the target. Duplicates can force a linear step.",
        ids: [33, 81, 153, 162, 1095] },
      { name: "3. Binary search the answer",
        recognize: "“Minimum speed/capacity/largest-sum so that …”, “minimize the maximum”. The answer itself is the search space.",
        solve: "check(x) = “is x feasible?” must be monotonic; binary search the smallest feasible x. sqrt(x) is the same idea on values.",
        ids: [69, 410, 875, 1011] },
      { name: "4. Divide & eliminate",
        recognize: "Two sorted arrays jointly (median), or a row+column-sorted matrix.",
        solve: "Median: binary search the partition of the shorter array. Sorted matrix: start at the top-right corner and discard a row or column each step.",
        ids: [4, 240] },
    ],

    "Linked List": [
      { name: "1. Reversal",
        recognize: "“Reverse the list / a sublist / in k-groups”, “swap pairs”.",
        solve: "The three-pointer loop below is the atom; sublist and k-group reversal wrap it with a dummy head and careful reconnection. Draw the arrows first.",
        tmpl: `prev, cur = None, head
while cur:
    nxt = cur.next
    cur.next = prev
    prev, cur = cur, nxt
return prev`,
        ids: [206, 92, 24, 25] },
      { name: "2. Dummy head & deletion",
        recognize: "Delete/skip/partition nodes where the head itself might be removed, “remove nth from end”, “rotate”.",
        solve: "dummy = ListNode(0, head) kills every head edge case. For nth-from-end, advance a lead pointer n steps, then move both.",
        ids: [19, 61, 82, 86] },
      { name: "3. Fast & slow pointers",
        recognize: "Cycle? middle? intersection? palindrome? — questions about list SHAPE without extra space.",
        solve: "fast moves 2, slow moves 1: they meet iff there is a cycle; reset one to head and they meet at the cycle entrance. Middle = where fast hits the end. Duplicate-number is this on the array seen as a function graph.",
        ids: [141, 142, 143, 160, 234, 287] },
      { name: "4. Merging & divide",
        recognize: "“Merge two/k sorted lists”, “sort a list”, “add two numbers”.",
        solve: "Two-list merge with a dummy tail is the atom; k lists use a heap of heads (or pairwise merging); sort = split at middle + merge (mergesort).",
        ids: [2, 21, 23, 148] },
      { name: "5. Design & copying",
        recognize: "“Design LRU/LFU/circular queue”, “copy a list with random pointers”.",
        solve: "LRU = hashmap + doubly-linked list, evict the tail. Random-pointer copy: map old→new (or interleave copies in place).",
        ids: [138, 146, 460, 622] },
    ],

    "Trees & BSTs": [
      { name: "1. Traversal basics",
        recognize: "“Return the in/pre/postorder”, “iterator over a BST”.",
        solve: "Know the recursive version cold and the stack-based iterative inorder (push all lefts, pop, go right) — the iterator is exactly that stack, paused.",
        ids: [94, 144, 145, 173] },
      { name: "2. Top-down DFS (preorder)",
        recognize: "Info flows root→leaf: running path sum, max seen so far, “count good nodes”, root-to-leaf numbers.",
        solve: "Pass accumulators as parameters; check leaf conditions at the leaf.",
        ids: [104, 112, 129, 1448] },
      { name: "3. Bottom-up DFS (postorder)",
        recognize: "A node's answer depends on its children: height, balance, symmetry, same/subtree, invert, prune.",
        solve: "Trust the recursion: assume dfs(child) already answers the subtree, combine at the node, return upward.",
        tmpl: `def dfs(node):
    if not node: return 0
    left, right = dfs(node.left), dfs(node.right)
    return max(left, right) + 1   # combine children's answers`,
        ids: [100, 101, 110, 226, 572, 543, 1325] },
      { name: "4. BFS by level",
        recognize: "“Level order / zigzag / average per level / right side view / connect next pointers”.",
        solve: "Queue; loop len(q) times per level so levels stay separated. Right side view = last node of each level.",
        ids: [102, 103, 117, 199, 637] },
      { name: "5. BST property",
        recognize: "The tree is a BST: validate, k-th smallest, closest values, insert/delete, LCA by value.",
        solve: "Inorder is sorted — many BST problems are “inorder + observation”. Validation passes down (lo, hi) bounds. LCA: walk from root, split point is the answer.",
        ids: [98, 230, 235, 450, 530, 701] },
      { name: "6. Build & transform",
        recognize: "“Construct from preorder+inorder”, serialize/deserialize, flatten, count complete-tree nodes.",
        solve: "Construction: the first preorder element is the root; inorder splits left/right (use an index map). Serialization: preorder with null markers.",
        ids: [105, 106, 108, 114, 222, 297, 427] },
      { name: "7. Paths & tree DP",
        recognize: "“Max path sum anywhere”, “count paths summing to k”, LCA of arbitrary nodes, rob houses on a tree.",
        solve: "Distinguish “best chain returned to parent” from “best path through the node” (diameter trick). Path Sum III = prefix sums on the root path. Tree DP returns a tuple of states per node.",
        ids: [124, 236, 337, 437] },
    ],

    "Heap / Priority Queue": [
      { name: "1. Top-k & k-th",
        recognize: "“k largest/smallest/closest/most frequent”, “k-th element”, “k smallest pairs”.",
        solve: "Min-heap of size k: push, pop when over k; the root is the k-th largest. Quickselect gives O(n) average for a one-shot k-th.",
        tmpl: `import heapq
h = []
for x in a:
    heapq.heappush(h, x)
    if len(h) > k: heapq.heappop(h)
# h[0] is the k-th largest`,
        ids: [215, 373, 703, 973] },
      { name: "2. Two heaps",
        recognize: "“Running median”, or any “split the stream around the middle” question.",
        solve: "Max-heap for the lower half, min-heap for the upper, rebalanced so sizes differ by ≤ 1; the median lives at the roots.",
        ids: [295] },
      { name: "3. Scheduling & rearranging",
        recognize: "Repeatedly take the best available item, possibly with cooldowns or capacities: tasks, stones, seats, “no two adjacent equal”.",
        solve: "Heap keyed by the greedy criterion (count, end time, ratio); pop, use, push back the updated item. Car Pooling is the simpler difference-array cousin.",
        ids: [355, 502, 621, 767, 1046, 1094, 1405, 1834] },
    ],

    "Backtracking": [
      { name: "1. Subsets & combinations",
        recognize: "“All subsets / combinations summing to target / letter combinations”. Order inside a choice does not matter.",
        solve: "Pass a start index so each element is considered once; reuse allowed → recurse with i, not i+1. Duplicates: sort, then skip a[i]==a[i-1] at the same depth.",
        tmpl: `def dfs(start, path):
    ans.append(path[:])         # every node is a subset
    for i in range(start, n):
        if i > start and a[i] == a[i-1]: continue  # dup guard
        path.append(a[i])
        dfs(i + 1, path)
        path.pop()`,
        ids: [17, 39, 40, 77, 78, 90, 1863] },
      { name: "2. Permutations & boards",
        recognize: "“All orderings”, N-Queens style constraint boards. Order matters, each element used once.",
        solve: "Track a used[] set (or column/diagonal sets for queens); choose, recurse, un-choose. Duplicates: sort + skip equal values whose previous twin is unused.",
        ids: [46, 47, 51, 52] },
      { name: "3. Partition backtracking",
        recognize: "“Split the string into valid pieces” (palindromes, dictionary words) and return all ways.",
        solve: "At position i, try every valid prefix and recurse on the rest; memoize feasibility when only counting or checking.",
        ids: [131, 140] },
      { name: "4. Search with pruning",
        recognize: "Grid word search, bucket-filling into k equal groups, matchsticks — exponential search that lives or dies on pruning.",
        solve: "Prune hard: sort descending, skip equal buckets, bail when a bucket overflows. Mark grid cells visited in place and restore on backtrack.",
        ids: [79, 473, 698] },
    ],

    "Tries": [
      { name: "1. Build & query",
        recognize: "Many words + “insert / exact search / startsWith”.",
        solve: "Nested maps (or arrays of 26); walk character by character; '$' marks end-of-word.",
        tmpl: `trie = {}
for w in words:
    node = trie
    for c in w:
        node = node.setdefault(c, {})
    node['$'] = True`,
        ids: [208] },
      { name: "2. Wildcards & board search",
        recognize: "Search with '.' wildcards, or find MANY words in one grid at once.",
        solve: "Wildcard → DFS over all children at that node. Word Search II: DFS the grid while walking the trie, prune dead branches, remove found words.",
        ids: [211, 212] },
      { name: "3. Trie + DP",
        recognize: "Partition/segment a string against a dictionary where prefix matching is the bottleneck.",
        solve: "f[i] over positions; transitions walk the trie from i instead of trying every substring.",
        ids: [2707] },
    ],

    "Graphs": [
      { name: "1. Grid flood fill (DFS)",
        recognize: "“Islands / regions / area / perimeter” on a grid; “spread from the border”.",
        solve: "DFS the 4 neighbors, mark visited by mutating the grid. Border-connected questions (Surrounded Regions, Pacific-Atlantic) flip the direction: start from the edges.",
        tmpl: `def dfs(r, c):
    if not (0 <= r < R and 0 <= c < C) or g[r][c] != LAND: return 0
    g[r][c] = SEEN
    return 1 + dfs(r+1,c) + dfs(r-1,c) + dfs(r,c+1) + dfs(r,c-1)`,
        ids: [130, 200, 417, 463, 695] },
      { name: "2. BFS shortest steps",
        recognize: "“Minimum number of steps/mutations/moves”, “time for rot to spread” — unweighted shortest path, sometimes multi-source.",
        solve: "Queue + seen set; mark visited when ENQUEUING, not when popping. Multi-source: seed the queue with all sources at distance 0. Word Ladder builds neighbors via wildcard buckets.",
        tmpl: `from collections import deque
q, seen, d = deque([start]), {start}, 0
while q:
    for _ in range(len(q)):
        u = q.popleft()
        if u == goal: return d
        for v in neighbors(u):
            if v not in seen:
                seen.add(v); q.append(v)
    d += 1`,
        ids: [127, 433, 752, 909, 994] },
      { name: "3. Topological sort",
        recognize: "“Prerequisites / build order / can you finish”, layered peeling (min height trees).",
        solve: "Kahn: queue of indegree-0 nodes, pop and decrement neighbors. Processed < n ⇒ cycle. Min Height Trees peels leaves layer by layer — same loop.",
        tmpl: `q = deque([u for u in range(n) if indeg[u] == 0])
order = []
while q:
    u = q.popleft(); order.append(u)
    for v in adj[u]:
        indeg[v] -= 1
        if indeg[v] == 0: q.append(v)
# len(order) < n -> cycle`,
        ids: [207, 210, 310, 1462] },
      { name: "4. Union-Find & graph modeling",
        recognize: "“Merge accounts/components”, “which edge creates a cycle”, ratio queries along paths, degree puzzles (town judge).",
        solve: "DSU with path compression: find(x) follows parents; union by attaching roots. Evaluate Division is DSU (or DFS) with edge weights. Some “graph” problems are just degree counting.",
        tmpl: `pa = list(range(n))
def find(x):
    while pa[x] != x:
        pa[x] = pa[pa[x]]       # path halving
        x = pa[x]
    return x
def union(a, b): pa[find(a)] = find(b)`,
        ids: [133, 399, 684, 721, 953, 997] },
    ],

    "Advanced Graphs": [
      { name: "1. Dijkstra & minimax paths",
        recognize: "Shortest path with WEIGHTED edges (no negatives); “path minimizing the maximum edge” (effort, rising water); “cheapest flights within k stops”.",
        solve: "Heap of (dist, node); settle the closest, relax edges, skip stale pops. Minimax: replace + with max in the relaxation. K-stops caps the relaxation rounds (Bellman-Ford flavor).",
        tmpl: `import heapq
dist = {s: 0}; h = [(0, s)]
while h:
    d, u = heapq.heappop(h)
    if d > dist.get(u, inf): continue   # stale
    for v, w in adj[u]:
        if d + w < dist.get(v, inf):
            dist[v] = d + w
            heapq.heappush(h, (d + w, v))`,
        ids: [743, 778, 787, 1631] },
      { name: "2. Minimum spanning tree",
        recognize: "“Connect all points at minimum total cost”.",
        solve: "Kruskal: sort edges, union-find, take edges that join two components. Critical edge = MST cost rises without it.",
        ids: [1489, 1584] },
      { name: "3. Special structures",
        recognize: "Use-every-edge-once itineraries (Eulerian path), building a matrix from order constraints, connectivity through shared prime factors.",
        solve: "Eulerian: Hierholzer — DFS consuming edges, append on the way out, reverse. Order constraints → topological sort per axis. Shared-factor connectivity → union nodes with their prime factors.",
        ids: [332, 2392, 2709] },
    ],

    "1-D Dynamic Programming": [
      { name: "1. Linear transitions",
        recognize: "“How many ways to reach step n”, cost to climb, Fibonacci-shaped recurrences, counting with order (Combination Sum IV).",
        solve: "f[i] from f[i-1], f[i-2], …; roll two variables when only the last few states matter.",
        tmpl: `f0, f1 = 1, 1               # climbing stairs
for _ in range(2, n + 1):
    f0, f1 = f1, f0 + f1
return f1`,
        ids: [70, 118, 377, 746, 1137] },
      { name: "2. Take or skip (House Robber)",
        recognize: "Pick elements under a no-two-adjacent constraint, maximize the total.",
        solve: "f[i] = max(f[i-1], f[i-2] + a[i]). Circular version: run twice, excluding the first or the last house.",
        ids: [198, 213] },
      { name: "3. Best subarray ending here (Kadane)",
        recognize: "“Maximum product/sum subarray” — contiguous, best ending at each index.",
        solve: "Carry the best (and for products, the worst — negatives flip) subarray ending at i; answer is the best over all i.",
        ids: [152] },
      { name: "4. Partition & decode",
        recognize: "“Can the string be segmented / how many decodings / longest valid prefix structure”.",
        solve: "f[i] = answer for the first i chars; transitions try every valid last piece (dictionary word, 1-2 digit code).",
        ids: [32, 91, 139] },
      { name: "5. Knapsack on values",
        recognize: "“Fewest coins / perfect squares to build n”, “split into two equal halves”. Items combined under a capacity.",
        solve: "0-1 knapsack: loop capacity DOWNWARD (each item once). Unbounded (coins): loop capacity upward.",
        tmpl: `# 0-1 knapsack feasibility (Partition Equal Subset Sum)
f = [True] + [False] * target
for x in a:
    for c in range(target, x - 1, -1):   # downward: use x once
        f[c] = f[c] or f[c - x]`,
        ids: [279, 322, 343, 416] },
      { name: "6. Subsequences & palindromes",
        recognize: "“Longest increasing subsequence”, “count palindromic substrings”.",
        solve: "LIS: patience trick — binary search a tails array, O(n log n). Palindromes: expand around each of the 2n−1 centers.",
        ids: [5, 300, 647] },
      { name: "7. Game DP",
        recognize: "Two players alternate taking from a line, both optimal, “who wins / best margin”.",
        solve: "f[i] = best score difference for the player to move from state i; take max over moves of (gain − f[next]).",
        ids: [1406] },
    ],

    "2-D Dynamic Programming": [
      { name: "1. Grid paths & submatrices",
        recognize: "Count/min-cost paths moving right+down, largest square, longest increasing path.",
        solve: "f[r][c] from top/left neighbors, row by row. Maximal square: f = min of three neighbors + 1. Arbitrary-direction grids → memoized DFS.",
        ids: [62, 63, 64, 120, 221, 329] },
      { name: "2. Two sequences",
        recognize: "Compare two strings: LCS, edit distance, interleaving, distinct subsequences, regex matching.",
        solve: "f[i][j] = answer for prefixes s[:i], t[:j]; match ⇒ diagonal, else best of dropping a character from either side.",
        tmpl: `for i in range(1, m + 1):        # LCS
    for j in range(1, n + 1):
        if s[i-1] == t[j-1]:
            f[i][j] = f[i-1][j-1] + 1
        else:
            f[i][j] = max(f[i-1][j], f[i][j-1])`,
        ids: [10, 72, 97, 115, 1143] },
      { name: "3. Knapsack variants",
        recognize: "“Ways to hit a target with +/− signs”, “ways to make amount with unlimited coins”, minimize leftover stone.",
        solve: "Same knapsack loops with a second dimension baked in: counting uses +=, 0-1 goes downward, unbounded upward. Target Sum reduces to subset-sum via (total+target)/2.",
        ids: [494, 518, 1049] },
      { name: "4. State machines (stock series)",
        recognize: "Buy/sell with limits, cooldowns, or k transactions.",
        solve: "States = (day, holding?, transactions used); f transitions buy/sell/rest. All five stock problems are this one machine with different constraints.",
        ids: [123, 188, 309] },
      { name: "5. Interval DP",
        recognize: "“Burst balloons” — the answer for a range depends on choosing the LAST action inside it.",
        solve: "f[l][r] over gaps, lengths increasing; pick the last balloon k: f[l][r] = max over k of f[l][k] + f[k][r] + gain(l,k,r).",
        ids: [312] },
      { name: "6. Game DP on ranges",
        recognize: "Two players pick from ends/piles, both optimal.",
        solve: "f[l][r] = best margin for the mover on that range; or exploit parity (Stone Game I: first player always wins).",
        ids: [877, 1140] },
    ],

    "Greedy": [
      { name: "1. Jump frontier",
        recognize: "“Can you reach the end / fewest jumps”, reachability with per-index ranges.",
        solve: "Sweep once, keep the furthest reachable index; count a jump when you pass the current frontier. BFS-on-intervals intuition.",
        tmpl: `far = 0                     # Jump Game
for i, x in enumerate(a):
    if i > far: return False    # unreachable gap
    far = max(far, i + x)
return True`,
        ids: [45, 55, 1871] },
      { name: "2. Running scans (Kadane family)",
        recognize: "“Maximum subarray”, circular variant, longest turbulent run.",
        solve: "Best subarray ending here: cur = max(x, cur + x). Circular = max(normal, total − minimum subarray). Turbulent: extend or restart the run per comparison sign.",
        ids: [53, 918, 978] },
      { name: "3. Partition by last occurrence",
        recognize: "“Cut into as many parts as possible so parts don't share letters”, build a target from pieces.",
        solve: "Precompute each element's last position; extend the current part to cover it; cut when i reaches the boundary.",
        ids: [763, 1899] },
      { name: "4. Exchange arguments & case analysis",
        recognize: "“Does a valid order/assignment exist”, distribute under fairness (candy), make change, circular gas tour.",
        solve: "Sort or scan with the one safe local rule, then prove no regret: gas station restarts after any failed prefix; candy needs a left pass + right pass.",
        ids: [134, 135, 649, 678, 846, 860] },
    ],

    "Intervals": [
      { name: "1. Merge & insert",
        recognize: "“Merge overlapping intervals”, “insert and merge”, “summarize ranges”.",
        solve: "Sort by start; overlap iff start ≤ current end; extend or push a new block.",
        tmpl: `ivs.sort()
merged = []
for s, e in ivs:
    if merged and s <= merged[-1][1]:
        merged[-1][1] = max(merged[-1][1], e)
    else:
        merged.append([s, e])`,
        ids: [56, 57, 228] },
      { name: "2. Sort by end (scheduling)",
        recognize: "“Fewest removals so none overlap”, “fewest arrows to pop all balloons”.",
        solve: "Sort by END and greedily keep the earliest-ending interval — it leaves the most room. Arrows = count the non-overlapping groups.",
        ids: [435, 452] },
      { name: "3. Sweep with a heap",
        recognize: "Rooms/machines over time, per-query smallest covering interval.",
        solve: "Sort events; heap holds active intervals keyed by end (or size). Offline trick: sort queries too and answer them in order.",
        ids: [1851, 2402] },
    ],

    "Math & Bit Manipulation": [
      { name: "1. Bit tricks",
        recognize: "“Without +”, “single number among pairs/triples”, count bits, missing number.",
        solve: "x ^ x = 0 cancels pairs; n & (n-1) drops the lowest set bit; add = XOR + shifted carries. Triples: count each bit position mod 3.",
        tmpl: `acc = 0                     # single number
for x in a:
    acc ^= x                    # pairs cancel
return acc`,
        ids: [136, 137, 190, 191, 201, 268, 338, 371, 3133] },
      { name: "2. Numbers & digits",
        recognize: "Digit-by-digit arithmetic (reverse, plus one, add binary, multiply strings), gcd, factorial zeros, base conversions, digit cycles.",
        solve: "Simulate school arithmetic with explicit carries; gcd(a,b) = gcd(b, a%b); trailing zeros = count factors of 5. Watch overflow rules the problem states.",
        ids: [7, 9, 13, 43, 50, 66, 67, 168, 172, 202, 1071, 2807] },
      { name: "3. Matrix simulation",
        recognize: "Rotate / spiral / set zeroes / Game of Life — transform a grid, often in place.",
        solve: "Rotate = transpose + reverse each row. Spiral: four shrinking boundaries. In-place updates encode old+new state in the same cell (extra bit).",
        ids: [48, 54, 73, 289, 867] },
      { name: "4. Geometry & counting",
        recognize: "Points on a line, counting axis-aligned squares.",
        solve: "Fix one point, hash slopes in lowest terms. Squares: store point counts, iterate diagonal partners.",
        ids: [149, 2013] },
    ],
  };

  // pattern -> Map(problem id -> subtopic entry), built once
  const BY_ID = {};
  for (const pat of Object.keys(SUB)) {
    const m = new Map();
    for (const sub of SUB[pat]) for (const id of sub.ids) m.set(id, sub);
    BY_ID[pat] = m;
  }

  global.Curriculum = {
    SUB,
    subtopicFor(pattern, id) { return (BY_ID[pattern] && BY_ID[pattern].get(id)) || null; },
  };
})(this);
