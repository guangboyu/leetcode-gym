"""Sliding window animations."""
from __future__ import annotations

from collections import deque

from ..model import Aux, Tracer, window_roles


# --------------------------------------------------------------------------- #
# LC 3 - longest substring without repeating characters (variable window)
# --------------------------------------------------------------------------- #
LC3_CODE = """
def length_of_longest(s):
    seen = set()
    left = 0
    best = 0
    for right in range(len(s)):
        while s[right] in seen:
            seen.remove(s[left])
            left += 1
        seen.add(s[right])
        best = max(best, right - left + 1)
    return best
"""


def _setfmt(items) -> str:
    return "{" + ",".join(items) + "}" if items else "{}"


def lc3_longest_substring(s: str = "abcabcbb"):
    t = Tracer(list(s), "Longest substring without repeating characters",
               "LeetCode 3  |  variable-size sliding window", LC3_CODE,
               slug="lc0003-longest-substring",
               legend={"idle": "not reached yet", "window": "current window",
                       "focus": "the new character", "valid": "no duplicates",
                       "invalid": "duplicate inside the window",
                       "best": "longest window so far", "dim": "left behind"})
    n = len(s)
    seen: list[str] = []
    left = 0
    best = 0
    best_span = None

    t.snap([("idle")] * n, line=1,
           note="Grow the window with right. The moment it breaks the rule, "
                "shrink it from the left until the rule holds again.",
           verdict="info",
           state=[("seen", "{}"), ("best", "0")], hold=1.6)

    for right in range(n):
        ch = s[right]
        # look at the new character
        roles = window_roles(n, left, right - 1, focus=right)
        t.snap(roles, line=5,
               note=f"right moves to {right}. New character '{ch}'.",
               pointers=[("left", left), ("right", right)],
               bracket=(left, right - 1, f"window len {right - left}") if right > left else None,
               state=[("seen", _setfmt(seen)), ("best", str(best))])

        if ch in seen:
            roles = window_roles(n, left, right, inside="invalid")
            t.snap(roles, line=6, verdict="invalid",
                   note=f"'{ch}' is already inside the window, so this window is invalid. "
                        f"Shrink from the left.",
                   pointers=[("left", left), ("right", right)],
                   bracket=(left, right, "invalid"), bracket_role="invalid",
                   state=[("seen", _setfmt(seen)), ("best", str(best))], hold=1.5)

        while ch in seen:
            dropped = s[left]
            seen.remove(dropped)
            left += 1
            roles = window_roles(n, left, right, inside="invalid" if ch in seen else "window")
            t.snap(roles, line=8, verdict="invalid" if ch in seen else None,
                   note=f"Drop '{dropped}' at index {left - 1} and move left to {left}."
                        + ("" if ch in seen else f" The duplicate '{ch}' is gone."),
                   pointers=[("left", left), ("right", right)],
                   bracket=(left, right, "shrinking"),
                   bracket_role="invalid" if ch in seen else "window",
                   state=[("seen", _setfmt(seen)), ("best", str(best))])

        seen.append(ch)
        size = right - left + 1
        is_best = size > best
        if is_best:
            best = size
            best_span = (left, right)
        roles = window_roles(n, left, right, inside="best" if is_best else "valid")
        t.snap(roles, line=10, verdict="record" if is_best else "valid",
               note=(f"Window [{left}, {right}] = \"{s[left:right + 1]}\" is valid, length {size}. "
                     + ("New best." if is_best else f"Best stays {best}.")),
               pointers=[("left", left), ("right", right)],
               bracket=(left, right, f"len {size}"),
               bracket_role="best" if is_best else "valid",
               state=[("seen", _setfmt(seen)), ("best", str(best))],
               hold=1.35 if is_best else 1.0)

    lo, hi = best_span
    roles = window_roles(n, lo, hi, inside="best", before="dim", after="dim")
    t.snap(roles, line=11, verdict="record",
           note=f"Answer: {best}  (\"{s[lo:hi + 1]}\"). Every index entered and left "
                f"the window at most once, so the scan is O(n).",
           bracket=(lo, hi, f"answer len {best}"), bracket_role="best",
           state=[("best", str(best))], hold=2.0)
    return t.trace


