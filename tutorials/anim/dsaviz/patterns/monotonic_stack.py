"""Monotonic stack: each element waits on the stack until something bigger arrives."""
from __future__ import annotations

from ..model import Aux, Tracer

LC739_CODE = """
def daily_temperatures(temps):
    out = [0] * len(temps)
    stack = []          # indices, temps decreasing
    for i in range(len(temps)):
        while stack and temps[stack[-1]] < temps[i]:
            j = stack.pop()
            out[j] = i - j
        stack.append(i)
    return out
"""


def lc739_daily_temperatures(temps=(73, 74, 75, 71, 69, 72, 76, 73)):
    temps = list(temps)
    n = len(temps)
    t = Tracer(temps, "Daily temperatures",
               "LeetCode 739  |  monotonic stack (next greater element)", LC739_CODE,
               slug="lc0739-monotonic-stack",
               legend={"idle": "not reached yet", "window": "waiting on the stack",
                       "focus": "today", "valid": "answered earlier",
                       "invalid": "being popped",
                       "best": "just answered", "dim": "not on the stack"})
    stack: list[int] = []
    out = [0] * n

    def stack_aux(extra=None):
        idx = stack + ([extra] if extra is not None else [])
        return Aux(title="stack  (indices waiting for a warmer day)", kind="cells",
                   cells=[str(temps[i]) for i in idx],
                   roles=["window"] * (len(idx) - 1) + (["invalid"] if extra is not None
                                                        else ["focus"] if idx else []),
                   subs=[f"i={i}" for i in idx])

    def out_aux(hot=()):
        return Aux(title="answer  (days to wait)", kind="aligned",
                   cells=[str(v) for v in out],
                   roles=["best" if i in hot else ("valid" if out[i] else "dim")
                          for i in range(n)])

    t.snap(line=3, verdict="info",
           note="Walk left to right. An index stays on the stack until a warmer day shows up. "
                "The stack is always decreasing, so the top is the one a warm day resolves first.",
           aux=[stack_aux(), out_aux()], hold=2.2)

    for i in range(n):
        roles = ["dim" if k in stack else "idle" for k in range(n)]
        for k in stack:
            roles[k] = "window"
        for k in range(n):
            if out[k]:
                roles[k] = "valid"
        roles[i] = "focus"
        t.snap(roles, line=4,
               note=f"Day {i}, temperature {temps[i]}.",
               pointers=[("i", i)], aux=[stack_aux(), out_aux()])

        resolved = []
        while stack and temps[stack[-1]] < temps[i]:
            j = stack.pop()
            out[j] = i - j
            resolved.append(j)
            r = ["dim"] * n
            for k in stack:
                r[k] = "window"
            for k in range(n):
                if out[k] and k not in resolved:
                    r[k] = "valid"
            for k in resolved:
                r[k] = "best"
            r[i] = "focus"
            t.snap(r, line=7, verdict="record",
                   note=f"Day {i} ({temps[i]}) is warmer than day {j} ({temps[j]}). "
                        f"Day {j} waited {i - j} day(s). Pop it.",
                   pointers=[("i", i)],
                   aux=[stack_aux(), out_aux(hot=set(resolved))], hold=1.5)

        stack.append(i)
        roles = ["dim"] * n
        for k in stack:
            roles[k] = "window"
        for k in range(n):
            if out[k]:
                roles[k] = "valid"
        roles[i] = "focus"
        t.snap(roles, line=8,
               note=f"Nothing warmer than {temps[i]} on the stack now. Push day {i} and "
                    f"let it wait.",
               pointers=[("i", i)], aux=[stack_aux(), out_aux()], hold=1.1)

    roles = ["valid" if out[k] else "dim" for k in range(n)]
    t.snap(roles, line=9, verdict="record",
           note=f"Answer: {out}. Indices still on the stack never found a warmer day, so they "
                f"keep 0. Each index is pushed once and popped once: O(n).",
           aux=[stack_aux(), out_aux()], hold=2.4)
    return t.trace
