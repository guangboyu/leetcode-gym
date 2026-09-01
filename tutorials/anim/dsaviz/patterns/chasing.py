"""Chasing pointers: a write pointer that lags a read pointer, and the
three-way partition it generalises to."""
from __future__ import annotations

from ..model import Aux, Tracer

LC283_CODE = """
def move_zeroes(nums):
    write = 0
    for read in range(len(nums)):
        if nums[read] != 0:
            nums[write] = nums[read]
            write += 1
    while write < len(nums):
        nums[write] = 0
        write += 1
"""


def lc283_move_zeroes(nums=(0, 1, 0, 3, 12, 0, 5)):
    a = list(nums)
    n = len(a)
    t = Tracer(a, "Move zeroes to the end",
               "LeetCode 283  |  chasing pointers, read and write", LC283_CODE,
               slug="lc0283-read-write",
               legend={"valid": "finished answer, [0, write)",
                       "dim": "already copied forward, safe to overwrite",
                       "idle": "not looked at yet",
                       "focus": "the element read is judging",
                       "invalid": "a zero, it does not earn a slot",
                       "best": "just written"})
    write = 0

    def roles(read=None, written=None, drop=None):
        out = []
        for i in range(n):
            if i < write:
                out.append("valid")
            elif read is not None and i < read:
                out.append("dim")
            else:
                out.append("idle")
        if read is not None and read < n:
            out[read] = "invalid" if drop else "focus"
        if written is not None:
            out[written] = "best"
        return out

    def st():
        return [("write", str(write))]

    t.snap(["idle"] * n, line=2, verdict="info",
           note="read visits everything. write only advances when an element earns its "
                "place. Because write never gets ahead of read, overwriting in place can "
                "never destroy something we still need.",
           state=st(), cells=a, hold=2.6)

    for read in range(n):
        keep = a[read] != 0
        t.snap(roles(read=read, drop=not keep), line=4,
               verdict=None if keep else "drop",
               note=(f"nums[{read}] = {a[read]} is not zero, so it earns a slot."
                     if keep else
                     f"nums[{read}] = 0. Zeros do not earn a slot, so write stays at "
                     f"{write} and the gap between the pointers grows."),
               pointers=[("write", write), ("read", read)],
               bracket=(write, read - 1, "already copied forward") if read > write else None,
               bracket_role="dim" if read > write else "window",
               state=st(), cells=a, hold=1.5)

        if keep:
            a[write] = a[read]
            write += 1
            t.snap(roles(read=read, written=write - 1), line=6, verdict="valid",
                   note=f"Copy it to index {write - 1}. Everything left of write is now "
                        f"final answer.",
                   pointers=[("write", write), ("read", read)],
                   bracket=(0, write - 1, f"finished, length {write}"), bracket_role="valid",
                   state=st(), cells=a, hold=1.3)

    tail_from = write
    while write < n:
        a[write] = 0
        write += 1
    out = ["valid"] * tail_from + ["best"] * (n - tail_from)
    t.snap(out, line=8, verdict="record",
           note=f"Fill the tail with zeroes. Answer: {a}. Every element was read once and "
                f"written at most once.",
           bracket=(0, tail_from - 1, "survivors, in order"), bracket_role="valid",
           cells=a, hold=2.6)
    return t.trace


LC75_CODE = """
def sort_colors(nums):
    low, mid, high = 0, 0, len(nums) - 1
    while mid <= high:
        if nums[mid] == 0:
            nums[low], nums[mid] = nums[mid], nums[low]
            low += 1
            mid += 1
        elif nums[mid] == 2:
            nums[mid], nums[high] = nums[high], nums[mid]
            high -= 1
        else:
            mid += 1
"""


def lc75_sort_colors(nums=(2, 0, 2, 1, 1, 0)):
    a = list(nums)
    n = len(a)
    t = Tracer(a, "Sort colors, the Dutch national flag",
               "LeetCode 75  |  three pointers, four regions", LC75_CODE,
               slug="lc0075-sort-colors",
               legend={"valid": "settled 0s, [0, low)",
                       "window": "settled 1s, [low, mid)",
                       "idle": "unknown, [mid, high]",
                       "best": "settled 2s, (high, n)",
                       "focus": "the value mid is judging",
                       "invalid": "swapped in from the right, still unknown"})
    low = mid = 0
    high = n - 1

    def roles(focus=None, unknown=None):
        out = []
        for i in range(n):
            if i < low:
                out.append("valid")
            elif i < mid:
                out.append("window")
            elif i <= high:
                out.append("idle")
            else:
                out.append("best")
        if focus is not None and 0 <= focus < n:
            out[focus] = "focus"
        if unknown is not None and 0 <= unknown < n:
            out[unknown] = "invalid"
        return out

    def st():
        return []

    t.snap(["idle"] * n, line=2, verdict="info",
           note="Four regions, three pointers: settled 0s, settled 1s, an unknown middle, "
                "and settled 2s. The loop runs until the unknown middle is empty.",
           pointers=[("low", 0), ("mid", 0), ("high", n - 1)], state=st(), cells=a, hold=2.6)

    while mid <= high:
        v = a[mid]
        t.snap(roles(focus=mid), line=3,
               note=f"mid is looking at {v}.",
               pointers=[("low", low), ("mid", mid), ("high", high)],
               bracket=(mid, high, "unknown") if mid <= high else None,
               state=st(), cells=a, hold=1.1)

        if v == 0:
            a[low], a[mid] = a[mid], a[low]
            low += 1
            mid += 1
            t.snap(roles(), line=7, verdict="valid",
                   note=f"A 0 belongs at the front. Swap it to index {low - 1}. The value "
                        f"that came back has already been examined, so mid is safe to "
                        f"advance too.",
                   pointers=[("low", low), ("mid", mid), ("high", high)],
                   state=st(), cells=a, hold=2.0)
        elif v == 2:
            a[mid], a[high] = a[high], a[mid]
            high -= 1
            t.snap(roles(unknown=mid), line=10, verdict="invalid",
                   note=f"A 2 belongs at the back. Swap it to index {high + 1}. The value "
                        f"that came back arrived from the unknown region and has never "
                        f"been examined, so mid must NOT advance. This is the asymmetry "
                        f"people get wrong.",
                   pointers=[("low", low), ("mid", mid), ("high", high)],
                   state=st(), cells=a, hold=2.8)
        else:
            mid += 1
            t.snap(roles(), line=12,
                   note="A 1 is already in the right region. Just step over it.",
                   pointers=[("low", low), ("mid", mid), ("high", high)],
                   state=st(), cells=a, hold=1.2)

    out = ["valid"] * low + ["window"] * (mid - low) + ["best"] * (n - mid)
    t.snap(out, line=12, verdict="record",
           note=f"mid passed high, so the unknown region is empty and the array is sorted: "
                f"{a}. One pass, no counting, no second loop.",
           state=st(), cells=a, hold=2.6)
    return t.trace
