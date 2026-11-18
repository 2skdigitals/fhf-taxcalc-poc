#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sweep widths to find the real maximum content height of every block.

A responsive change measured only at one width is how a block ships with an
inner scrollbar: the peak is usually at the narrow end, or in the band where a
control switches type (here: the income picker becomes a native <select> below
721px and a two-column radio list from 721px).

Two languages, two height contracts. English is not automatically shorter than
Chinese: at phone widths it costs more lines (more words per sentence), while at
desktop widths it costs fewer. The peak of each block is therefore measured per
language and declared separately — see docs/INTERFACE.md §2.

Usage:
    python3 qa/sweep_heights.py                  # both languages
    python3 qa/sweep_heights.py --lang en
    python3 qa/sweep_heights.py --base http://127.0.0.1:8765
"""
import json
import sys
from playwright.sync_api import sync_playwright

ARGS = sys.argv[1:]
BASE = "http://127.0.0.1:8765"
LANGS = ["zh-HK", "en"]
for i, a in enumerate(ARGS):
    if a == "--base" and i + 1 < len(ARGS):
        BASE = ARGS[i + 1]
    if a == "--lang" and i + 1 < len(ARGS):
        LANGS = [ARGS[i + 1]]

PARTS = ["calc", "input", "result", "pay", "receipt"]
WIDTHS = [320, 328, 360, 390, 414, 430, 480, 540, 568, 600, 640, 700, 721, 768,
          820, 900, 944, 1024, 1100, 1200, 1280, 1440]

# peak + 45..70px of slack, measured not assumed (see the peaks printed below).
# English peaks are HIGHER than Chinese at every width: 35% more lines at 320px,
# where the column is ~288px wide and a sentence costs two lines instead of one.
DECLARED = {
    "zh-HK": {"calc": 1500, "input": 900, "result": 750, "pay": 550, "receipt": 780},
    "en":    {"calc": 1500, "input": 900, "result": 750, "pay": 550, "receipt": 890},
}

peaks = {}
with sync_playwright() as pw:
    b = pw.chromium.launch(channel="chrome", headless=True)
    for lang in LANGS:
        peaks[lang] = {}
        print(f"\n=== ?lang={lang} ===")
        for part in PARTS:
            rows = []
            for w in WIDTHS:
                # short viewport: .wrap has min-height:100vh, which would mask
                # any content shorter than the viewport and hide the real number
                p = b.new_page(viewport={"width": w, "height": 240},
                               is_mobile=(w < 600), has_touch=(w < 600))
                p.goto(f"{BASE}/embed/?part={part}&lang={lang}", wait_until="load")
                p.wait_for_timeout(400)
                rows.append((w, p.evaluate("()=>document.documentElement.scrollHeight")))
                p.close()
            top = max(rows, key=lambda r: r[1])
            declared = DECLARED[lang][part]
            peaks[lang][part] = {"max": top[1], "at": top[0], "declared": declared,
                                 "slack": declared - top[1], "curve": rows}
            print(f"?part={part:8} peak {top[1]:>5}px at {top[0]:>4}px | "
                  f"declared {declared:>5} | slack {declared-top[1]:>4} "
                  f"{'OK' if declared >= top[1] else 'OVERFLOW'}")
            lo = min(r[1] for r in rows)
            print(f"{'':16} range {lo}–{top[1]} across {len(WIDTHS)} widths")
    b.close()

if len(LANGS) == 2:
    print(f"\n{'block':10} {'zh-HK peak':>12} {'en peak':>9}  width  | "
          f"{'zh declared':>12} {'en declared':>12}")
    for part in PARTS:
        z, e = peaks["zh-HK"][part], peaks["en"][part]
        print(f"?part={part:<4} {z['max']:>8} @{z['at']:<4} {e['max']:>5} @{e['at']:<4}      | "
              f"{z['declared']:>12} {e['declared']:>12}")

with open("/tmp/fhf-sweep.json", "w") as f:
    json.dump(peaks, f, indent=2)
print("\nwrote /tmp/fhf-sweep.json")

over = [p for l in peaks for p in peaks[l] if peaks[l][p]["max"] > peaks[l][p]["declared"]]
if over:
    print(f"OVERFLOW in {len(over)} block(s): " + ", ".join(f"{l}/{p}" for l in peaks for p in peaks[l]
                                                           if peaks[l][p]["max"] > peaks[l][p]["declared"]))
    sys.exit(1)