# --------------------------------------------------------------------------- #
# LC 643 - maximum average subarray I (fixed window)
# --------------------------------------------------------------------------- #
LC643_CODE = """
def max_sum_window(nums, k):
    total = sum(nums[:k])
    best = total
    for right in range(k, len(nums)):
        total += nums[right]
        total -= nums[right - k]
        best = max(best, total)
    return best
"""


def lc643_fixed_window(nums=(1, 12, -5, -6, 50, 3, -8, 7, 20, -2), k: int = 4):
    nums = list(nums)
    n = len(nums)
    t = Tracer(nums, f"Maximum sum of a subarray of size {k}",
               "LeetCode 643  |  fixed-size sliding window", LC643_CODE,
               slug="lc0643-fixed-window",
               legend={"idle": "not reached yet", "window": "current window",
                       "focus": "entering the window",
                       "invalid": "leaving the window",
                       "best": "best window so far", "dim": "left behind"})

    t.snap(line=1, verdict="info",
           note=f"The window never changes size. Every step adds one element on the right "
                f"and drops one on the left, so each step costs O(1).",
           state=[("k", str(k)), ("sum", "-"), ("best", "-")], hold=1.7)

    total = sum(nums[:k])
    best = total
    best_span = (0, k - 1)
    roles = window_roles(n, 0, k - 1)
    t.snap(roles, line=2, verdict="record",
           note=f"Build the first window: sum of the first {k} elements = {total}.",
           pointers=[("left", 0), ("right", k - 1)],
           bracket=(0, k - 1, f"sum {total}"),
           state=[("k", str(k)), ("sum", str(total)), ("best", str(best))], hold=1.5)

    for right in range(k, n):
        left = right - k + 1
        gone = right - k
        roles = window_roles(n, gone, right, inside="window", focus=right)
        roles[gone] = "invalid"
        t.snap(roles, line=5,
               note=f"Slide right. Add nums[{right}] = {nums[right]} (amber), "
                    f"drop nums[{gone}] = {nums[gone]} (red).",
               pointers=[("left", left), ("right", right)],
               state=[("k", str(k)), ("sum", str(total)), ("best", str(best))],
               hold=1.25)

        total += nums[right] - nums[gone]
        is_best = total > best
        if is_best:
            best = total
            best_span = (left, right)
        roles = window_roles(n, left, right, inside="best" if is_best else "window")
        t.snap(roles, line=7, verdict="record" if is_best else None,
               note=f"Window [{left}, {right}] sums to {total}. "
                    + ("New best." if is_best else f"Best stays {best}."),
               pointers=[("left", left), ("right", right)],
               bracket=(left, right, f"sum {total}"),
               bracket_role="best" if is_best else "window",
               state=[("k", str(k)), ("sum", str(total)), ("best", str(best))],
               hold=1.3 if is_best else 1.0)

    lo, hi = best_span
    roles = window_roles(n, lo, hi, inside="best", before="dim", after="dim")
    t.snap(roles, line=8, verdict="record",
           note=f"Answer: {best} from window [{lo}, {hi}]. "
                f"One pass, O(n) time and O(1) extra space.",
           bracket=(lo, hi, f"best sum {best}"), bracket_role="best",
           state=[("best", str(best)), ("max avg", f"{best / k:g}")], hold=2.0)
    return t.trace


# --------------------------------------------------------------------------- #
# LC 239 - sliding window maximum (monotonic deque)
# --------------------------------------------------------------------------- #
LC239_CODE = """
def max_sliding_window(nums, k):
    dq = deque()          # indices, values decreasing
    out = []
    for right in range(len(nums)):
        while dq and nums[dq[-1]] <= nums[right]:
            dq.pop()
        dq.append(right)
        if dq[0] <= right - k:
            dq.popleft()
        if right >= k - 1:
            out.append(nums[dq[0]])
    return out
"""


