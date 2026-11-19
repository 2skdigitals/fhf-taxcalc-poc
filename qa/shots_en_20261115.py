#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Screenshots of the English build, 15 Nov 2026 — all five blocks, two widths.

Each shot is the whole block element at 2x DPR, so the image is literally what a
donor sees inside the frame and nothing below the fold can hide. The measured
element height is printed next to the declared height from docs/INTERFACE.md §2,
so a shot that would be clipped in the client's frame is visible in the output
rather than discovered on their page.

The Chinese build is captured at the same widths for side-by-side review: the
two languages are one file, and a reviewer approving the English should be able
to see what did not move.

Usage: python3 qa/shots_en_20261115.py [base-url]
"""
import os
import sys
from playwright.sync_api import sync_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8765"
OUT = os.path.expanduser("~/2SK/fred-hollows/work/iframe-poc/screens/en-20261115")
os.makedirs(OUT, exist_ok=True)

LANGS = ["en", "zh-HK"]
# the five embeddable blocks, and the element that IS that block
PARTS = [("calc", "#root"), ("input", "#calculator"), ("result", "#result"),
         ("pay", "#payment"), ("receipt", "#receipt")]
WIDTHS = [390, 1440]
DECLARED = {"zh-HK": {"calc": 1920, "input": 1120, "result": 920, "pay": 600, "receipt": 780},
            "en":    {"calc": 1920, "input": 1120, "result": 920, "pay": 600, "receipt": 890}}

rows = []
with sync_playwright() as pw:
    b = pw.chromium.launch(channel="chrome", headless=True)
    for lang in LANGS:
        print(f"— ?lang={lang} —")
        for part, target in PARTS:
            for w in WIDTHS:
                p = b.new_page(viewport={"width": w, "height": 900},
                               is_mobile=(w < 600), has_touch=(w < 600), device_scale_factor=2)
                p.goto(f"{BASE}/embed/?part={part}&lang={lang}", wait_until="load")
                p.wait_for_timeout(500)
                el = p.query_selector(target)
                tag = f"{part}-{w}" + ("" if lang == "en" else f"-{lang}")
                path = os.path.join(OUT, f"{tag}.png")
                el.screenshot(path=path)
                size = os.path.getsize(path)
                box = el.bounding_box()
                h = int(box["height"])
                decl = DECLARED[lang][part]
                rows.append((tag, lang, w, h, decl, size))
                print(f"{tag:22} {w:>4}px  {int(box['width'])}x{h}px  "
                      f"declared {decl}  {'OK' if h <= decl else 'OVERFLOW'}  {size:>9,}B")
                p.close()
    b.close()

print(f"\n{len(rows)} files, {sum(r[5] for r in rows):,} bytes total\n-> {OUT}")
