"""Colors, fonts and sizing for the light theme."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from functools import lru_cache

from PIL import ImageFont

FONT_DIR = os.path.join(os.path.dirname(__file__), "fonts")

SANS = os.path.join(FONT_DIR, "Inter-Regular.ttf")
SANS_MED = os.path.join(FONT_DIR, "Inter-SemiBold.ttf")
SANS_BOLD = os.path.join(FONT_DIR, "Inter-Bold.ttf")
MONO = os.path.join(FONT_DIR, "JetBrainsMono-Regular.ttf")
MONO_BOLD = os.path.join(FONT_DIR, "JetBrainsMono-Bold.ttf")


@lru_cache(maxsize=256)
def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


@dataclass(frozen=True)
class Role:
    fill: str
    border: str
    text: str


# Cell roles.
#
# The palette is built on one opposition: BLUE means this passed / is valid /
# is kept, RED means this failed / is discarded. Red-vs-blue survives the common
# forms of colour blindness, which red-vs-green does not.
#
# Everything else is deliberately outside that axis so it cannot be mistaken for
# a verdict: SLATE is "in scope, no judgement yet", AMBER is "look here right
# now", PURPLE is "this is the answer".
ROLES = {
    # not yet touched
    "idle":    Role("#FFFFFF", "#D3D9E0", "#1F2328"),
    # scanned and left behind
    "dim":     Role("#F4F5F7", "#E1E5EA", "#9AA1AB"),
    # inside the current window / still in the live search space
    "window":  Role("#E6EBF4", "#7C90AE", "#263449"),
    # the element being looked at right now
    "focus":   Role("#FEF1CD", "#C98A04", "#6B4A02"),
    # passes the constraint
    "valid":   Role("#DBEAFE", "#2563EB", "#14356E"),
    # breaks the constraint, or is being thrown away
    "invalid": Role("#FDE3E2", "#E5484D", "#8B1D1F"),
    # part of the best answer found so far
    "best":    Role("#F1E6FE", "#9333EA", "#4B1580"),
    # a quantity the algorithm is accumulating, drawn above the bars.
    # Off the verdict axis: it is a thing in the problem, not a judgement.
    "water":   Role("#CDEFF6", "#0E9AA7", "#08606B"),
}

# Fallback wording for the key row. Each animation can override any of these
# with its own vocabulary (a "window" is a "search space" in binary search).
DEFAULT_LEGEND = {
    "idle": "not visited yet",
    "window": "in scope",
    "focus": "looking at this now",
    "valid": "passes the rule",
    "invalid": "fails the rule",
    "best": "best answer so far",
    "dim": "done with",
    "water": "water held",
}
LEGEND_ORDER = ["idle", "window", "focus", "valid", "invalid", "best", "water", "dim"]

# Pointers are pills with words in them, kept off the verdict axis so a blue
# pill is never read as "valid".
POINTER_COLORS = {
    "l": "#4F46E5", "left": "#4F46E5", "lo": "#4F46E5", "i": "#4F46E5",
    "r": "#DB2777", "right": "#DB2777", "hi": "#DB2777", "j": "#DB2777",
    "mid": "#0D9488", "m": "#0D9488", "w": "#0D9488",
    "k": "#B45309", "top": "#B45309",
    "low": "#4F46E5", "write": "#4F46E5", "slow": "#4F46E5",
    "high": "#DB2777", "read": "#DB2777", "fast": "#DB2777",
}
POINTER_FALLBACK = "#475569"

VERDICTS = {
    None:      ("#F7F8FA", "#E1E5EA", "#4B5563", ""),
    "info":    ("#F4F6FA", "#CBD5E1", "#475569", "i"),
    "valid":   ("#EFF5FF", "#BBD5FB", "#1D4ED8", "OK"),
    "invalid": ("#FDF0EF", "#F6C9C7", "#B91C1C", "X"),
    "drop":    ("#FDF3F2", "#F3D3D1", "#C2410C", "-"),
    "record":  ("#F6EEFE", "#DFC6FA", "#7E22CE", "*"),
    "count":   ("#F6EEFE", "#DFC6FA", "#7E22CE", "+"),
}

# Page
BG = "#FFFFFF"
PANEL = "#F8F9FB"
INK = "#171A1F"
MUTED = "#6B7280"
FAINT = "#9AA1AB"
RULE = "#E4E8ED"

# Code syntax colors (One Light flavoured)
SYN = {
    "kw": "#A626A4",
    "str": "#3D8F3D",
    "num": "#9A6100",
    "com": "#A0A6AF",
    "fn": "#3B6FD4",
    "op": "#4B5563",
    "txt": "#2B2F36",
}
CODE_BG = "#FAFBFC"
CODE_HL = "#EAF1FE"
CODE_HL_BAR = "#3B82F6"
CODE_GUTTER = "#B4BAC3"


@dataclass
class Layout:
    """All numbers in design pixels; the renderer draws at `scale` and downsamples."""
    width: int = 1000
    pad: int = 26
    code_w: int = 356
    scale: int = 3          # supersampling factor while drawing
    export: int = 2         # output pixels per design pixel (2 = HiDPI sharp)

    title_h: int = 30
    rule_gap: int = 14
    cell_h: int = 58
    cell_max_w: int = 62
    cell_gap: int = 6
    bracket_h: int = 26
    index_h: int = 18
    pointer_h: int = 44
    aux_h: int = 70
    chip_h: int = 30
    note_h: int = 58
    legend_h: int = 24
    bar_h: int = 168
    line_h: int = 21

    @property
    def left_x(self) -> int:
        return self.pad

    @property
    def left_w(self) -> int:
        return self.width - self.pad * 2 - self.code_w - 24

    @property
    def code_x(self) -> int:
        return self.width - self.pad - self.code_w