def _dq_aux(nums, dq):
    return Aux(title="deque  (indices, values decreasing)", kind="cells",
               cells=[str(nums[i]) for i in dq],
               roles=["best"] + ["window"] * (len(dq) - 1),
               subs=[f"i={i}" for i in dq])


def lc239_window_maximum(nums=(1, 3, -1, -3, 5, 3, 6, 7), k: int = 3):
    nums = list(nums)
    n = len(nums)
    t = Tracer(nums, f"Sliding window maximum (k = {k})",
               "LeetCode 239  |  monotonic deque", LC239_CODE,
               slug="lc0239-window-maximum",
               legend={"idle": "not reached yet",
                       "window": "in the window / on the deque",
                       "focus": "current element",
                       "invalid": "popped, can never be a maximum",
                       "best": "the window maximum", "dim": "outside the window"})
    dq: deque[int] = deque()
    out: list[int] = []

    def st():
        return [("out", "[" + ",".join(map(str, out)) + "]")]

    t.snap(line=1, verdict="info",
           note="The deque holds indices whose values decrease from front to back. "
                "The front is always the maximum of the current window.",
           aux=_dq_aux(nums, dq), state=st(), hold=1.8)

    for right in range(n):
        left = max(0, right - k + 1)
        roles = window_roles(n, left, right - 1, focus=right)
        t.snap(roles, line=4,
               note=f"right = {right}, value {nums[right]}.",
               pointers=[("right", right)],
               aux=_dq_aux(nums, dq), state=st())

        while dq and nums[dq[-1]] <= nums[right]:
            j = dq.pop()
            roles = window_roles(n, left, right - 1, focus=right)
            roles[j] = "invalid"
            t.snap(roles, line=6, verdict="drop",
                   note=f"nums[{j}] = {nums[j]} is not bigger than {nums[right]} and sits "
                        f"further left, so it can never be a future maximum. Pop it.",
                   pointers=[("right", right)],
                   aux=_dq_aux(nums, dq + deque([j])), state=st(), hold=1.4)

        dq.append(right)
        t.snap(window_roles(n, left, right, focus=right), line=7,
               note=f"Push index {right}. The deque stays decreasing.",
               pointers=[("right", right)],
               aux=_dq_aux(nums, dq), state=st())

        if dq[0] <= right - k:
            expired = dq.popleft()
            roles = window_roles(n, left, right)
            roles[expired] = "invalid"
            t.snap(roles, line=9, verdict="drop",
                   note=f"Index {expired} fell out of the window [{left}, {right}]. "
                        f"Drop it from the front.",
                   pointers=[("left", left), ("right", right)],
                   bracket=(left, right, f"window k={k}"),
                   aux=_dq_aux(nums, dq), state=st(), hold=1.3)

        if right >= k - 1:
            out.append(nums[dq[0]])
            roles = window_roles(n, left, right)
            roles[dq[0]] = "best"
            t.snap(roles, line=11, verdict="record",
                   note=f"Window [{left}, {right}] is full. Its maximum is the deque front, "
                        f"nums[{dq[0]}] = {nums[dq[0]]}.",
                   pointers=[("left", left), ("right", right)],
                   bracket=(left, right, f"max {nums[dq[0]]}"), bracket_role="best",
                   aux=_dq_aux(nums, dq), state=st(), hold=1.4)

    t.snap([("dim")] * n, line=12, verdict="record",
           note=f"Answer: {out}. Each index is pushed once and popped once, so the whole "
                f"scan is O(n), not O(n·k).",
           aux=_dq_aux(nums, dq), state=st(), hold=2.2)
    return t.trace


# --------------------------------------------------------------------------- #
# LC 76 - minimum window substring (shrink while valid)
# --------------------------------------------------------------------------- #
LC76_CODE = """
def min_window(s, t):
    need = Counter(t)
    have = 0
    left = 0
    best = ""
    for right in range(len(s)):
        if need[s[right]] > 0:
            have += 1
        need[s[right]] -= 1
        while have == len(t):
            if not best or right-left+1 < len(best):
                best = s[left:right+1]
            need[s[left]] += 1
            if need[s[left]] > 0:
                have -= 1
            left += 1
    return best
"""


