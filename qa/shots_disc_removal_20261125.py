#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Evidence screenshots for the pass that removed the disclaimer from the widget.

Full-page `?part=all` at 390 and 1440, both languages, plus a crop of the FOOT of
each document — the place the disclaimer used to occupy. The foot crop is the
point: the document must end on the payment block with no orphan rule and no
dangling spacing, and that is exactly what a passing measurement cannot show.

    /Library/Developer/CommandLineTools/usr/bin/python3 qa/shots_disc_removal_20261125.py
"""
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8765"
OUT = Path(__file__).resolve().parent.parent / "shots" / "disc-removal-20261125"
OUT.mkdir(parents=True, exist_ok=True)

with sync_playwright() as pw:
    b = pw.chromium.launch(channel="chrome", headless=True)
    for tag, q in (("zh", ""), ("en", "&lang=en")):
        for w in (390, 1440):
            p = b.new_page(viewport={"width": w, "height": 900},
                           is_mobile=(w < 600), has_touch=(w < 600))
            p.goto(f"{BASE}/embed/?part=all{q}", wait_until="load")
            p.wait_for_timeout(800)
            p.screenshot(path=str(OUT / f"all-{tag}-{w}-full.png"), full_page=True)
            # the last 520px of the document: where the disclaimer used to be
            h = p.evaluate("()=>document.documentElement.scrollHeight")
            # scrolled to the last viewport: the foot crop must show the END of the
            # document, not a clip rectangle computed from a taller full-page image
            p.evaluate("()=>window.scrollTo(0, document.documentElement.scrollHeight)")
            p.wait_for_timeout(300)
            p.screenshot(path=str(OUT / f"all-{tag}-{w}-foot.png"))
            print(tag, w, h)
            p.close()
    b.close()
print(f"wrote {OUT}")
