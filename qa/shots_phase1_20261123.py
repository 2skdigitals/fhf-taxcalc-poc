#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Evidence screenshots for the phase-1 / AlipayHK pass.

  · the payment block with the new receipt line, 390 and 1440, both languages
  · the tooltip open, both languages
  · the foot of `?part=all`, where the disclaimer now closes the page, both languages
"""
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8765"
OUT = Path(__file__).resolve().parent.parent / "shots" / "phase1-20261123"
OUT.mkdir(parents=True, exist_ok=True)

with sync_playwright() as pw:
    b = pw.chromium.launch(channel="chrome", headless=True)

    for lang, q, tag in (("", "", "zh"), ("&lang=en", "", "en")):
        pass

    for tag, q in (("zh", ""), ("en", "&lang=en")):
        for w, h in ((390, 900), (1440, 900)):
            p = b.new_page(viewport={"width": w, "height": h},
                           is_mobile=(w < 600), has_touch=(w < 600))
            p.goto(f"{BASE}/embed/?part=pay{q}", wait_until="load")
            p.wait_for_timeout(700)
            p.screenshot(path=str(OUT / f"pay-{tag}-{w}.png"))
            # open the tooltip and shoot it in place
            p.click("#alipay-help")
            p.wait_for_timeout(700)
            p.screenshot(path=str(OUT / f"tooltip-{tag}-{w}.png"))
            p.close()

        # the foot of the one-link arrangement: the disclaimer closes the page
        p = b.new_page(viewport={"width": 390, "height": 900}, is_mobile=True, has_touch=True)
        p.goto(f"{BASE}/embed/?part=all{q}", wait_until="load")
        p.wait_for_timeout(700)
        p.evaluate("()=>document.getElementById('disclaimer').scrollIntoView({block:'center'})")
        p.wait_for_timeout(500)
        p.screenshot(path=str(OUT / f"all-foot-{tag}-390.png"))
        p.close()

    b.close()

for f in sorted(OUT.glob("*.png")):
    print(f"{f.name}  {f.stat().st_size // 1024} KB")
