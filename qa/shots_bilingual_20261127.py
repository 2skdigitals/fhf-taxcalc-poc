#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Local visual proof of the two languages after the English-crop pass.

Writes, into shots/20261227-bilingual/:
  page-zh.png / page-en.png      the mock host page (/preview/) at 1280 wide, full height
  pay-zh.png  / pay-en.png       the payment block alone, AlipayHK receipt tooltip OPEN
  pay-zh-2.png / pay-en-2.png    the same tooltip scrolled to Option 2 (the claim-it-later flow)

Usage: start a server on the repo root, then
  python3 qa/shots_bilingual_20261127.py http://127.0.0.1:8777
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8777"
OUT = Path(__file__).resolve().parent.parent / "shots" / "20261127-bilingual"
OUT.mkdir(parents=True, exist_ok=True)

with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome")

    # 1 · the page, both languages
    for tag, q in (("zh", ""), ("en", "?lang=en")):
        pg = b.new_page(viewport={"width": 1280, "height": 900})
        pg.goto(f"{BASE}/preview/{q}", wait_until="load")
        pg.wait_for_timeout(2500)
        h = pg.evaluate("document.documentElement.scrollHeight")
        pg.screenshot(path=str(OUT / f"page-{tag}.png"), full_page=True)
        print(f"page-{tag}.png  {1280}x{h}")
        pg.close()

    # 2 · the payment block with the tooltip open, then scrolled to Option 2
    for tag, lang in (("zh", "zh"), ("en", "en")):
        pg = b.new_page(viewport={"width": 1100, "height": 1300}, device_scale_factor=1)
        pg.goto(f"{BASE}/embed/?part=pay&lang={lang}", wait_until="load")
        pg.wait_for_timeout(900)
        pg.click("#alipay-help")
        pg.wait_for_timeout(1200)
        pg.screenshot(path=str(OUT / f"pay-{tag}.png"))
        pg.evaluate("() => { const p = document.querySelector('#alipay-help-panel');"
                    " p.scrollTop = p.querySelector('[data-opt=\"2\"]').offsetTop - 40; }")
        pg.wait_for_timeout(700)
        pg.screenshot(path=str(OUT / f"pay-{tag}-2.png"))
        pg.close()

    b.close()
print("done ->", OUT)
