#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Capture the payment block at the widths Kevin's brief names, both languages.

Two uses, one script:
  · a BEFORE corpus (git stash / saved copy) and an AFTER corpus, compared pixel
    for pixel at 390px — mobile must be untouched by a desktop-only design pass;
  · the delivered shots of the Option B desktop block and its receipt panel.

Usage:
    python3 qa/shot_pay_desktop_20261124.py <outdir> [--panel] [--tag]

Deterministic on purpose: fixed viewport, deviceScaleFactor 1, animations off,
lazy images forced eager and every web font settled — so two runs of the same
HTML are byte-comparable and a diff means a layout change, not a timer.
"""
import pathlib
import sys

from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8765"
OUT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "shots/pay-desktop-20261124")
PANEL = "--panel" in sys.argv
TAG = ""
for i, a in enumerate(sys.argv):
    if a == "--tag" and i + 1 < len(sys.argv):
        TAG = sys.argv[i + 1]

WIDTHS = (390, 768, 1024, 1440)
LANGS = (("zh-HK", ""), ("en", "&lang=en"))

OUT.mkdir(parents=True, exist_ok=True)

SETTLE = """() => {
  document.querySelectorAll('img[loading=lazy]').forEach(i => i.loading = 'eager');
  document.querySelectorAll('*').forEach(el => {
    el.style.animation = 'none'; el.style.transition = 'none';
  });
}"""

with sync_playwright() as pw:
    b = pw.chromium.launch(channel="chrome", headless=True)
    for lang, q in LANGS:
        for w in WIDTHS:
            # a SHORT viewport: .wrap carries min-height:100vh, so a tall viewport
            # pads the capture with white and hides what actually grew
            p = b.new_page(viewport={"width": w, "height": 320}, device_scale_factor=1,
                           is_mobile=(w < 600), has_touch=(w < 600))
            p.goto(f"{BASE}/embed/?part=pay{q}", wait_until="load")
            p.evaluate(SETTLE)
            # every receipt crop decoded, every font metric final
            p.wait_for_function("() => [...document.images].every(i => i.complete)")
            p.wait_for_timeout(400)
            p.evaluate("async () => { await document.fonts.ready; }")
            height = p.evaluate("() => document.documentElement.scrollHeight")
            name = f"{lang}-{w}{TAG}.png"
            p.screenshot(path=str(OUT / name), full_page=True)
            print(f"{name:22} scrollHeight={height}")
            if PANEL and w >= 720:
                # the panel's height is capped against 100vh, so it is only
                # honest at the height the host actually declares for the block
                p.set_viewport_size({"width": w, "height": 690 if lang == "zh-HK" else 800})
                p.wait_for_timeout(200)
                p.click("#alipay-help")
                p.wait_for_timeout(500)
                p.screenshot(path=str(OUT / f"{lang}-{w}{TAG}-panel.png"), full_page=True)
                box = p.evaluate("""() => {
                  const pop = document.getElementById('alipay-help-panel');
                  const r = pop.getBoundingClientRect();
                  return {top: Math.round(r.top), bottom: Math.round(r.bottom),
                          left: Math.round(r.left), right: Math.round(r.right),
                          doc: document.documentElement.scrollHeight};
                }""")
                print(f"{'':22} panel {box}")
            p.close()
    b.close()