def lc76_min_window(s: str = "ADOBECODEBANC", target: str = "ABC"):
    n = len(s)
    tr = Tracer(list(s), "Minimum window substring",
                "LeetCode 76  |  grow to become valid, shrink while still valid",
                LC76_CODE, slug="lc0076-min-window",
                legend={"idle": "not reached yet", "window": "current window",
                        "focus": "the new character",
                        "valid": "covers every needed letter",
                        "best": "shortest valid window so far",
                        "dim": "left behind"})
    need = {c: target.count(c) for c in target}
    have = 0
    left = 0
    best = ""
    best_span = None

    def need_aux():
        return Aux(title="need  (positive = still missing, negative = surplus)", kind="chips",
                   chips=[(c, str(need[c])) for c in sorted(need)])

    def st():
        return [("have", f"{have}/{len(target)}"), ("best", best or "-")]

    tr.snap(line=1, verdict="info",
            note=f"Find the shortest window of \"{s}\" that contains every letter of "
                 f"\"{target}\". Grow right until the window is valid, then shrink left "
                 f"while it stays valid.",
            aux=need_aux(), state=st(), hold=2.2)

    for right in range(n):
        ch = s[right]
        wanted = ch in need
        if wanted and need[ch] > 0:
            have += 1
        if wanted:
            need[ch] -= 1

        roles = window_roles(n, left, right, focus=right,
                             inside="valid" if have == len(target) else "window")
        tr.snap(roles, line=9,
                note=(f"right = {right}, '{ch}' is one of the letters we need."
                      if wanted else
                      f"right = {right}, '{ch}' is not needed. Carry it along for now."),
                pointers=[("left", left), ("right", right)],
                bracket=(left, right, f"len {right - left + 1}"),
                bracket_role="valid" if have == len(target) else "window",
                aux=need_aux(), state=st(),
                hold=1.15 if wanted else 0.85)

        first_valid = True
        while have == len(target):
            size = right - left + 1
            if first_valid:
                roles = window_roles(n, left, right, inside="valid")
                tr.snap(roles, line=10, verdict="valid",
                        note=f"Window \"{s[left:right + 1]}\" now covers \"{target}\". "
                             f"It is valid, so try to make it shorter.",
                        pointers=[("left", left), ("right", right)],
                        bracket=(left, right, f"valid, len {size}"), bracket_role="valid",
                        aux=need_aux(), state=st(), hold=1.5)
                first_valid = False

            if not best or size < len(best):
                best = s[left:right + 1]
                best_span = (left, right)
                roles = window_roles(n, left, right, inside="best")
                tr.snap(roles, line=12, verdict="record",
                        note=f"\"{best}\" is the shortest valid window so far (length {size}).",
                        pointers=[("left", left), ("right", right)],
                        bracket=(left, right, f"best len {size}"), bracket_role="best",
                        aux=need_aux(), state=st(), hold=1.5)

            dropped = s[left]
            if dropped in need:
                need[dropped] += 1
                if need[dropped] > 0:
                    have -= 1
            left += 1
            still = have == len(target)
            roles = window_roles(n, left, right, inside="valid" if still else "window")
            tr.snap(roles, line=16, verdict=None if still else "drop",
                    note=(f"Drop '{dropped}' and move left to {left}. Still valid, keep shrinking."
                          if still else
                          f"Dropping '{dropped}' loses the last copy we needed. The window is "
                          f"no longer valid, so go back to growing right."),
                    pointers=[("left", left), ("right", right)],
                    bracket=(left, right, "shrinking") if left <= right else None,
                    bracket_role="valid" if still else "window",
                    aux=need_aux(), state=st(), hold=1.2)

    lo, hi = best_span
    roles = window_roles(n, lo, hi, inside="best", before="dim", after="dim")
    tr.snap(roles, line=17, verdict="record",
            note=f"Answer: \"{best}\". left and right each only move forward, "
                 f"so despite the inner loop the whole scan is O(n).",
            bracket=(lo, hi, f"answer \"{best}\""), bracket_role="best",
            state=[("best", best)], hold=2.4)
    return tr.trace


