"""Prefix sums plus a hash map: subarray questions in one pass."""
from __future__ import annotations

from ..model import Aux, Tracer

LC560_CODE = """
def subarray_sum(nums, k):
    count = 0
    total = 0
    seen = {0: 1}
    for right in range(len(nums)):
        total += nums[right]
        count += seen.get(total - k, 0)
        seen[total] = seen.get(total, 0) + 1
    return count
"""


def lc560_subarray_sum(nums=(1, 2, 3, -1, 2, 1), k: int = 3):
    nums = list(nums)
    n = len(nums)
    t = Tracer(nums, f"Subarray sum equals k  (k = {k})",
               "LeetCode 560  |  prefix sum + hash map", LC560_CODE,
               slug="lc0560-prefix-sum",
               legend={"idle": "not reached yet", "window": "prefix recorded",
                       "focus": "current index",
                       "best": "a subarray summing to k", "dim": "behind us"})

    total = 0
    count = 0
    seen = {0: 1}
    prefix_at = {0: [-1]}      # prefix value -> list of end indices
    shown = [""] * n

    def pref_aux(hot=()):
        return Aux(title="prefix  (sum of everything up to and including this index)",
                   kind="aligned", cells=list(shown),
                   roles=["focus" if i in hot else ("window" if shown[i] else "idle")
                          for i in range(n)])

    def seen_aux(hot=None):
        return Aux(title="seen  (how many times each prefix has appeared, incl. the empty prefix 0)",
                   kind="chips",
                   chips=[(str(p), f"x{c}" if c > 1 else "x1") for p, c in seen.items()])

    t.snap(line=4, verdict="info",
           note=f"A subarray sums to {k} exactly when two prefix sums differ by {k}. "
                f"So at each index, ask how many earlier prefixes equal total - {k}.",
           aux=[pref_aux(), seen_aux()],
           state=[("total", "0"), ("count", "0")], hold=2.4)

    for right in range(n):
        total += nums[right]
        shown[right] = str(total)
        roles = ["dim"] * right + ["focus"] + ["idle"] * (n - right - 1)
        t.snap(roles, line=6,
               note=f"Add nums[{right}] = {nums[right]}. Prefix sum up to index {right} "
                    f"is {total}.",
               pointers=[("right", right)],
               aux=[pref_aux(hot={right}), seen_aux()],
               state=[("total", str(total)), ("count", str(count))], hold=1.2)

        want = total - k
        hits = seen.get(want, 0)
        if hits:
            starts = [p + 1 for p in prefix_at.get(want, [])]
            lo = starts[-1]
            roles = ["dim"] * n
            for i in range(lo, right + 1):
                roles[i] = "best"
            count += hits
            t.snap(roles, line=7, verdict="record",
                   note=f"total - k = {total} - {k} = {want}, and {want} has appeared "
                        f"{hits} time(s) before. That is {hits} subarray(s) ending at "
                        f"index {right} summing to {k}, e.g. indices {lo}..{right}.",
                   pointers=[("right", right)],
                   bracket=(lo, right, f"sum {k}"), bracket_role="best",
                   aux=[pref_aux(hot={right}), seen_aux()],
                   state=[("total", str(total)), ("count", str(count))], hold=2.2)
        else:
            roles = ["dim"] * right + ["window"] + ["idle"] * (n - right - 1)
            t.snap(roles, line=7,
                   note=f"total - k = {total} - {k} = {want}, which has never been a prefix "
                        f"sum. No subarray ends here.",
                   pointers=[("right", right)],
                   aux=[pref_aux(hot={right}), seen_aux()],
                   state=[("total", str(total)), ("count", str(count))], hold=1.4)

        seen[total] = seen.get(total, 0) + 1
        prefix_at.setdefault(total, []).append(right)
        t.snap(["dim"] * (right + 1) + ["idle"] * (n - right - 1), line=8,
               note=f"Record prefix {total} so later indices can find it.",
               pointers=[("right", right)],
               aux=[pref_aux(), seen_aux()],
               state=[("total", str(total)), ("count", str(count))], hold=0.9)

    t.snap(["dim"] * n, line=9, verdict="record",
           note=f"Answer: {count} subarrays sum to {k}. One pass, O(n) time, and no nested "
                f"loop over every start and end.",
           aux=[pref_aux(), seen_aux()],
           state=[("count", str(count))], hold=2.4)
    return t.trace
