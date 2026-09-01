"""Low-level drawing helpers. Everything is drawn at `scale` and downsampled."""
from __future__ import annotations

import re

from PIL import ImageDraw

from . import theme


def hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def mix(a: str, b: str, t: float) -> str:
    """Blend hex colour a toward b by t (0..1)."""
    ra, ga, ba = hex_to_rgb(a)
    rb, gb, bb = hex_to_rgb(b)
    f = lambda x, y: int(round(x + (y - x) * t))
    return "#%02X%02X%02X" % (f(ra, rb), f(ga, gb), f(ba, bb))


class Pen:
    """ImageDraw wrapper that multiplies every coordinate by a scale factor."""

    def __init__(self, draw: ImageDraw.ImageDraw, scale: int):
        self.d = draw
        self.s = scale

    def rrect(self, box, radius=8, fill=None, outline=None, width=1):
        s = self.s
        x0, y0, x1, y1 = [v * s for v in box]
        self.d.rounded_rectangle([x0, y0, x1, y1], radius=radius * s, fill=fill,
                                 outline=outline, width=max(1, int(width * s)))

    def rect(self, box, fill=None, outline=None, width=1):
        s = self.s
        x0, y0, x1, y1 = [v * s for v in box]
        self.d.rectangle([x0, y0, x1, y1], fill=fill, outline=outline,
                         width=max(1, int(width * s)))

    def line(self, pts, fill, width=1):
        s = self.s
        self.d.line([(x * s, y * s) for x, y in pts], fill=fill,
                    width=max(1, int(width * s)))

    def poly(self, pts, fill):
        s = self.s
        self.d.polygon([(x * s, y * s) for x, y in pts], fill=fill)

    def text(self, xy, txt, font_path, size, fill, anchor="la"):
        s = self.s
        f = theme.font(font_path, int(round(size * s)))
        self.d.text((xy[0] * s, xy[1] * s), txt, font=f, fill=fill, anchor=anchor)

    def text_w(self, txt, font_path, size) -> float:
        f = theme.font(font_path, int(round(size * self.s)))
        return f.getlength(txt) / self.s


# --- python syntax highlighting -------------------------------------------------

KEYWORDS = {
    "def", "return", "for", "while", "if", "elif", "else", "in", "not", "and",
    "or", "None", "True", "False", "break", "continue", "pass", "import",
    "from", "as", "with", "class", "lambda", "is", "yield", "global",
}
BUILTINS = {
    "len", "max", "min", "range", "set", "dict", "list", "sum", "abs", "sorted",
    "enumerate", "deque", "Counter", "float", "int", "str", "append", "pop",
    "popleft", "add", "remove", "get", "items", "keys", "values",
}

TOKEN_RE = re.compile(
    r"(?P<com>#.*$)"
    r"|(?P<str>\"[^\"]*\"|'[^']*')"
    r"|(?P<num>\b\d+(?:\.\d+)?\b)"
    r"|(?P<word>[A-Za-z_][A-Za-z_0-9]*)"
    r"|(?P<op>[^A-Za-z_0-9\s]+)"
    r"|(?P<ws>\s+)"
)


def tokenize(line: str):
    """Yield (text, colour) pairs for one line of Python."""
    out = []
    for m in TOKEN_RE.finditer(line):
        kind = m.lastgroup
        txt = m.group()
        if kind == "com":
            out.append((txt, theme.SYN["com"]))
        elif kind == "str":
            out.append((txt, theme.SYN["str"]))
        elif kind == "num":
            out.append((txt, theme.SYN["num"]))
        elif kind == "word":
            if txt in KEYWORDS:
                out.append((txt, theme.SYN["kw"]))
            elif txt in BUILTINS:
                out.append((txt, theme.SYN["fn"]))
            else:
                out.append((txt, theme.SYN["txt"]))
        elif kind == "op":
            out.append((txt, theme.SYN["op"]))
        else:
            out.append((txt, theme.SYN["txt"]))
    return out


def wrap(pen: Pen, txt: str, font_path: str, size: float, max_w: float, max_lines=2):
    words = txt.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if pen.text_w(trial, font_path, size) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
            if len(lines) == max_lines:
                break
    if cur and len(lines) < max_lines:
        lines.append(cur)
    if len(lines) == max_lines and len(" ".join(lines)) < len(txt):
        while lines and pen.text_w(lines[-1] + " ...", font_path, size) > max_w:
            lines[-1] = lines[-1].rsplit(" ", 1)[0]
        lines[-1] = lines[-1] + " ..."
    return lines
