#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Quick DOM probe for the phase-1 / AlipayHK pass — read-only, prints facts."""
import sys
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8765"

with sync_playwright() as pw:
    b = pw.chromium.launch(channel="chrome", headless=True)

    # 1 · the receipt module is gone from phase 1, the disclaimer is not
    for lang in ("", "&lang=en"):
        for part in ("all", "pay", "receipt", "calc", "input", "result"):
            p = b.new_page(viewport={"width": 390, "height": 900}, is_mobile=True, has_touch=True)
            p.goto(f"{BASE}/embed/?part={part}{lang}", wait_until="load")
            p.wait_for_timeout(500)
            r = p.evaluate("""() => {
              const vis = e => !!e && e.getBoundingClientRect().height > 0 && getComputedStyle(e).display !== 'none';
              const rc = document.getElementById('receipt'), d = document.getElementById('disclaimer');
              return {
                h: document.documentElement.scrollHeight,
                receipt_h: rc ? Math.round(rc.getBoundingClientRect().height) : null,
                receipt_vis: vis(rc),
                form_vis: vis(document.getElementById('rform')),
                disc_vis: vis(d),
                disc_items: document.querySelectorAll('#disclaimer .disc-list > li').length,
                disc_h: d ? Math.round(d.getBoundingClientRect().height) : 0,
                last_panel: [...document.querySelectorAll('section.panel')].filter(vis).map(s => s.id).pop() || null,
                helps: [...document.querySelectorAll('[data-help]')].filter(vis).map(e => e.id),
                imgs_bad: [...document.images].filter(i => i.offsetParent && (!i.complete || i.naturalWidth === 0)).map(i => i.getAttribute('src')),
                step_ns: [...document.querySelectorAll('.step-n')].filter(e => e.offsetParent).map(e => e.textContent)
              };
            }""")
            print(f"{lang or 'zh':9} part={part:8} h={r['h']:5} receipt_vis={r['receipt_vis']!s:5} "
                  f"form_vis={r['form_vis']!s:5} disc_vis={r['disc_vis']!s:5} items={r['disc_items']} "
                  f"last={r['last_panel']} helps={r['helps']} steps={r['step_ns']} bad={r['imgs_bad']}")
            p.close()

    # 2 · the tooltip itself, open, at 390 and 1440
    for w in (390, 1440):
        for lang, frame in (("", 640), ("&lang=en", 750)):
            p = b.new_page(viewport={"width": w, "height": frame}, is_mobile=(w == 390), has_touch=(w == 390))
            p.goto(f"{BASE}/embed/?part=pay{lang}", wait_until="load")
            p.wait_for_timeout(500)
            before = p.evaluate("()=>({hidden:document.getElementById('alipay-help-panel').hidden,"
                                "exp:document.getElementById('alipay-help').getAttribute('aria-expanded')})")
            p.click("#alipay-help")
            p.wait_for_timeout(600)
            after = p.evaluate("""() => {
              const pop = document.getElementById('alipay-help-panel');
              const r = pop.getBoundingClientRect(), d = document.documentElement;
              return {hidden: pop.hidden, w: Math.round(r.width), x: Math.round(r.left),
                      top: Math.round(r.top), bottom: Math.round(r.bottom),
                      right: Math.round(r.right), vw: d.clientWidth,
                      h: Math.round(r.height), frame: d.clientHeight,
                      scrolls: pop.scrollHeight > pop.clientHeight + 1,
                      docH: d.scrollHeight,
                      steps: [...pop.querySelectorAll('.n')].map(n => n.textContent),
                      imgs: [...pop.querySelectorAll('img')].map(i => ({s: i.getAttribute('src').split('/').pop(),
                              ok: i.complete && i.naturalWidth > 0, alt: (i.getAttribute('alt') || '').slice(0, 30)})),
                      line: document.querySelector('.payhelp-line').textContent.trim(),
                      line_h: Math.round(document.querySelector('.payhelp-line').getBoundingClientRect().height)};
            }""")
            print(f"\n--- w={w} {lang or 'zh'} frame={frame}")
            print("   closed:", before)
            print("   open  :", {k: after[k] for k in ("hidden", "w", "x", "top", "bottom", "right", "vw", "h", "frame",
                                                      "scrolls", "docH", "line", "line_h")})
            print("   steps :", after["steps"])
            print("   imgs  :", [(i["s"], i["ok"]) for i in after["imgs"]])
            print("   alts  :", [i["alt"] for i in after["imgs"]])
            p.close()

    b.close()
