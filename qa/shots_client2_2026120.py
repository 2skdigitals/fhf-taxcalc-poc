#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Screenshots for the 20 Nov client-comment pass.

  python3 qa/shots_client2_2026120.py [--base http://127.0.0.1:8765]

Writes shots/client2-2026120/:
  calc-{w}-{lang}.png       ?part=input — the white ground and the wider column
  result-{w}-{lang}.png     ?part=result — the saving with no minus sign
  all-top-{w}-{lang}.png    ?part=all — the combined document, first screen
  all-bottom-{w}-{lang}.png ?part=all — the combined document, foot (payment + receipt)
"""
import os
import sys
from playwright.sync_api import sync_playwright

ARGS = sys.argv[1:]
BASE = "http://127.0.0.1:8765"
for i, a in enumerate(ARGS):
    if a == "--base" and i + 1 < len(ARGS):
        BASE = ARGS[i + 1]

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "shots", "client2-2026120")
os.makedirs(OUT, exist_ok=True)

VIEWS = [("calc", "input", 1040), ("result", "result", 890), ("all", "all", 2880)]
WIDTHS = (390, 1440)

with sync_playwright() as pw:
    b = pw.chromium.launch(channel="chrome", headless=True)
    for w in WIDTHS:
        for lang in ("zh-HK", "en"):
            for name, part, h in VIEWS:
                p = b.new_page(viewport={"width": w, "height": min(h, 1000)},
                               is_mobile=(w < 600), has_touch=(w < 600), device_scale_factor=1)
                p.goto(f"{BASE}/embed/?part={part}&lang={lang}", wait_until="load")
                p.wait_for_timeout(700)
                if name == "all":
                    top = os.path.join(OUT, f"all-top-{w}-{lang.split('-')[0]}.png")
                    p.screenshot(path=top)
                    p.evaluate("()=>window.scrollTo({top:document.documentElement.scrollHeight,behavior:'instant'})")
                    p.wait_for_timeout(400)
                    bot = os.path.join(OUT, f"all-bottom-{w}-{lang.split('-')[0]}.png")
                    p.screenshot(path=bot)
                    print(top, os.path.getsize(top))
                    print(bot, os.path.getsize(bot))
                else:
                    p.set_viewport_size({"width": w, "height": h})
                    p.wait_for_timeout(350)
                    f = os.path.join(OUT, f"{name}-{w}-{lang.split('-')[0]}.png")
                    p.screenshot(path=f, full_page=True)
                    print(f, os.path.getsize(f))
                p.close()
    b.close()
