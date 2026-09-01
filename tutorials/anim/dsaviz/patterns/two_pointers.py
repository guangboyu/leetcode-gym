"""Two pointers converging from both ends."""
from __future__ import annotations

from ..model import Tracer

LC167_CODE = """
def two_sum(nums, target):
    lo, hi = 0, len(nums) - 1
    while lo < hi:
        total = nums[lo] + nums[hi]
        if total == target:
            return [lo + 1, hi + 1]
        if total < target:
            lo += 1
        else:
            hi -= 1
    return []
"""


def _roles(n, lo, hi, focus=(), dead=()):
    r = ["dim"] * n
    for i in range(max(0, lo), min(n, hi + 1)):
        r[i] = "idle"
    for i in focus:
        if 0 <= i < n:
            r[i] = "focus"
    for i in dead:
        if 0 <= i < n:
            r[i] = "invalid"
    return r


def lc167_two_sum_sorted(nums=(2, 3, 5, 8, 11, 15, 18), target: int = 19):
    nums = list(nums)
    n = len(nums)
    t = Tracer(nums, f"Two sum on a sorted array (target = {target})",
               "LeetCode 167  |  two pointers from both ends", LC167_CODE,
               slug="lc0167-two-pointers",
               legend={"idle": "still possible", "focus": "the pair being tested",
                       "invalid": "just ruled out", "best": "the answer",
                       "dim": "ruled out earlier"})
    lo, hi = 0, n - 1

    t.snap(line=2, verdict="info",
           note="The array is sorted, so the sum only has one way to grow and one way to "
                "shrink: move lo right to grow, move hi left to shrink.",
           state=[("target", str(target))], hold=2.0)

    while lo < hi:
        total = nums[lo] + nums[hi]
        t.snap(_roles(n, lo, hi, focus=(lo, hi)), line=4,
               note=f"nums[{lo}] + nums[{hi}] = {nums[lo]} + {nums[hi]} = {total}.",
               pointers=[("lo", lo), ("hi", hi)],
               bracket=(lo, hi, "search space"),
               state=[("target", str(target)), ("sum", str(total))], hold=1.2)

        if total == target:
            r = _roles(n, lo, hi, focus=())
            r[lo] = r[hi] = "best"
            t.snap(r, line=6, verdict="record",
                   note=f"{nums[lo]} + {nums[hi]} = {target}. Answer: indices {lo} and {hi} "
                        f"(1-based {lo + 1} and {hi + 1}).",
                   pointers=[("lo", lo), ("hi", hi)],
                   bracket=(lo, hi, "found"), bracket_role="best",
                   state=[("target", str(target)), ("sum", str(total))], hold=2.4)
            return t.trace

        if total < target:
            t.snap(_roles(n, lo, hi, focus=(hi,), dead=(lo,)), line=8, verdict="drop",
                   note=f"The sum {total} is below {target}. nums[{lo}] = {nums[lo]} is the "
                        f"smallest value left, so even paired with the largest one it falls "
                        f"short. Discard it and move lo to {lo + 1}.",
                   pointers=[("lo", lo), ("hi", hi)],
                   state=[("target", str(target)), ("sum", str(total))], hold=1.5)
            lo += 1
        else:
            t.snap(_roles(n, lo, hi, focus=(lo,), dead=(hi,)), line=10, verdict="drop",
                   note=f"The sum {total} is above {target}. nums[{hi}] = {nums[hi]} is the "
                        f"largest value left, so even paired with the smallest one it "
                        f"overshoots. Discard it and move hi to {hi - 1}.",
                   pointers=[("lo", lo), ("hi", hi)],
                   state=[("target", str(target)), ("sum", str(total))], hold=1.5)
            hi -= 1

    t.snap(["dim"] * n, line=11, note="No pair adds up to the target.", hold=2.0)
    return t.trace
