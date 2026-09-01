#!/usr/bin/env python3
"""Generate the app icon (packaging/AppIcon.icns) and the in-app favicon
(tracker/static/favicon.svg) from ONE geometry, so the Dock, the DMG and the
browser tab all show the same mark.

The mark: a dumbbell — two rounded plates joined by a bar — in the accent blue
(#2563EB, the "kept / valid" blue of the tutorial animations) on a soft
blue-to-white ground inside a macOS rounded square. Bit-for-bit derived from
tutorials/anim/dsaviz/theme.py: valid fill #DBEAFE, valid border #2563EB,
valid text #14356E.

Renders a 1024px master (4x supersampled for clean edges), emits every size
macOS wants into a .iconset, then calls `iconutil` to assemble the .icns.

Run from the repo root:  python3 packaging/make_icon.py
No args; overwrites packaging/AppIcon.icns and tracker/static/favicon.svg.
"""
import os
import subprocess
import tempfile

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
OUT_ICNS = os.path.join(HERE, "AppIcon.icns")
OUT_SVG = os.path.join(REPO, "tracker", "static", "favicon.svg")

SS = 4                      # supersample factor for anti-aliasing
BASE = 1024
S = BASE * SS

ACCENT = (0x25, 0x63, 0xEB)       # #2563EB
ACCENT_DEEP = (0x1D, 0x4E, 0xD8)  # #1D4ED8, plate shading
GROUND_TOP = (0xDB, 0xEA, 0xFE)   # #DBEAFE
GROUND_BOT = (0xFF, 0xFF, 0xFF)

# Geometry in unit coordinates (0..1 of the full canvas), shared by PNG + SVG.
MARGIN = 0.085                     # transparent margin macOS icons keep
CORNER = 0.235                     # squircle-ish corner radius (of the square side)
BAR = (0.22, 0.455, 0.78, 0.545)   # x0, y0, x1, y1 of the bar
PLATES = [                         # (x0, y0, x1, y1) — outer then inner, both sides
    (0.155, 0.335, 0.245, 0.665), (0.755, 0.335, 0.845, 0.665),
    (0.265, 0.275, 0.365, 0.725), (0.635, 0.275, 0.735, 0.725),
]
PLATE_R = 0.028                    # plate corner radius
BAR_R = 0.045


def lerp(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _px(v):
    return int(round(v * S))


def render_master():
    """Return the 1024px master icon as an RGBA image."""
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))

    margin = _px(MARGIN)
    box = (margin, margin, S - margin, S - margin)
    side = box[2] - box[0]
    radius = int(side * CORNER)

    # Ground: vertical soft-blue -> white gradient clipped to the rounded square.
    grad = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grad)
    for y in range(box[1], box[3]):
        t = (y - box[1]) / (box[3] - box[1])
        gd.line([(box[0], y), (box[2], y)], fill=lerp(GROUND_TOP, GROUND_BOT, t) + (255,))
    mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(mask).rounded_rectangle(box, radius=radius, fill=255)
    img.paste(grad, (0, 0), mask)

    # A hairline inner border in the accent, very light, so the tile reads on
    # white backgrounds (Finder list view) without a hard edge.
    d = ImageDraw.Draw(img)
    d.rounded_rectangle(box, radius=radius, outline=(0x25, 0x63, 0xEB, 40), width=_px(0.006))

    # Dumbbell: bar first, plates on top; outer plates slightly deeper blue.
    x0, y0, x1, y1 = (_px(v) for v in BAR)
    d.rounded_rectangle((x0, y0, x1, y1), radius=_px(BAR_R), fill=ACCENT + (255,))
    for i, (px0, py0, px1, py1) in enumerate(PLATES):
        col = ACCENT_DEEP if i < 2 else ACCENT
        d.rounded_rectangle((_px(px0), _px(py0), _px(px1), _px(py1)),
                            radius=_px(PLATE_R), fill=col + (255,))

    return img.resize((BASE, BASE), Image.LANCZOS)


def render_svg():
    """Same mark as an SVG (16..64px favicon; tab icon in the browser build)."""
    def u(v):
        return f"{v * 100:.2f}"
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">',
             '<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1">'
             f'<stop offset="0" stop-color="#{GROUND_TOP[0]:02X}{GROUND_TOP[1]:02X}{GROUND_TOP[2]:02X}"/>'
             '<stop offset="1" stop-color="#FFFFFF"/></linearGradient></defs>']
    side = 1 - 2 * MARGIN
    parts.append(f'<rect x="{u(MARGIN)}" y="{u(MARGIN)}" width="{u(side)}" height="{u(side)}" '
                 f'rx="{u(side * CORNER)}" fill="url(#g)" stroke="#2563EB" stroke-opacity=".16" stroke-width=".6"/>')
    x0, y0, x1, y1 = BAR
    parts.append(f'<rect x="{u(x0)}" y="{u(y0)}" width="{u(x1 - x0)}" height="{u(y1 - y0)}" '
                 f'rx="{u(BAR_R)}" fill="#2563EB"/>')
    for i, (px0, py0, px1, py1) in enumerate(PLATES):
        col = "#1D4ED8" if i < 2 else "#2563EB"
        parts.append(f'<rect x="{u(px0)}" y="{u(py0)}" width="{u(px1 - px0)}" height="{u(py1 - py0)}" '
                     f'rx="{u(PLATE_R)}" fill="{col}"/>')
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def main():
    master = render_master()
    sizes = [16, 32, 128, 256, 512]
    with tempfile.TemporaryDirectory() as tmp:
        iconset = os.path.join(tmp, "AppIcon.iconset")
        os.makedirs(iconset)
        for sz in sizes:
            master.resize((sz, sz), Image.LANCZOS).save(
                os.path.join(iconset, f"icon_{sz}x{sz}.png"))
            master.resize((sz * 2, sz * 2), Image.LANCZOS).save(
                os.path.join(iconset, f"icon_{sz}x{sz}@2x.png"))
        subprocess.run(
            ["iconutil", "-c", "icns", iconset, "-o", OUT_ICNS], check=True)
    print("Wrote", OUT_ICNS)
    with open(OUT_SVG, "w", encoding="utf-8") as f:
        f.write(render_svg())
    print("Wrote", OUT_SVG)
    if os.environ.get("ICON_PREVIEW"):
        master.save(os.environ["ICON_PREVIEW"])
        print("Preview", os.environ["ICON_PREVIEW"])


if __name__ == "__main__":
    main()