# --------------------------------------------------------------------------- #
# LC 713 - subarray product less than k (counting windows)
# --------------------------------------------------------------------------- #
LC713_CODE = """
def num_subarrays(nums, k):
    prod = 1
    left = 0
    ans = 0
    for right in range(len(nums)):
        prod *= nums[right]
        while prod >= k and left <= right:
            prod //= nums[left]
            left += 1
        ans += right - left + 1
    return ans
"""


def lc713_count_subarrays(nums=(10, 5, 2, 6, 3), k: int = 100):
    nums = list(nums)
    n = len(nums)
    t = Tracer(nums, f"Counting subarrays with product < {k}",
               "LeetCode 713  |  sliding window, shape 4 (count)", LC713_CODE,
               slug="lc0713-count-subarrays",
               legend={"idle": "not reached yet", "window": "current window",
                       "focus": "the new element",
                       "invalid": "product too big, dropped",
                       "best": "the subarrays counted this step",
                       "dim": "left behind"})
    prod = 1
    left = 0
    ans = 0

    t.snap(line=1, verdict="info",
           note=f"Instead of counting subarrays directly, count how many valid ones "
                f"END at each index. Add those up and you have the answer.",
           state=[("product", "1"), ("answer", "0")], hold=2.4)

    for right in range(n):
        prod *= nums[right]
        t.snap(window_roles(n, left, right - 1, focus=right), line=6,
               note=f"Multiply in nums[{right}] = {nums[right]}. Product of the window "
                    f"is now {prod}.",
               pointers=[("left", left), ("right", right)],
               bracket=(left, right, f"product {prod}") if right >= left else None,
               state=[("product", str(prod)), ("answer", str(ans))], hold=1.2)

        while prod >= k and left <= right:
            roles = window_roles(n, left, right, inside="invalid")
            t.snap(roles, line=7, verdict="invalid",
                   note=f"Product {prod} is not below {k}. This window is invalid, "
                        f"so shrink from the left.",
                   pointers=[("left", left), ("right", right)],
                   bracket=(left, right, "invalid"), bracket_role="invalid",
                   state=[("product", str(prod)), ("answer", str(ans))], hold=1.5)
            dropped = nums[left]
            prod //= dropped
            left += 1
            t.snap(window_roles(n, left, right), line=9,
                   note=f"Drop {dropped} at index {left - 1}. Product falls to {prod}.",
                   pointers=[("left", left), ("right", right)],
                   bracket=(left, right, f"product {prod}") if left <= right else None,
                   state=[("product", str(prod)), ("answer", str(ans))], hold=1.2)

        gained = right - left + 1
        ans += gained
        subs = ", ".join("[" + ",".join(str(v) for v in nums[s:right + 1]) + "]"
                         for s in range(left, right + 1))
        roles = window_roles(n, left, right, inside="best")
        t.snap(roles, line=10, verdict="count",
               note=f"Every start from {left} to {right} gives a valid subarray ending "
                    f"at {right}. That is {gained} of them: {subs}. Answer is now {ans}.",
               pointers=[("left", left), ("right", right)],
               bracket=(left, right, f"+{gained} subarrays"), bracket_role="best",
               state=[("product", str(prod)), ("answer", str(ans))], hold=2.2)

    t.snap(["dim"] * n, line=11, verdict="count",
           note=f"Answer: {ans}. This step only works because the constraint is "
                f"shrink-safe: if a window is valid, every window inside it is too.",
           state=[("answer", str(ans))], hold=2.6)
    return t.trace


# --------------------------------------------------------------------------- #
# LC 424 - longest repeating character replacement (shift, do not shrink)
# --------------------------------------------------------------------------- #
LC424_CODE = """
def character_replacement(s, k):
    count = {}
    max_freq = 0
    left = 0
    best = 0
    for right in range(len(s)):
        count[s[right]] = count.get(s[right], 0) + 1
        max_freq = max(max_freq, count[s[right]])
        if right - left + 1 - max_freq > k:
            count[s[left]] -= 1
            left += 1
        best = max(best, right - left + 1)
    return best
"""


