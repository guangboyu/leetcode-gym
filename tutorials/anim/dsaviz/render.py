"""Turns a Trace into PNG frames and an animated GIF."""
from __future__ import annotations

import os

import math

from PIL import Image, ImageDraw

from . import theme
from .draw import Pen, mix, tokenize, wrap
from .model import Frame, Trace
from .theme import Layout


class Renderer:
    def __init__(self, trace: Trace, layout: Layout | None = None):
        self.t = trace
        self.L = layout or Layout()
        self._measure()

    # -- geometry -------------------------------------------------------------
    def _measure(self):
        L, t = self.L, self.t
        s = L.scale
        img = Image.new("RGB", (10, 10))
        pen = Pen(ImageDraw.Draw(img), s)
        self.pen_probe = pen

        n = len(t.frames[0].cells)
        self.n = n
        longest = max((len(c) for f in t.frames for c in f.cells), default=1)

        gap = L.cell_gap
        cw = min(L.cell_max_w, (L.left_w - gap * (n - 1)) / n)
        needed = longest * 11 + 14
        cw = max(min(cw, L.cell_max_w), min(needed, (L.left_w - gap * (n - 1)) / n))
        self.cw = cw
        self.cell_fs = max(11, min(20, cw * 0.42))
        row_w = cw * n + gap * (n - 1)
        self.x0 = L.left_x + (L.left_w - row_w) / 2

        self.graph_mode = t.graph is not None
        if self.graph_mode:
            self._graph_geometry()
        self.bar_mode = any(f.bars for f in t.frames)
        if self.bar_mode:
            self.bar_scale_max = max(
                (h + w for f in t.frames if f.bars for h, w in f.bars), default=1.0) or 1.0
        self.has_bracket = any(f.bracket for f in t.frames)
        self.n_aux = max((len(f.auxes) for f in t.frames), default=0)
        self.has_state = any(f.state for f in t.frames)
        self.max_ptr_rows = max((self._ptr_rows(f) for f in t.frames), default=0)

        self.legend_items = self._legend_items()

        y = L.pad
        self.y_title = y
        y += L.title_h + 6
        self.y_rule = y
        y += 12
        self.legend_rows = []
        if self.legend_items:
            self.y_legend = y
            self.legend_rows = self._legend_rows(pen)
            y += L.legend_h * len(self.legend_rows) + 6
        self.content_top = y

        if self.has_bracket:
            self.y_bracket = y
            y += L.bracket_h
        self.y_cells = y
        if self.graph_mode:
            y += self.graph_h
            self.y_index = self.y_ptr = y
        else:
            y += (L.bar_h if self.bar_mode else L.cell_h) + 4
            self.y_index = y
            y += L.index_h + 4
            self.y_ptr = y
            y += 14 + 24 * max(1, self.max_ptr_rows) if self.max_ptr_rows else 0
        if self.n_aux:
            y += 10
            self.y_aux = y
            y += L.aux_h * self.n_aux
        if self.has_state:
            y += 16
            self.y_state = y
            y += L.chip_h
        left_bottom = y

        # code panel
        self.code_fs = 13
        inner_w = L.code_w - 30 - 28
        maxlen = max((len(l) for l in t.code), default=1)
        while self.code_fs > 9.5 and maxlen * self.code_fs * 0.6 > inner_w:
            self.code_fs -= 0.5
        self.code_lh = self.code_fs + 8.5
        self.y_code = self.content_top
        code_bottom = self.y_code + 30 + len(t.code) * self.code_lh + 12
        self.code_h = code_bottom - self.y_code

        body_bottom = max(left_bottom, code_bottom)
        self.y_note = body_bottom + 18
        self.H = int(round(self.y_note + L.note_h + L.pad))
        self.W = L.width

    def _legend_items(self) -> list[tuple[str, str]]:
        """Only the roles this animation actually uses, in a fixed reading order."""
        used = set()
        for f in self.t.frames:
            used.update(f.roles)
            for a in f.auxes:
                used.update(a.roles)
        if any((f.bars and any(w > 0 for _, w in f.bars)) or f.region
               for f in self.t.frames):
            used.add("water")
        items = []
        for role in theme.LEGEND_ORDER:
            if role not in used:
                continue
            label = self.t.legend.get(role, theme.DEFAULT_LEGEND.get(role, ""))
            if label:
                items.append((role, label))
        return items

    def _legend_rows(self, pen: Pen) -> list[list[tuple[str, str, float]]]:
        avail = self.L.width - self.L.pad * 2
        rows, cur, cur_w = [], [], 0.0
        for role, label in self.legend_items:
            w = 14 + 6 + pen.text_w(label, theme.SANS, 11) + 20
            if cur and cur_w + w > avail:
                rows.append(cur)
                cur, cur_w = [], 0.0
            cur.append((role, label, w))
            cur_w += w
        if cur:
            rows.append(cur)
        return rows

    def _draw_legend(self, pen: Pen):
        y = self.y_legend
        for row in self.legend_rows:
            x = self.L.pad
            for role, label, w in row:
                r = theme.ROLES.get(role, theme.ROLES["idle"])
                pen.rrect((x, y + 4, x + 14, y + 18), radius=4, fill=r.fill,
                          outline=r.border, width=1.2)
                pen.text((x + 20, y + 11), label, theme.SANS, 11, theme.MUTED,
                         anchor="lm")
                x += w
            y += self.L.legend_h

    def _ptr_rows(self, f: Frame) -> int:
        if not f.pointers:
            return 0
        by_idx = {}
        for lbl, i in f.pointers:
            by_idx.setdefault(i, []).append(lbl)
        return 1

    # -- drawing --------------------------------------------------------------
    def _cell_x(self, i: int) -> float:
        return self.x0 + i * (self.cw + self.L.cell_gap)

    def render(self, f: Frame) -> Image.Image:
        L = self.L
        s = L.scale
        img = Image.new("RGB", (self.W * s, self.H * s), theme.BG)
        pen = Pen(ImageDraw.Draw(img), s)

        # header
        pen.text((L.pad, self.y_title + 2), self.t.title, theme.SANS_BOLD, 19, theme.INK)
        if self.t.subtitle:
            pen.text((self.W - L.pad, self.y_title + 8), self.t.subtitle,
                     theme.SANS, 12.5, theme.FAINT, anchor="ra")
        pen.line([(L.pad, self.y_rule), (self.W - L.pad, self.y_rule)], theme.RULE, 1)
        if self.legend_rows:
            self._draw_legend(pen)

        if self.graph_mode:
            self._draw_graph(pen, f)
        elif self.bar_mode:
            self._draw_bars(pen, f)
        else:
            self._draw_array(pen, f)
        if f.bracket:
            self._draw_bracket(pen, f)
        if f.pointers and not self.graph_mode:
            self._draw_pointers(pen, f)
        for k, a in enumerate(f.auxes):
            self._draw_aux(pen, a, self.y_aux + k * self.L.aux_h)
        if f.state:
            self._draw_state(pen, f)
        self._draw_code(pen, f)
        self._draw_note(pen, f)

        e = self.L.export
        return img.resize((self.W * e, self.H * e), Image.LANCZOS)

    def _draw_array(self, pen: Pen, f: Frame):
        cw, ch = self.cw, self.L.cell_h
        for i, (val, role) in enumerate(zip(f.cells, f.roles)):
            r = theme.ROLES.get(role, theme.ROLES["idle"])
            x = self._cell_x(i)
            y = self.y_cells
            pen.rrect((x, y, x + cw, y + ch), radius=7, fill=r.fill,
                      outline=r.border, width=1.5 if role != "idle" else 1)
            pen.text((x + cw / 2, y + ch / 2), val, theme.MONO_BOLD,
                     self.cell_fs, r.text, anchor="mm")
            idx_col = theme.FAINT if role in ("idle", "dim") else theme.MUTED
            pen.text((x + cw / 2, self.y_index + 8), str(i), theme.MONO,
                     10.5, idx_col, anchor="mm")

    def _graph_geometry(self):
        """Lay a rho-shaped linked list out: a straight tail into a polygon cycle."""
        L = self.L
        n, a = self.t.graph
        c = n - a
        r = 26.0
        dx = 2 * r + 36
        R = max(72.0, c * (2 * r + 26) / (2 * math.pi))
        self.node_r = r
        span = (a - 1) * dx + dx + 2 * R
        x0 = L.left_x + (L.left_w - (span + 2 * r)) / 2 + r
        self.graph_h = 2 * (R + r) + 10
        cy_rel = self.graph_h / 2
        xc = x0 + (a - 1) * dx + dx + R

        self._node_rel = []
        for i in range(a):
            self._node_rel.append((x0 + i * dx, cy_rel))
        for k in range(c):
            th = math.pi - k * (2 * math.pi / c)
            self._node_rel.append((xc + R * math.cos(th), cy_rel - R * math.sin(th)))
        self._graph_centre = (xc, cy_rel)
        self._tail_len = a

    def _node_xy(self, i):
        x, yr = self._node_rel[i]
        return x, self.y_cells + yr

    def _arrow(self, pen: Pen, i: int, j: int, colour: str):
        (x1, y1), (x2, y2) = self._node_xy(i), self._node_xy(j)
        dx, dy = x2 - x1, y2 - y1
        d = math.hypot(dx, dy) or 1
        ux, uy = dx / d, dy / d
        r = self.node_r
        sx, sy = x1 + ux * (r + 2), y1 + uy * (r + 2)
        ex, ey = x2 - ux * (r + 9), y2 - uy * (r + 9)
        pen.line([(sx, sy), (ex, ey)], colour, 1.6)
        px, py = -uy, ux
        pen.poly([(ex + ux * 8, ey + uy * 8), (ex + px * 4.5, ey + py * 4.5),
                  (ex - px * 4.5, ey - py * 4.5)], colour)

    def _draw_graph(self, pen: Pen, f: Frame):
        n, a = self.t.graph
        r = self.node_r
        edge = "#B9C0CA"
        for i in range(n - 1):
            self._arrow(pen, i, i + 1, edge)
        self._arrow(pen, n - 1, a, "#8DA0BC")

        for i in range(n):
            role = f.roles[i] if i < len(f.roles) else "idle"
            ro = theme.ROLES.get(role, theme.ROLES["idle"])
            x, y = self._node_xy(i)
            pen.d.ellipse([(x - r) * pen.s, (y - r) * pen.s,
                           (x + r) * pen.s, (y + r) * pen.s],
                          fill=ro.fill, outline=ro.border,
                          width=max(1, int(1.6 * pen.s)))
            pen.text((x, y), f.cells[i], theme.MONO_BOLD, 15, ro.text, anchor="mm")

        by_node: dict[int, list[str]] = {}
        for lbl, i in f.pointers:
            by_node.setdefault(i, []).append(lbl)
        cx, cyr = self._graph_centre
        cy = self.y_cells + cyr
        for i, labels in by_node.items():
            if not (0 <= i < n):
                continue
            x, y = self._node_xy(i)
            if i < self._tail_len or i == self._tail_len:
                # tail nodes, and the cycle entry, would collide with the tail
                # if their labels were pushed outward, so drop them straight down
                ux, uy = 0.0, 1.0
            else:
                dxx, dyy = x - cx, y - cy
                d = math.hypot(dxx, dyy) or 1
                ux, uy = dxx / d, dyy / d
            off = r + 16
            for lbl in labels:
                col = theme.POINTER_COLORS.get(lbl.lower(), theme.POINTER_FALLBACK)
                w = max(46, pen.text_w(lbl, theme.MONO_BOLD, 11.5) + 20)
                px, py = x + ux * off, y + uy * off
                pen.rrect((px - w / 2, py - 10, px + w / 2, py + 10), radius=10,
                          fill=mix(col, "#FFFFFF", 0.88),
                          outline=mix(col, "#FFFFFF", 0.4), width=1.2)
                pen.text((px, py), lbl, theme.MONO_BOLD, 11.5, col, anchor="mm")
                off += 24 if abs(uy) >= abs(ux) else w + 8

    def _draw_bars(self, pen: Pen, f: Frame):
        """Histogram mode: value as bar height, plus an accumulated quantity on top."""
        L = self.L
        cw = self.cw
        base_y = self.y_cells + L.bar_h
        scale = (L.bar_h - 22) / self.bar_scale_max
        x_end = self._cell_x(self.n - 1) + cw
        pen.line([(self.x0 - 6, base_y), (x_end + 6, base_y)], "#C7CDD6", 1.2)

        wr = theme.ROLES["water"]
        if f.region:
            rl, rr, rh, _ = f.region
            pen.rect((self._cell_x(rl), base_y - rh * scale,
                      self._cell_x(rr) + cw, base_y), fill=wr.fill)

        bars = f.bars or [(0.0, 0.0)] * self.n
        for i, (h, w) in enumerate(bars):
            role = f.roles[i] if i < len(f.roles) else "idle"
            r = theme.ROLES.get(role, theme.ROLES["idle"])
            x = self._cell_x(i)
            top = base_y - h * scale
            if w > 0:
                wtop = top - w * scale
                pen.rrect((x, wtop, x + cw, top), radius=3, fill=wr.fill,
                          outline=wr.border, width=1)
                pen.text((x + cw / 2, wtop - 9), f"{w:g}", theme.MONO_BOLD, 10.5,
                         wr.text, anchor="mm")
            if h > 0:
                pen.rrect((x, top, x + cw, base_y), radius=3, fill=r.fill,
                          outline=r.border, width=1.4)
                pen.text((x + cw / 2, min(base_y - 11, top + 11)), f"{h:g}",
                         theme.MONO_BOLD, min(12.5, self.cell_fs - 2), r.text, anchor="mm")
            else:
                pen.line([(x, base_y), (x + cw, base_y)], r.border, 2)
            idx_col = theme.FAINT if role in ("idle", "dim") else theme.MUTED
            pen.text((x + cw / 2, self.y_index + 8), str(i), theme.MONO, 10.5,
                     idx_col, anchor="mm")

        if f.region:
            rl, rr, rh, rlabel = f.region
            rx0, rx1 = self._cell_x(rl), self._cell_x(rr) + cw
            ry = base_y - rh * scale
            pen.rect((rx0, ry, rx1, base_y), outline=wr.border, width=1.8)
            if rlabel:
                tw = pen.text_w(rlabel, theme.MONO_BOLD, 11)
                pen.rrect(((rx0 + rx1 - tw - 14) / 2, ry - 10, (rx0 + rx1 + tw + 14) / 2,
                           ry + 10), radius=10, fill=mix(wr.border, "#FFFFFF", 0.9),
                          outline=wr.border, width=1)
                pen.text(((rx0 + rx1) / 2, ry), rlabel, theme.MONO_BOLD, 11,
                         wr.text, anchor="mm")

        for val, label, col in f.hlines:
            y = base_y - val * scale
            x = self.x0 - 6
            while x < x_end + 6:
                pen.line([(x, y), (min(x + 6, x_end + 6), y)], col, 1.2)
                x += 10
            if label:
                tw = pen.text_w(label, theme.MONO_BOLD, 10)
                x1 = x_end - cw - 8
                x0 = x1 - tw - 12
                py = y - 9 if y - 18 >= self.y_cells else y + 11
                pen.rrect((x0, py - 8, x1, py + 8), radius=8,
                          fill=mix(col, '#FFFFFF', 0.9),
                          outline=mix(col, '#FFFFFF', 0.5), width=1)
                pen.text(((x0 + x1) / 2, py), label, theme.MONO_BOLD, 10,
                         col, anchor='mm')

    def _draw_bracket(self, pen: Pen, f: Frame):
        lo, hi, label = f.bracket
        if lo > hi or lo < 0:
            return
        r = theme.ROLES.get(f.bracket_role, theme.ROLES["window"])
        x_l = self._cell_x(lo) - 3
        x_r = self._cell_x(hi) + self.cw + 3
        y_b = self.y_bracket + self.L.bracket_h - 5
        y_t = self.y_bracket + 6
        col = r.border
        pen.line([(x_l, y_b), (x_l, y_t), (x_r, y_t), (x_r, y_b)], col, 1.5)
        if label:
            tw = pen.text_w(label, theme.SANS_MED, 11.5)
            cx = (x_l + x_r) / 2
            pen.rrect((cx - tw / 2 - 7, y_t - 8, cx + tw / 2 + 7, y_t + 8),
                      radius=8, fill=mix(col, "#FFFFFF", 0.88), outline=col, width=1)
            pen.text((cx, y_t + 1), label, theme.SANS_MED, 11.5, r.text, anchor="mm")

    def _draw_pointers(self, pen: Pen, f: Frame):
        by_idx: dict[int, list[str]] = {}
        for lbl, i in f.pointers:
            by_idx.setdefault(i, []).append(lbl)
        y_arrow = self.y_ptr + 2
        for i, labels in by_idx.items():
            if not (0 <= i < self.n):
                continue
            cx = self._cell_x(i) + self.cw / 2
            main = theme.POINTER_COLORS.get(labels[0].lower(), theme.POINTER_FALLBACK)
            pen.poly([(cx - 7, y_arrow + 10), (cx + 7, y_arrow + 10), (cx, y_arrow)], main)
            widths = [max(42, pen.text_w(l, theme.MONO_BOLD, 11.5) + 20) for l in labels]
            total = sum(widths) + 4 * (len(labels) - 1)
            x = cx - total / 2
            for lbl, w in zip(labels, widths):
                col = theme.POINTER_COLORS.get(lbl.lower(), theme.POINTER_FALLBACK)
                pen.rrect((x, y_arrow + 13, x + w, y_arrow + 33), radius=10,
                          fill=mix(col, "#FFFFFF", 0.88), outline=mix(col, "#FFFFFF", 0.45),
                          width=1)
                pen.text((x + w / 2, y_arrow + 23.5), lbl, theme.MONO_BOLD, 11.5,
                         col, anchor="mm")
                x += w + 4

    def _draw_aux(self, pen: Pen, a, y0: float):
        L = self.L
        y = y0
        pen.text((L.left_x, y), a.title.upper(), theme.SANS_MED, 10, theme.FAINT)
        y += 16
        if a.kind == "aligned":
            for i, val in enumerate(a.cells):
                role = a.roles[i] if i < len(a.roles) else "idle"
                r = theme.ROLES.get(role, theme.ROLES["idle"])
                x = self._cell_x(i)
                pen.rrect((x, y, x + self.cw, y + 28), radius=6, fill=r.fill,
                          outline=r.border, width=1.2)
                pen.text((x + self.cw / 2, y + 14), val, theme.MONO_BOLD,
                         min(13, self.cell_fs - 2), r.text, anchor="mm")
            return
        if a.kind == "cells":
            if not a.cells:
                pen.rrect((L.left_x, y, L.left_x + 74, y + 30), radius=7,
                          fill="#FBFCFD", outline="#E1E5EA", width=1)
                pen.text((L.left_x + 37, y + 15), "empty", theme.MONO, 11,
                         theme.FAINT, anchor="mm")
                return
            x = L.left_x
            for k, val in enumerate(a.cells):
                role = a.roles[k] if k < len(a.roles) else "window"
                r = theme.ROLES.get(role, theme.ROLES["window"])
                w = max(34, pen.text_w(val, theme.MONO_BOLD, 12.5) + 18)
                pen.rrect((x, y, x + w, y + 30), radius=7, fill=r.fill,
                          outline=r.border, width=1.3)
                pen.text((x + w / 2, y + 15), val, theme.MONO_BOLD, 12.5,
                         r.text, anchor="mm")
                if k < len(a.subs) and a.subs[k]:
                    pen.text((x + w / 2, y + 38), a.subs[k], theme.MONO, 9.5,
                             theme.FAINT, anchor="mm")
                x += w + 6
        else:
            x = L.left_x
            for k, v in a.chips:
                txt = f"{k}: {v}"
                w = pen.text_w(txt, theme.MONO, 12) + 18
                pen.rrect((x, y, x + w, y + 28), radius=7, fill="#F4F6F9",
                          outline="#E1E5EA", width=1)
                pen.text((x + w / 2, y + 14), txt, theme.MONO, 12,
                         theme.INK, anchor="mm")
                x += w + 6

    def _draw_state(self, pen: Pen, f: Frame):
        L = self.L
        x, y = L.left_x, self.y_state
        for k, v in f.state:
            kw = pen.text_w(k, theme.SANS_MED, 11)
            vw = pen.text_w(v, theme.MONO_BOLD, 12)
            w = kw + vw + 26
            pen.rrect((x, y, x + w, y + 26), radius=8, fill=theme.PANEL,
                      outline="#E4E8ED", width=1)
            pen.text((x + 10, y + 13), k, theme.SANS_MED, 11, theme.MUTED, anchor="lm")
            pen.text((x + 16 + kw, y + 13), v, theme.MONO_BOLD, 12, theme.INK, anchor="lm")
            x += w + 8

    def _draw_code(self, pen: Pen, f: Frame):
        L = self.L
        x0, y0 = L.code_x, self.y_code
        x1, y1 = x0 + L.code_w, y0 + self.code_h
        pen.rrect((x0, y0, x1, y1), radius=10, fill=theme.CODE_BG,
                  outline="#E4E8ED", width=1)
        pen.text((x0 + 14, y0 + 10), "solution.py", theme.MONO, 10.5, theme.FAINT)
        pen.line([(x0 + 1, y0 + 29), (x1 - 1, y0 + 29)], "#EDF0F3", 1)

        ty = y0 + 36
        for k, src in enumerate(self.t.code, start=1):
            row_y = ty + (k - 1) * self.code_lh
            if f.line == k:
                pen.rrect((x0 + 6, row_y - 3, x1 - 6, row_y + self.code_fs + 4),
                          radius=5, fill=theme.CODE_HL)
                pen.rect((x0 + 6, row_y - 3, x0 + 8.5, row_y + self.code_fs + 4),
                         fill=theme.CODE_HL_BAR)
            pen.text((x0 + 30, row_y), f"{k:>2}", theme.MONO, self.code_fs - 1.5,
                     theme.CODE_GUTTER, anchor="ra")
            cx = x0 + 38
            for txt, col in tokenize(src):
                pen.text((cx, row_y), txt, theme.MONO, self.code_fs, col)
                cx += pen.text_w(txt, theme.MONO, self.code_fs)

    def _draw_note(self, pen: Pen, f: Frame):
        L = self.L
        bg, br, fg, _ = theme.VERDICTS.get(f.verdict, theme.VERDICTS[None])
        x0, y0 = L.pad, self.y_note
        x1, y1 = self.W - L.pad, self.y_note + L.note_h
        pen.rrect((x0, y0, x1, y1), radius=10, fill=bg, outline=br, width=1)
        pen.rrect((x0, y0 + 8, x0 + 4, y1 - 8), radius=2, fill=br)

        tx = x0 + 18
        label = {"valid": "VALID", "invalid": "VIOLATION", "record": "NEW BEST",
                 "info": "STEP", "drop": "DISCARD",
                 "count": "COUNTED"}.get(f.verdict or "", "")
        if label:
            lw = pen.text_w(label, theme.SANS_BOLD, 10) + 18
            pen.rrect((tx, y0 + (L.note_h - 20) / 2, tx + lw, y0 + (L.note_h + 20) / 2),
                      radius=10, fill=mix(br, "#FFFFFF", 0.55), outline=br, width=1)
            pen.text((tx + lw / 2, y0 + L.note_h / 2), label, theme.SANS_BOLD, 10,
                     fg, anchor="mm")
            tx += lw + 14

        lines = wrap(pen, f.note, theme.SANS, 13.5, x1 - tx - 18, max_lines=2)
        if len(lines) == 1:
            pen.text((tx, y0 + L.note_h / 2), lines[0], theme.SANS, 13.5,
                     mix(fg, theme.INK, 0.35), anchor="lm")
        else:
            for k, ln in enumerate(lines):
                pen.text((tx, y0 + L.note_h / 2 - 10 + k * 19), ln, theme.SANS, 13.5,
                         mix(fg, theme.INK, 0.35), anchor="lm")


