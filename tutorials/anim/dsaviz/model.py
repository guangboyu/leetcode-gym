"""Frame model and the tracer that algorithms write into.

An algorithm is written once, normally, with `t.snap(...)` calls sprinkled in.
Each snap records one teaching step. The renderer never knows what algorithm
it is drawing.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable, Sequence


@dataclass
class Aux:
    """A secondary row under the array: a deque, a stack, a hash map."""
    title: str
    kind: str = "cells"                     # "cells" | "chips"
    cells: list[str] = field(default_factory=list)
    roles: list[str] = field(default_factory=list)
    subs: list[str] = field(default_factory=list)   # small caption under each cell
    chips: list[tuple[str, str]] = field(default_factory=list)


@dataclass
class Frame:
    cells: list[str]
    roles: list[str]
    pointers: list[tuple[str, int]] = field(default_factory=list)
    bracket: tuple[int, int, str] | None = None     # (lo, hi, label)
    bracket_role: str = "window"
    line: int | None = None                          # 1-based code line
    note: str = ""
    verdict: str | None = None
    state: list[tuple[str, str]] = field(default_factory=list)
    auxes: list[Aux] = field(default_factory=list)
    bars: list[tuple[float, float]] | None = None   # (height, water) per index
    hlines: list[tuple[float, str, str]] = field(default_factory=list)  # (value, label, colour)
    region: tuple[int, int, float, str] | None = None  # (lo, hi, height, label)
    hold: float = 1.0                                # duration multiplier


@dataclass
class Trace:
    title: str
    subtitle: str = ""
    code: list[str] = field(default_factory=list)
    frames: list[Frame] = field(default_factory=list)
    slug: str = "trace"
    legend: dict[str, str] = field(default_factory=dict)
    graph: tuple[int, int] | None = None   # (node count, tail length) for a rho-shaped list


class Tracer:
    """Records frames while an instrumented algorithm runs."""

    def __init__(self, cells: Sequence[Any], title: str, subtitle: str = "",
                 code: str = "", slug: str = "trace",
                 legend: dict[str, str] | None = None,
                 graph: tuple[int, int] | None = None):
        self.cells = [str(c) for c in cells]
        self.trace = Trace(
            title=title,
            subtitle=subtitle,
            code=[ln for ln in code.strip("\n").split("\n")] if code else [],
            slug=slug,
            legend=dict(legend or {}),
            graph=graph,
        )

    def snap(self, roles: Iterable[str] | dict[int, str] | None = None, *,
             line: int | None = None, note: str = "", verdict: str | None = None,
             pointers: Iterable[tuple[str, int]] = (), bracket=None,
             bracket_role: str = "window", state: Iterable[tuple[str, Any]] = (),
             aux=None, bars=None, hlines=(), region=None, cells=None,
             hold: float = 1.0, base: str = "idle") -> None:
        shown = [str(c) for c in cells] if cells is not None else list(self.cells)
        n = len(shown)
        if roles is None:
            resolved = [base] * n
        elif isinstance(roles, dict):
            resolved = [roles.get(i, base) for i in range(n)]
        else:
            resolved = list(roles)
            if len(resolved) != n:
                raise ValueError(f"roles has {len(resolved)} entries, need {n}")
        self.trace.frames.append(Frame(
            cells=shown,
            roles=resolved,
            pointers=[(str(k), int(v)) for k, v in pointers],
            bracket=bracket,
            bracket_role=bracket_role,
            line=line,
            note=note,
            verdict=verdict,
            state=[(str(k), str(v)) for k, v in state],
            auxes=[] if aux is None else ([aux] if isinstance(aux, Aux) else list(aux)),
            bars=[(float(h), float(w)) for h, w in bars] if bars else None,
            hlines=[(float(v), str(lb), str(c)) for v, lb, c in hlines],
            region=region,
            hold=hold,
        ))

    @property
    def frames(self) -> list[Frame]:
        return self.trace.frames


def window_roles(n: int, lo: int, hi: int, *, inside: str = "window",
                 before: str = "dim", after: str = "idle",
                 focus: int | None = None, focus_role: str = "focus",
                 best: tuple[int, int] | None = None,
                 best_role: str = "best") -> list[str]:
    """Standard colouring for a [lo, hi] window over n cells."""
    roles = []
    for i in range(n):
        if lo <= i <= hi:
            roles.append(inside)
        elif i < lo:
            roles.append(before)
        else:
            roles.append(after)
    if best and not (lo <= best[0] and best[1] <= hi):
        for i in range(best[0], best[1] + 1):
            if not (lo <= i <= hi):
                roles[i] = best_role
    if focus is not None and 0 <= focus < n:
        roles[focus] = focus_role
    return roles