def lc424_high_water_mark(s: str = "AABABBA", k: int = 1):
    n = len(s)
    t = Tracer(list(s), f"Longest repeating character replacement (k = {k})",
               "LeetCode 424  |  the window shifts, it never shrinks", LC424_CODE,
               slug="lc0424-high-water-mark",
               legend={"idle": "not reached yet", "window": "current window",
                       "focus": "the new character",
                       "invalid": "dropped as the window shifts",
                       "best": "longest window so far", "dim": "left behind"})
    count: dict[str, int] = {}
    max_freq = 0
    left = 0
    best = 0
    best_span = (0, 0)

    def chips():
        return Aux(title="count  (characters inside the window)", kind="chips",
                   chips=[(c, str(v)) for c, v in sorted(count.items()) if v > 0])

    t.snap(line=1, verdict="info",
           note=f"Keep the most common character, replace the rest. A window is legal "
                f"when its length minus the count of its most common character is at "
                f"most {k}.",
           aux=chips(), state=[("k", str(k)), ("best", "0")], hold=3.0)

    for right in range(n):
        ch = s[right]
        count[ch] = count.get(ch, 0) + 1
        stale = max_freq > max(count.values())
        max_freq = max(max_freq, count[ch])
        size = right - left + 1
        need = size - max_freq
        t.snap(window_roles(n, left, right - 1, focus=right), line=8,
               note=f"'{ch}' enters. Window is {size} long, its most common character "
                    f"appears {max_freq} times, so {size} - {max_freq} = {need} "
                    f"replacements would be needed.",
               pointers=[("left", left), ("right", right)],
               bracket=(left, right, f"len {size}"),
               aux=chips(),
               state=[("max_freq", str(max_freq)), ("to replace", str(need)),
                      ("k", str(k)), ("best", str(best))], hold=1.6)

        if need > k:
            dropped = s[left]
            roles = window_roles(n, left, right)
            roles[left] = "invalid"
            t.snap(roles, line=9, verdict="drop",
                   note=f"{need} > {k}, so this window is not legal. Drop '{dropped}' and "
                        f"move left by one. Note what does NOT happen: the window does not "
                        f"keep shrinking, it slides one step and keeps its length.",
                   pointers=[("left", left), ("right", right)],
                   bracket=(left, right, f"len {size}"), bracket_role="invalid",
                   aux=chips(),
                   state=[("max_freq", str(max_freq)), ("to replace", str(need)),
                          ("k", str(k)), ("best", str(best))], hold=2.8)
            count[dropped] -= 1
            left += 1

        size = right - left + 1
        is_best = size > best
        if is_best:
            best = size
            best_span = (left, right)
        t.snap(window_roles(n, left, right, inside="best" if is_best else "window"),
               line=12, verdict="record" if is_best else None,
               note=(f"Window [{left}, {right}] is {size} long. "
                     + ("New best." if is_best else
                        f"Same length as before, so best stays {best}.")),
               pointers=[("left", left), ("right", right)],
               bracket=(left, right, f"len {size}"),
               bracket_role="best" if is_best else "window",
               aux=chips(),
               state=[("max_freq", str(max_freq)), ("k", str(k)), ("best", str(best))],
               hold=1.5 if is_best else 1.1)

    lo, hi = best_span
    roles = window_roles(n, lo, hi, inside="best", before="dim", after="dim")
    t.snap(roles, line=13, verdict="record",
           note=f"Answer: {best}. max_freq is never lowered when the window moves. A stale "
                f"value only makes the check stricter, so the window shifts when it did "
                f"not have to. It never lets a too-long window through, which is the only "
                f"thing that would break the answer.",
           bracket=(lo, hi, f"answer len {best}"), bracket_role="best",
           state=[("best", str(best))], hold=3.6)
    return t.trace


