#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Screenshots for the 23 Nov disclaimer pass: the block at 390 and 1440, both languages.

Two crops per language per width: the block itself (element screenshot, so the
fine print is readable) and the receipt block's foot at 390, where the consent
line's #disc-link jump lands.
"""
import pathlib
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8765"
OUT = pathlib.Path(__file__).resolve().parent.parent / "shots" / "disc-list-20261123"
OUT.mkdir(parents=True, exist_ok=True)

with sync_playwright() as pw:
    b = pw.chromium.launch(channel="chrome")
    for lang, qs in (("zh", ""), ("en", "&lang=en")):
        for w, h in ((390, 900), (1440, 1100)):
            p = b.new_page(viewport={"width": w, "height": h},
                           is_mobile=(w < 600), has_touch=(w < 600))
            p.goto(f"{BASE}/embed/?part=receipt{qs}", wait_until="load")
            p.wait_for_timeout(600)
            el = p.query_selector("#disclaimer")
            el.screenshot(path=str(OUT / f"disclaimer-{lang}-{w}.png"))
            p.screenshot(path=str(OUT / f"receipt-foot-{lang}-{w}.png"), full_page=True)
            # the jump from the consent line, at phone width, then the focus ring
            if w == 390:
                p.evaluate("()=>window.scrollTo(0,0)")
                p.wait_for_timeout(150)
                p.click("#disc-link")
                p.wait_for_timeout(500)
                p.screenshot(path=str(OUT / f"after-disc-link-{lang}-{w}.png"))
                p.keyboard.press("Tab")
                p.wait_for_timeout(200)
                p.screenshot(path=str(OUT / f"link-focus-{lang}-{w}.png"))
            p.close()
    b.close()
print("shots in", OUT)
for f in sorted(OUT.glob("*.png")):
    print(" ", f.name, f.stat().st_size // 1024, "KB")