def _palette(frames: list[Image.Image], colors: int = 220) -> Image.Image:
    """Build one palette that covers every frame, so colours never drift between frames."""
    step = max(1, len(frames) // 48)
    sample = frames[::step] or frames[:1]
    w = max(1, sample[0].width // 4)
    h = max(1, sample[0].height // 4)
    swatches = []
    for r in theme.ROLES.values():
        swatches += [r.fill, r.border, r.text]
    for c in list(theme.POINTER_COLORS.values()) + [theme.POINTER_FALLBACK]:
        swatches += [c, mix(c, "#FFFFFF", 0.88), mix(c, "#FFFFFF", 0.45)]
    for v in theme.VERDICTS.values():
        swatches += [v[0], v[1], v[2], mix(v[1], "#FFFFFF", 0.55)]
    swatches += list(theme.SYN.values()) + [theme.BG, theme.PANEL, theme.INK,
                                            theme.MUTED, theme.FAINT, theme.RULE,
                                            theme.CODE_BG, theme.CODE_HL,
                                            theme.CODE_HL_BAR, theme.CODE_GUTTER]
    sw = 8
    per_row = max(1, w // sw)
    rows = (len(swatches) + per_row - 1) // per_row
    strip = Image.new("RGB", (w, h * len(sample) + rows * sw), "#FFFFFF")
    for i, im in enumerate(sample):
        strip.paste(im.resize((w, h), Image.LANCZOS), (0, i * h))
    d = ImageDraw.Draw(strip)
    y0 = h * len(sample)
    for k, c in enumerate(swatches):
        cx, cy = (k % per_row) * sw, y0 + (k // per_row) * sw
        d.rectangle([cx, cy, cx + sw - 1, cy + sw - 1], fill=c)
    return strip.quantize(colors=colors, method=Image.MEDIANCUT)


def save_gif(trace: Trace, path: str, *, base_ms: int = 900, end_ms: int = 2200,
             layout: Layout | None = None, also_png: bool = False) -> str:
    r = Renderer(trace, layout)
    frames = [r.render(f) for f in trace.frames]
    pal = _palette(frames)
    pframes = [im.quantize(palette=pal, dither=Image.Dither.NONE) for im in frames]
    durations = [max(120, int(base_ms * f.hold)) for f in trace.frames]
    durations[-1] = max(durations[-1], end_ms)
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    pframes[0].save(path, save_all=True, append_images=pframes[1:],
                    duration=durations, loop=0, optimize=True, disposal=1)
    if also_png:
        stem = os.path.splitext(path)[0]
        frames[0].save(f"{stem}-first.png")
        frames[len(frames) // 2].save(f"{stem}-mid.png")
        frames[-1].save(f"{stem}-last.png")
    return path