# --------------------------------------------------------------------------- #
# LC 424 - longest repeating character replacement (shift, don't shrink)
# --------------------------------------------------------------------------- #
LC424_CODE = """
def character_replacement(s, k):
    count = defaultdict(int)
    max_freq = 0
    left = 0
    for right, ch in enumerate(s):
        count[ch] += 1
        max_freq = max(max_freq, count[ch])
        if (right - left + 1) - max_freq > k:
            count[s[left]] -= 1
            left += 1
    return len(s) - left
"""


def lc424_shift_dont_shrink(s: str = "AABABBA", k: int = 1):
    n = len(s)
    t = Tracer(list(s), f"Longest repeating character replacement (k = {k})",
               "LeetCode 424  |  the window shifts, it never shrinks", LC424_CODE,
               slug="lc0424-shift-dont-shrink",
               legend={"idle": "not reached yet", "window": "current window",
                       "focus": "the character just added",
                       "invalid": "dropped as the window shifts",
                       "best": "the window at its longest", "dim": "left behind"})
    count: dict[str, int] = {}
    max_freq = 0
    left = 0
    widest = 0

    def chips():
        return Aux(title="count  (characters inside the window)", kind="chips",
                   chips=[(c, str(v)) for c, v in sorted(count.items()) if v > 0])

    t.snap(line=1, verdict="info",
           note=f"Keep the most common character, replace the rest. A window is legal "
                f"while its length minus the count of its most common character is at "
                f"most {k}. Watch the window length: it never goes down.",
           aux=chips(), state=[("k", str(k)), ("length", "0")], hold=3.2)

    for right in range(n):
        ch = s[right]
        count[ch] = count.get(ch, 0) + 1
        max_freq = max(max_freq, count[ch])
        size = right - left + 1
        need = size - max_freq
        widest = max(widest, size)
        legal = need <= k
        t.snap(window_roles(n, left, right - 1, focus=right,
                            inside="best" if legal and size >= widest else "window"),
               line=7,
               note=f"'{ch}' enters. Length {size}, most common character appears "
                    f"{max_freq} times, so {size} - {max_freq} = {need} replacement"
                    f"{'' if need == 1 else 's'} would be needed.",
               pointers=[("left", left), ("right", right)],
               bracket=(left, right, f"length {size}"),
               bracket_role="best" if legal else "window",
               aux=chips(),
               state=[("max_freq", str(max_freq)), ("need", str(need)),
                      ("k", str(k)), ("length", str(size))],
               hold=1.5 if legal else 1.2)

        if need > k:
            dropped = s[left]
            roles = window_roles(n, left, right)
            roles[left] = "invalid"
            t.snap(roles, line=9, verdict="drop",
                   note=f"{need} > {k}, so this window is not legal. Drop '{dropped}' and "
                        f"move left by one. Notice what does not happen: there is no "
                        f"while loop, so the window slides one step and keeps its length "
                        f"of {size}.",
                   pointers=[("left", left), ("right", right)],
                   bracket=(left, right, f"length {size}"), bracket_role="invalid",
                   aux=chips(),
                   state=[("max_freq", str(max_freq)), ("need", str(need)),
                          ("k", str(k)), ("length", str(size))], hold=3.0)
            count[dropped] -= 1
            left += 1
            t.snap(window_roles(n, left, right), line=10,
                   note=f"Same length, one step to the right. The answer cannot improve "
                        f"this step, and that is the whole cost of a stale max_freq.",
                   pointers=[("left", left), ("right", right)],
                   bracket=(left, right, f"length {right - left + 1}"),
                   aux=chips(),
                   state=[("max_freq", str(max_freq)), ("k", str(k)),
                          ("length", str(right - left + 1))], hold=1.8)

    lo, hi = left, n - 1
    roles = window_roles(n, lo, hi, inside="best", before="dim", after="dim")
    t.snap(roles, line=11, verdict="record",
           note=f"Answer: {n - left}. Because the window only ever shifts or grows, its "
                f"final length is its maximum, so no max() is needed. A stale max_freq "
                f"only makes the test stricter; it can never let an illegal window "
                f"through, which is the only thing that would break correctness.",
           bracket=(lo, hi, f"length {n - left}"), bracket_role="best",
           state=[("answer", str(n - left))], hold=3.8)
    return t.trace
