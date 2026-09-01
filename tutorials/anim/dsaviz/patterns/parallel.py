"""Parallel pointers: one index per sorted sequence."""
from __future__ import annotations

from ..model import Aux, Tracer

LC88_CODE = """
def merge(nums1, m, nums2, n):
    i, j, w = m - 1, n - 1, m + n - 1
    while j >= 0:
        if i >= 0 and nums1[i] > nums2[j]:
            nums1[w] = nums1[i]
            i -= 1
        else:
            nums1[w] = nums2[j]
            j -= 1
        w -= 1
"""


def lc88_merge_sorted(a=(1, 2, 3), b=(2, 5, 6)):
    m, n = len(a), len(b)
    nums1 = list(a) + [0] * n
    nums2 = list(b)
    total = m + n
    t = Tracer(nums1, "Merge two sorted arrays, filling backward",
               "LeetCode 88  |  parallel pointers, largest first", LC88_CODE,
               slug="lc0088-merge-sorted",
               legend={"window": "still to be merged", "focus": "the candidate from nums1",
                       "best": "just written", "valid": "final, in place",
                       "idle": "empty slot waiting", "dim": "already consumed"})
    i, j, w = m - 1, n - 1, total - 1

    def show():
        return [str(v) if (k < m or k > w) else "_" for k, v in enumerate(nums1)]

    def roles(cur=None, wrote=None):
        out = []
        for k in range(total):
            if k > w:
                out.append("valid")
            elif k <= i:
                out.append("window")
            else:
                out.append("idle")
        if cur is not None and 0 <= cur < total:
            out[cur] = "focus"
        if wrote is not None:
            out[wrote] = "best"
        return out

    def aux(cur=False):
        return Aux(title="nums2  (merged in from the right)", kind="cells",
                   cells=[str(v) for v in nums2],
                   roles=["dim" if k > j else ("focus" if (cur and k == j) else "window")
                          for k in range(n)],
                   subs=[f"j={k}" if k == j else "" for k in range(n)])

    t.snap(roles(), line=2, verdict="info",
           note="nums1 has n empty slots at the end. Filling forward would clobber values "
                "that have not been read yet, so fill backward: take the larger of the two "
                "tails and put it in the last free slot.",
           pointers=[("i", i), ("w", w)], aux=aux(), cells=show(), hold=2.8)

    while j >= 0:
        take_a = i >= 0 and nums1[i] > nums2[j]
        if take_a:
            t.snap(roles(cur=i), line=4,
                   note=f"nums1[{i}] = {nums1[i]} is larger than nums2[{j}] = {nums2[j]}, "
                        f"so it takes the last free slot.",
                   pointers=[("i", i), ("w", w)], aux=aux(cur=True), cells=show(),
                   hold=1.5)
            nums1[w] = nums1[i]
            i -= 1
        else:
            t.snap(roles(cur=i if i >= 0 else None), line=8,
                   note=(f"nums2[{j}] = {nums2[j]} is at least as large, so it goes next."
                         if i >= 0 else
                         f"nums1 is exhausted, so the rest of nums2 copies straight in."),
                   pointers=[("i", i), ("w", w)] if i >= 0 else [("w", w)],
                   aux=aux(cur=True), cells=show(), hold=1.5)
            nums1[w] = nums2[j]
            j -= 1
        written = w
        w -= 1
        t.snap(roles(wrote=written), line=10, verdict="valid",
               note=f"Write {nums1[written]} at index {written}. The write pointer is still "
                    f"ahead of both read pointers, which is why nothing was destroyed.",
               pointers=[("i", i), ("w", w)] if i >= 0 else [("w", w)],
               aux=aux(), cells=show(), hold=1.4)

    t.snap(["valid"] * total, line=10, verdict="record",
           note=f"nums2 is drained, so whatever is left of nums1 is already sitting in the "
                f"right place. Result: {nums1}.",
           aux=aux(), cells=[str(v) for v in nums1], hold=2.8)
    return t.trace
