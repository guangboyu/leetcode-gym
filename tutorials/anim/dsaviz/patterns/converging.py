"""Converging two pointers on a histogram: container and trapping water."""
from __future__ import annotations

from ..model import Tracer

LEFT_C = "#4F46E5"
RIGHT_C = "#DB2777"


# --------------------------------------------------------------------------- #
# LC 11 - container with most water
# --------------------------------------------------------------------------- #
LC11_CODE = """
def max_area(height):
    l, r = 0, len(height) - 1
    best = 0
    while l < r:
        area = (r - l) * min(height[l], height[r])
        best = max(best, area)
        if height[l] < height[r]:
            l += 1
        else:
            r -= 1
    return best
"""


def lc11_container(height=(1, 8, 6, 2, 5, 4, 8, 3, 7)):
    h = list(height)
    n = len(h)
    t = Tracer(h, "Container with most water",
               "LeetCode 11  |  converging pointers, the short wall is discarded",
               LC11_CODE, slug="lc0011-container-water",
               legend={"idle": "not reached yet", "window": "still in play",
                       "focus": "the two walls being measured",
                       "invalid": "discarded, cannot beat what we have",
                       "best": "the best container so far",
                       "dim": "discarded earlier", "water": "water this pair holds"})

    plain = [(v, 0) for v in h]

    def region(l, r, label=""):
        return (l, r, min(h[l], h[r]), label)

    def roles(l, r, dead=None, best_pair=None):
        out = []
        for i in range(n):
            if l <= i <= r:
                out.append("window")
            else:
                out.append("dim")
        if best_pair:
            for i in best_pair:
                out[i] = "best"
        else:
            for i in (l, r):
                out[i] = "focus"
        if dead is not None:
            out[dead] = "invalid"
        return out

    l, r = 0, n - 1
    best = 0
    best_pair = None

    t.snap(["idle"] * n, line=2, verdict="info",
           note="Start as wide as possible. Every move after this makes the container "
                "narrower, so a move is only worth it if it can raise the height.",
           bars=plain,
           state=[("best area", "0")], hold=2.2)

    while l < r:
        area = (r - l) * min(h[l], h[r])
        is_best = area > best
        if is_best:
            best = area
            best_pair = (l, r)
        t.snap(roles(l, r, best_pair=(l, r) if is_best else None), line=5,
               verdict="record" if is_best else None,
               note=f"Width {r - l} times the shorter wall {min(h[l], h[r])} = {area}. "
                    + ("New best." if is_best else f"Best stays {best}."),
               pointers=[("l", l), ("r", r)],
               bars=plain, region=region(l, r, f"area {area}"),
               state=[("area", str(area)), ("best area", str(best))],
               hold=1.5 if is_best else 1.1)

        if h[l] < h[r]:
            t.snap(roles(l, r, dead=l), line=7, verdict="drop",
                   note=f"Wall {l} is the shorter one at {h[l]}. Any other partner for it "
                        f"is closer, so narrower, and still capped at {h[l]}. Nothing it "
                        f"can reach beats {area}. Discard it.",
                   pointers=[("l", l), ("r", r)],
                   bars=plain, region=region(l, r),
                   state=[("area", str(area)), ("best area", str(best))], hold=1.9)
            l += 1
        else:
            t.snap(roles(l, r, dead=r), line=9, verdict="drop",
                   note=f"Wall {r} is the shorter one at {h[r]}. Every remaining partner "
                        f"for it is closer and still capped at {h[r]}, so it can never do "
                        f"better than {area}. Discard it.",
                   pointers=[("l", l), ("r", r)],
                   bars=plain, region=region(l, r),
                   state=[("area", str(area)), ("best area", str(best))], hold=1.9)
            r -= 1

    bl, br = best_pair
    out = ["dim"] * n
    out[bl] = out[br] = "best"
    t.snap(out, line=10, verdict="record",
           note=f"Answer: {best}, from walls {bl} and {br}. Each step killed one wall "
                f"forever, so the whole scan is {n} moves instead of {n * (n - 1) // 2} pairs.",
           bars=plain, region=region(bl, br, f"area {best}"),
           state=[("best area", str(best))], hold=2.6)
    return t.trace


# --------------------------------------------------------------------------- #
# LC 42 - trapping rain water
# --------------------------------------------------------------------------- #
LC42_CODE = """
def trap(height):
    l, r = 0, len(height) - 1
    left_max = right_max = 0
    total = 0
    while l < r:
        left_max = max(left_max, height[l])
        right_max = max(right_max, height[r])
        if left_max <= right_max:
            total += left_max - height[l]
            l += 1
        else:
            total += right_max - height[r]
            r -= 1
    return total
"""


