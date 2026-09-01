"""Floyd's cycle detection on a rho-shaped linked list."""
from __future__ import annotations

from ..model import Tracer

LC142_CODE = """
def detect_cycle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:
            slow = head
            while slow is not fast:
                slow = slow.next
                fast = fast.next
            return slow
    return None
"""


def lc142_floyd(values=(3, 7, 1, 9, 4, 6, 2, 8), tail: int = 3):
    vals = list(values)
    n = len(vals)
    a = tail                      # nodes before the cycle
    c = n - a                     # cycle length
    nxt = lambda i: i + 1 if i < n - 1 else a

    t = Tracer(vals, "Floyd's cycle detection",
               "LeetCode 142  |  slow and fast, then find where the cycle starts",
               LC142_CODE, slug="lc0142-floyd-cycle",
               graph=(n, a),
               legend={"idle": "not visited", "dim": "visited",
                       "focus": "a pointer is standing here",
                       "valid": "proven, but not the answer",
                       "best": "the cycle entry, the answer"})

    seen: set[int] = set()

    def roles(marks: dict[int, str] | None = None):
        out = ["dim" if i in seen else "idle" for i in range(n)]
        for i, r in (marks or {}).items():
            out[i] = r
        return out

    slow = fast = 0
    seen.add(0)
    t.snap(roles({0: "focus"}), line=2, verdict="info",
           note="Both pointers start at the head. fast moves two steps for every one of "
                "slow, so fast closes the gap by exactly one node per move. Inside a "
                "cycle a gap that shrinks by one every move must reach zero.",
           pointers=[("slow", 0), ("fast", 0)],
           state=[("phase", "1, find a meeting point")], hold=3.0)

    step = 0
    while True:
        slow = nxt(slow)
        fast = nxt(nxt(fast))
        seen.add(slow)
        seen.add(fast)
        step += 1
        if slow == fast:
            break
        gap = (fast - slow) % n if fast >= a and slow >= a else None
        t.snap(roles({slow: "focus", fast: "focus"}), line=5,
               note=(f"Move {step}. slow is on {vals[slow]}, fast is on {vals[fast]}."
                     + (f" Both are inside the cycle now, {(fast - slow) % c} nodes apart."
                        if slow >= a and fast >= a else "")),
               pointers=[("slow", slow), ("fast", fast)],
               state=[("phase", "1, find a meeting point"), ("moves", str(step))],
               hold=1.5)

    meet = slow
    b = meet - a
    t.snap(roles({meet: "valid"}), line=6, verdict="valid",
           note=f"They meet on node {vals[meet]}. A meeting proves a cycle exists, but "
                f"this node is not the answer: it is {b} steps past the entry, not the "
                f"entry itself.",
           pointers=[("slow", meet), ("fast", meet)],
           state=[("phase", "1 done"), ("moves", str(step))], hold=3.0)

    t.snap(roles({meet: "valid", a: "best"}), line=7, verdict="info",
           note=f"The algebra: the tail is {a} long, and the meeting point sits {b} into "
                f"the cycle, so walking forward from it to the entry takes {c} - {b} = "
                f"{c - b} steps. That is the same as {a}. So one pointer from the head and "
                f"one from the meeting point, both moving one step, arrive together.",
           pointers=[("slow", meet), ("fast", meet)],
           state=[("tail a", str(a)), ("cycle c", str(c)), ("met b", str(b))], hold=3.6)

    slow = 0
    seen = {meet, 0}
    t.snap(roles({0: "focus", meet: "valid"}), line=7,
           note="Phase 2. Send slow back to the head and leave fast where they met. From "
                "here both move one step at a time.",
           pointers=[("slow", 0), ("fast", meet)],
           state=[("phase", "2, find the entry")], hold=2.4)

    fast = meet
    while slow != fast:
        slow = nxt(slow)
        fast = nxt(fast)
        seen.add(slow)
        seen.add(fast)
        if slow == fast:
            break
        t.snap(roles({slow: "focus", fast: "focus"}), line=9,
               note=f"slow is on {vals[slow]}, fast is on {vals[fast]}. Still apart.",
               pointers=[("slow", slow), ("fast", fast)],
               state=[("phase", "2, find the entry")], hold=1.6)

    out = ["dim"] * n
    out[slow] = "best"
    t.snap(out, line=11, verdict="record",
           note=f"They meet again on node {vals[slow]}, and that is where the cycle "
                f"begins. O(n) time, two pointers, no hash set and no extra memory.",
           pointers=[("slow", slow), ("fast", slow)],
           state=[("answer", f"node {vals[slow]}")], hold=3.4)
    return t.trace
