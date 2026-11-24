#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Screenshots of the rebuilt AlipayHK receipt tooltip — both flows, both languages.

Four states per language: the panel as it opens (Option 1 first) and scrolled to
Option 2, at 390px (phone, panel full width below the trigger) and 1440px
(desktop, 420px panel opening upward). Each is written twice: the block as the
donor sees it, and a clip of the panel alone so the copy is legible at review
size.

    python3 qa/shots_alipay_two_options_20261124.py [--base http://127.0.0.1:8765]
"""
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "shots" / "alipay-two-options-20261124"
ARGS = sys.argv[1:]
BASE = "http://127.0.0.1:8765"
for i, a in enumerate(ARGS):
    if a == "--base" and i + 1 < len(ARGS):
        BASE = ARGS[i + 1]

# the declared payment frame per language (docs/INTERFACE.md §2)
FRAME = {"zh-HK": 690, "en": 800}
OUT.mkdir(parents=True, exist_ok=True)

with sync_playwright() as pw:
    b = pw.chromium.launch(channel="chrome", headless=True)
    for lang in ("zh-HK", "en"):
        q = "" if lang == "zh-HK" else "&lang=en"
        for w in (390, 1440):
            p = b.new_page(viewport={"width": w, "height": FRAME[lang]},
                           is_mobile=(w < 600), has_touch=(w < 600))
            p.goto(f"{BASE}/embed/?part=pay{q}", wait_until="load")
            p.wait_for_timeout(500)
            p.click("#alipay-help")
            p.wait_for_timeout(900)
            for shot, scroll_to in (("option-1", None), ("option-2", 2)):
                if scroll_to:
                    p.evaluate("""(n)=>{
                      const pop=document.getElementById('alipay-help-panel');
                      const sec=pop.querySelector('.hsec[data-opt="'+n+'"]');
                      pop.scrollTop=sec.offsetTop-8;
                    }""", scroll_to)
                    p.wait_for_timeout(700)
                stem = OUT / f"{lang}-{w}-{shot}"
                p.screenshot(path=str(stem) + ".png")
                box = p.evaluate("""()=>{const r=document.getElementById('alipay-help-panel')
                    .getBoundingClientRect();return {x:r.x-8,y:r.y-8,
                    width:r.width+16,height:r.height+16};}""")
                p.screenshot(path=str(stem) + "-panel.png", clip=box)
                h = p.evaluate("""()=>{const pop=document.getElementById('alipay-help-panel');
                    return {top:pop.scrollTop, sc:pop.scrollHeight, ch:pop.clientHeight};}""")
                print(f"{lang:6} {w:>5}px {shot:9} panel scroll {h['top']}/{h['sc']} "
                      f"(view {h['ch']}) -> {stem.name}.png")
            p.close()
    b.close()
print(f"\nwrote {len(list(OUT.glob('*.png')))} files to {OUT}")