def lc42_trapping_water(height=(4, 1, 2, 0, 3, 1, 0, 2, 1, 5)):
    h = list(height)
    n = len(h)
    t = Tracer(h, "Trapping rain water",
               "LeetCode 42  |  converging pointers, the short side is resolved",
               LC42_CODE, slug="lc0042-trapping-water",
               legend={"idle": "not looked at yet", "window": "unresolved, still in play",
                       "focus": "the column being decided now",
                       "valid": "resolved, holds water",
                       "best": "no water here",
                       "dim": "resolved, holds none", "water": "the water"})
    l, r = 0, n - 1
    left_max = right_max = 0
    total = 0
    banked = [0.0] * n
    done = [False] * n

    def roles(cur=None):
        out = []
        for i in range(n):
            if done[i]:
                out.append("valid" if banked[i] > 0 else "dim")
            elif l <= i <= r:
                out.append("window")
            else:
                out.append("idle")
        if cur is not None:
            out[cur] = "focus"
        return out

    def lines():
        return [(left_max, f"left_max {left_max:g}", LEFT_C),
                (right_max, f"right_max {right_max:g}", RIGHT_C)]

    bars = lambda: [(h[i], banked[i]) for i in range(n)]

    t.snap(["idle"] * n, line=2, verdict="info",
           note="Water on a column is min(tallest bar to its left, tallest bar to its "
                "right) minus its own height. The trick is that you can decide a column "
                "without ever knowing the true maximum on the far side.",
           bars=bars(), state=[("total", "0")], hold=2.8)

    while l < r:
        left_max = max(left_max, h[l])
        right_max = max(right_max, h[r])
        t.snap(roles(), line=7,
               note=f"left_max is {left_max:g} over columns 0..{l}. right_max is "
                    f"{right_max:g} over columns {r}..{n - 1}. Everything between "
                    f"{l + 1} and {r - 1} is still unknown.",
               pointers=[("l", l), ("r", r)], bars=bars(), hlines=lines(),
               state=[("left_max", f"{left_max:g}"), ("right_max", f"{right_max:g}"),
                      ("total", f"{total:g}")], hold=1.6)

        if left_max <= right_max:
            got = left_max - h[l]
            t.snap(roles(cur=l), line=8, verdict="valid",
                   note=f"left_max {left_max:g} <= right_max {right_max:g}. The true "
                        f"maximum to the right of column {l} is at least {right_max:g}, "
                        f"so the min is {left_max:g} whatever is hiding in the middle. "
                        f"Column {l} is decided: {left_max:g} - {h[l]:g} = {got:g}.",
                   pointers=[("l", l), ("r", r)], bars=bars(), hlines=lines(),
                   state=[("left_max", f"{left_max:g}"), ("right_max", f"{right_max:g}"),
                          ("total", f"{total:g}")], hold=2.4)
            banked[l] = got
            done[l] = True
            total += got
            l += 1
        else:
            got = right_max - h[r]
            t.snap(roles(cur=r), line=11, verdict="valid",
                   note=f"right_max {right_max:g} < left_max {left_max:g}. Now it is the "
                        f"right side that is the binding constraint, so column {r} is "
                        f"decided: {right_max:g} - {h[r]:g} = {got:g}.",
                   pointers=[("l", l), ("r", r)], bars=bars(), hlines=lines(),
                   state=[("left_max", f"{left_max:g}"), ("right_max", f"{right_max:g}"),
                          ("total", f"{total:g}")], hold=2.4)
            banked[r] = got
            done[r] = True
            total += got
            r -= 1

    done[l] = True
    t.snap(roles(), line=13, verdict="record",
           note=f"Answer: {total:g}. One pass, O(1) memory, and the unvisited middle was "
                f"never needed because the min always resolved to the side we knew.",
           bars=bars(), state=[("total", f"{total:g}")], hold=2.8)
    return t.trace


# --------------------------------------------------------------------------- #
# LC 42 - the two-pass version, which is where the two-pointer one comes from
# --------------------------------------------------------------------------- #
LC42_TWOPASS_CODE = """
def trap(height):
    n = len(height)
    left_max, right_max = [0] * n, [0] * n

    left_max[0] = height[0]
    for i in range(1, n):
        left_max[i] = max(left_max[i - 1], height[i])

    right_max[n - 1] = height[n - 1]
    for i in range(n - 2, -1, -1):
        right_max[i] = max(right_max[i + 1], height[i])

    total = 0
    for i in range(n):
        lo = min(left_max[i], right_max[i])
        total += lo - height[i]
    return total
"""


