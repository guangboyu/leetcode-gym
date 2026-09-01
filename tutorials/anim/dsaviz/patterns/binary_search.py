"""Binary search: half the search space disappears every probe."""
from __future__ import annotations

from ..model import Tracer

LC704_CODE = """
def search(nums, target):
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if nums[mid] == target:
            return mid
        if nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1
"""


def _roles(n, lo, hi, mid=None, dead=None):
    r = ["dim"] * n
    for i in range(max(0, lo), min(n, hi + 1)):
        r[i] = "window"
    if dead:
        for i in range(max(0, dead[0]), min(n, dead[1] + 1)):
            r[i] = "invalid"
    if mid is not None and 0 <= mid < n:
        r[mid] = "focus"
    return r


def lc704_binary_search(nums=(-1, 0, 3, 5, 9, 12, 15, 18, 21, 27), target: int = 15):
    nums = list(nums)
    n = len(nums)
    t = Tracer(nums, f"Binary search (target = {target})",
               "LeetCode 704  |  halve the search space", LC704_CODE,
               slug="lc0704-binary-search",
               legend={"window": "still possible", "focus": "mid, the probe",
                       "invalid": "ruled out by this probe", "best": "found it",
                       "dim": "ruled out earlier"})
    lo, hi = 0, n - 1
    probes = 0

    t.snap(_roles(n, lo, hi), line=2, verdict="info",
           note=f"{n} candidates. Every probe throws away half of what is left, so the "
                f"answer is at most {n.bit_length()} probes away, not {n}.",
           bracket=(lo, hi, f"{hi - lo + 1} candidates"),
           state=[("target", str(target)), ("probes", "0")], hold=2.2)

    while lo <= hi:
        mid = (lo + hi) // 2
        probes += 1
        t.snap(_roles(n, lo, hi, mid=mid), line=4,
               note=f"mid = ({lo} + {hi}) // 2 = {mid}. Check nums[{mid}] = {nums[mid]}.",
               pointers=[("lo", lo), ("mid", mid), ("hi", hi)],
               bracket=(lo, hi, f"{hi - lo + 1} candidates"),
               state=[("target", str(target)), ("probes", str(probes))], hold=1.3)

        if nums[mid] == target:
            r = _roles(n, lo, hi)
            r = ["dim"] * n
            r[mid] = "best"
            t.snap(r, line=6, verdict="record",
                   note=f"nums[{mid}] = {target}. Found it in {probes} probes.",
                   pointers=[("mid", mid)],
                   state=[("target", str(target)), ("probes", str(probes))], hold=2.4)
            return t.trace

        if nums[mid] < target:
            t.snap(_roles(n, lo, hi, mid=mid, dead=(lo, mid - 1)), line=8, verdict="drop",
                   note=f"{nums[mid]} < {target}, and everything left of mid is even smaller. "
                        f"Mid and its whole left side are out; the search space becomes "
                        f"{mid + 1}..{hi}.",
                   pointers=[("lo", lo), ("mid", mid), ("hi", hi)],
                   state=[("target", str(target)), ("probes", str(probes))], hold=1.6)
            lo = mid + 1
        else:
            t.snap(_roles(n, lo, hi, mid=mid, dead=(mid + 1, hi)), line=10, verdict="drop",
                   note=f"{nums[mid]} > {target}, and everything right of mid is even bigger. "
                        f"Mid and its whole right side are out; the search space becomes "
                        f"{lo}..{mid - 1}.",
                   pointers=[("lo", lo), ("mid", mid), ("hi", hi)],
                   state=[("target", str(target)), ("probes", str(probes))], hold=1.6)
            hi = mid - 1

    t.snap(["dim"] * n, line=11, note=f"{target} is not in the array.", hold=2.0)
    return t.trace
