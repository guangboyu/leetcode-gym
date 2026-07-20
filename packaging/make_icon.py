#!/usr/bin/env python3
"""Generate packaging/AppIcon.icns for the desktop app.

Draws a macOS-style rounded-square ("squircle") icon: an indigo->cyan gradient
with a subtle spaced-repetition retention curve and a bold check mark. Renders a
1024px master (4x supersampled for clean edges), emits every size macOS wants
into a .iconset, then calls `iconutil` to assemble the .icns.

Run from the repo root:  python3 packaging/make_icon.py
No args; overwrites packaging/AppIcon.icns.
"""
import math
import os
import subprocess
import tempfile

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_ICNS = os.path.join(HERE, "AppIcon.icns")

SS = 4                      # supersample factor for anti-aliasing
BASE = 1024
S = BASE * SS


def lerp(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def render_master():
    """Return the 1024px master icon as an RGBA image."""
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Rounded-square mask (macOS icons leave a small transparent margin).
    margin = int(S * 0.085)
    box = (margin, margin, S - margin, S - margin)
    radius = int((box[2] - box[0]) * 0.235)   # ~squircle corner

    # Vertical gradient fill, painted row by row inside the rounded rect.
    top = (0x4F, 0x46, 0xE5)     # indigo
    bot = (0x06, 0xB6, 0xD4)     # cyan
    grad = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grad)
    for y in range(box[1], box[3]):
        t = (y - box[1]) / (box[3] - box[1])
        gd.line([(box[0], y), (box[2], y)], fill=lerp(top, bot, t) + (255,))

    mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(mask).rounded_rectangle(box, radius=radius, fill=255)
    img.paste(grad, (0, 0), mask)
    d = ImageDraw.Draw(img)

    cx = S // 2

    # Subtle forgetting/retention curve — a soft descending-then-reset arc,
    # drawn semi-transparent so it reads as texture, not clutter.
    curve = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    cdraw = ImageDraw.Draw(curve)
    w = int(S * 0.012)
    pts = []
    x0, x1 = box[0] + int(S * 0.10), box[2] - int(S * 0.10)
    y_hi, y_lo = int(S * 0.62), int(S * 0.30)
    for i in range(220):
        t = i / 219
        x = x0 + (x1 - x0) * t
        # exponential decay bumped by periodic review "resets"
        phase = (t * 3) % 1.0
        decay = math.exp(-2.4 * phase)
        y = y_lo + (y_hi - y_lo) * (1 - decay)
        pts.append((x, y))
    cdraw.line(pts, fill=(255, 255, 255, 60), width=w, joint="curve")
    img.alpha_composite(curve)

    d = ImageDraw.Draw(img)

    # Bold rounded check mark, centered slightly high.
    lw = int(S * 0.075)
    p1 = (cx - int(S * 0.20), cx - int(S * 0.02))
    p2 = (cx - int(S * 0.045), cx + int(S * 0.16))
    p3 = (cx + int(S * 0.235), cx - int(S * 0.20))
    d.line([p1, p2, p3], fill=(255, 255, 255, 255), width=lw, joint="curve")
    # round the stroke ends
    r = lw // 2
    for (px, py) in (p1, p2, p3):
        d.ellipse([px - r, py - r, px + r, py + r], fill=(255, 255, 255, 255))

    return img.resize((BASE, BASE), Image.LANCZOS)


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


if __name__ == "__main__":
    main()