def lc42_two_pass(height=(4, 1, 2, 0, 3, 1, 0, 2, 1, 5)):
    from ..model import Aux
    h = list(height)
    n = len(h)
    t = Tracer(h, "Trapping rain water, one column at a time",
               "LeetCode 42  |  prefix and suffix maxima, two passes",
               LC42_TWOPASS_CODE, slug="lc0042-trapping-two-pass",
               legend={"idle": "not computed yet", "window": "computed",
                       "focus": "the column being handled now",
                       "valid": "its water is banked",
                       "dim": "holds no water", "water": "water on this column"})

    lm = [None] * n
    rm = [None] * n
    banked = [0.0] * n
    done = [False] * n
    total = 0

    def aux_rows():
        return [
            Aux(title="left_max  (tallest bar at or left of this column)", kind="aligned",
                cells=["" if v is None else f"{v:g}" for v in lm],
                roles=["window" if v is not None else "idle" for v in lm]),
            Aux(title="right_max  (tallest bar at or right of this column)", kind="aligned",
                cells=["" if v is None else f"{v:g}" for v in rm],
                roles=["window" if v is not None else "idle" for v in rm]),
        ]

    bars = lambda: [(h[i], banked[i]) for i in range(n)]

    t.snap(["idle"] * n, line=1, verdict="info",
           note="Forget the bowls. Ask one column at a time: how deep is the water "
                "standing on top of THIS bar? Sum those and you are done.",
           bars=bars(), aux=aux_rows(), hold=3.0)

    i = 0
    roles = ["idle"] * n
    roles[0] = "focus"
    lm[0] = h[0]
    t.snap(roles, line=5,
           note=f"Pass 1, left to right. Nothing is left of column 0, so left_max[0] is "
                f"its own height, {h[0]:g}.",
           bars=bars(), aux=aux_rows(), hold=1.6)

    for i in range(1, n):
        lm[i] = max(lm[i - 1], h[i])
        roles = ["window" if k < i else "idle" for k in range(n)]
        roles[i] = "focus"
        t.snap(roles, line=7,
               note=f"left_max[{i}] = max(left_max[{i - 1}] = {lm[i - 1]:g}, "
                    f"height[{i}] = {h[i]:g}) = {lm[i]:g}. It can only stay the same or "
                    f"go up, never down.",
               bars=bars(), aux=aux_rows(), hold=0.75)

    rm[n - 1] = h[n - 1]
    roles = ["window"] * n
    roles[n - 1] = "focus"
    t.snap(roles, line=9,
           note=f"Pass 2, right to left. Same idea from the other end: right_max[{n - 1}] "
                f"= {h[n - 1]:g}.",
           bars=bars(), aux=aux_rows(), hold=1.8)

    for i in range(n - 2, -1, -1):
        rm[i] = max(rm[i + 1], h[i])
        roles = ["window"] * n
        roles[i] = "focus"
        t.snap(roles, line=11,
               note=f"right_max[{i}] = max({rm[i + 1]:g}, {h[i]:g}) = {rm[i]:g}. "
                    f"Non-decreasing again, just walking the other way.",
               bars=bars(), aux=aux_rows(), hold=0.75)

    for i in range(n):
        got = min(lm[i], rm[i]) - h[i]
        banked[i] = got
        done[i] = True
        total += got
        roles = []
        for k in range(n):
            if done[k]:
                roles.append("valid" if banked[k] > 0 else "dim")
            else:
                roles.append("window")
        roles[i] = "focus"
        short = "left" if lm[i] <= rm[i] else "right"
        t.snap(roles, line=15,
               note=f"Column {i}: min({lm[i]:g}, {rm[i]:g}) - {h[i]:g} = {got:g}. "
                    f"The {short} side is the shorter one, so it is the side that decides "
                    f"how deep the water can get here.",
               bars=bars(), aux=aux_rows(),
               hlines=[(lm[i], f"left_max {lm[i]:g}", LEFT_C),
                       (rm[i], f"right_max {rm[i]:g}", RIGHT_C)],
               state=[("total", f"{total:g}")], hold=1.15)

    roles = ["valid" if banked[k] > 0 else "dim" for k in range(n)]
    t.snap(roles, line=17, verdict="record",
           note=f"Answer: {total:g}. Two passes, O(n) time, O(n) space. Every column was "
                f"decided on its own, and the two arrays only ever grow, which is exactly "
                f"what the two-pointer version exploits to drop the arrays.",
           bars=bars(), aux=aux_rows(), state=[("total", f"{total:g}")], hold=3.2)
    return t.trace
