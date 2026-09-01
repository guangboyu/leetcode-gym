#!/usr/bin/env python3
"""Render every tutorial animation to tutorials/assets/<pattern>/<slug>.gif.

    python render_all.py                  # render everything
    python render_all.py --list           # show what exists
    python render_all.py --only lc0003    # render one, by slug fragment
    python render_all.py --png            # also drop first/mid/last stills
"""
from __future__ import annotations

import argparse
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dsaviz import save_gif
from dsaviz.patterns import binary_search as bs
from dsaviz.patterns import chasing as ch
from dsaviz.patterns import linked_list as ll
from dsaviz.patterns import converging as cv
from dsaviz.patterns import monotonic_stack as ms
from dsaviz.patterns import parallel as pl
from dsaviz.patterns import prefix_sum as ps
from dsaviz.patterns import sliding_window as sw
from dsaviz.patterns import two_pointers as tp

# group folder -> list of builders
REGISTRY = {
    "sliding-window": [
        sw.lc643_fixed_window,
        sw.lc3_longest_substring,
        sw.lc424_shift_dont_shrink,
        sw.lc76_min_window,
        sw.lc424_high_water_mark,
        sw.lc239_window_maximum,
        sw.lc713_count_subarrays,
    ],
    "two-pointers": [
        tp.lc167_two_sum_sorted,
        cv.lc11_container,
        cv.lc42_two_pass,
        cv.lc42_trapping_water,
        ch.lc283_move_zeroes,
        ch.lc75_sort_colors,
        pl.lc88_merge_sorted,
        ll.lc142_floyd,
    ],
    "binary-search": [bs.lc704_binary_search],
    "monotonic-stack": [ms.lc739_daily_temperatures],
    "prefix-sum": [ps.lc560_subarray_sum],
}

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUT = os.path.abspath(os.path.join(HERE, "..", "assets"))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=DEFAULT_OUT, help="output directory")
    ap.add_argument("--only", default=None, help="render only slugs containing this text")
    ap.add_argument("--png", action="store_true", help="also write first/mid/last stills")
    ap.add_argument("--list", action="store_true", help="list available animations")
    ap.add_argument("--speed", type=float, default=1.0,
                    help="playback multiplier; 1.5 = 50%% faster")
    args = ap.parse_args()

    if args.list:
        for group, builders in REGISTRY.items():
            for b in builders:
                print(f"{group:18s} {b().slug}")
        return 0

    total = 0
    for group, builders in REGISTRY.items():
        for build in builders:
            trace = build()
            if args.only and args.only not in trace.slug:
                continue
            path = os.path.join(args.out, group, f"{trace.slug}.gif")
            t0 = time.time()
            save_gif(trace, path, base_ms=int(900 / args.speed),
                     end_ms=int(2200 / args.speed), also_png=args.png)
            kb = os.path.getsize(path) // 1024
            total += kb
            rel = os.path.relpath(path, os.getcwd())
            print(f"  {rel:58s} {len(trace.frames):3d} frames  {kb:5d} KB  "
                  f"({time.time() - t0:.1f}s)")
    print(f"\n{total} KB total")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
