#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Where does the AlipayHK help panel actually land? Prints, per width and
language, the trigger offset and the OPEN panel's box against the declared
payment frame. A panel that ends outside the frame scrolls the host's fixed
box, which is the one failure a fixed-height embed cannot absorb."""
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8765"
WIDTHS = (320, 360, 390, 414, 568, 640, 721, 768, 900, 1024, 1280, 1440)
FRAME = {"zh-HK": 640, "en": 750}

with sync_playwright() as pw:
    b = pw.chromium.launch(channel="chrome", headless=True)
    for lang in ("zh-HK", "en"):
        q = "" if lang == "zh-HK" else "&lang=en"
        print(f"\n=== {lang} (frame {FRAME[lang]}px) ===")
        for w in WIDTHS:
            p = b.new_page(viewport={"width": w, "height": FRAME[lang]}, is_mobile=(w < 600), has_touch=(w < 600))
            p.goto(f"{BASE}/embed/?part=pay{q}", wait_until="load")
            p.wait_for_timeout(400)
            before = p.evaluate("()=>({doc:document.documentElement.scrollHeight})")
            p.click("#alipay-help")
            p.wait_for_timeout(450)
            r = p.evaluate("""() => {
              const pop = document.getElementById('alipay-help-panel');
              const b = pop.getBoundingClientRect(), d = document.documentElement;
              const t = document.getElementById('alipay-help').getBoundingClientRect();
              return {top: Math.round(b.top), bottom: Math.round(b.bottom),
                      w: Math.round(b.width), right: Math.round(b.right),
                      h: Math.round(b.height), doc: d.scrollHeight, vw: d.clientWidth,
                      vh: d.clientHeight,
                      trig: Math.round(t.top), over: d.scrollWidth > d.clientWidth + 1,
                      scrolls: pop.scrollHeight > pop.clientHeight + 1};
            }""")
            flag = "OK " if r["bottom"] <= FRAME[lang] and r["top"] >= 0 and r["doc"] <= FRAME[lang] else "BAD"
            print(f"  {w:>5} closed_doc={before['doc']:>4} trig={r['trig']:>4} "
                  f"panel top={r['top']:>4} bottom={r['bottom']:>4} h={r['h']:>4} w={r['w']:>4} "
                  f"open_doc={r['doc']:>4} {flag}")
            p.close()
    b.close()
