#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Screenshots of the fixed result block, 15 Nov 2026 (tax-engine fix).

Three states, each driven for real — nothing is injected into the DOM:
  1. range-large-gift   band r17, HK$250,000  -> the band renders 13,245 – 42,500
  2. exact-income       same gift, exact income HK$500,000 -> the capped 29,150
  3. exact-row          the new collapsed row, open, in the calculator block

The figures printed next to each shot are read out of the same DOM the image
was taken from, so the image and the claim cannot drift apart.

Usage: python3 qa/shots_taxfix_20261115.py [base-url]
"""
import os
import sys
from playwright.sync_api import sync_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8765"
OUT = os.path.expanduser("~/2SK/fred-hollows/work/iframe-poc/screens/taxfix-20261115")
os.makedirs(OUT, exist_ok=True)

READ = """() => ({
  gift:   document.getElementById('gift-out').textContent.trim(),
  saved:  document.getElementById('saved').textContent.trim(),
  label:  document.getElementById('saved-label').textContent.trim(),
  net:    document.getElementById('net').textContent.trim(),
  rate:   document.getElementById('rate').textContent.trim(),
  rlabel: document.getElementById('rate-label').textContent.trim(),
  caption:document.getElementById('net-caption').textContent.trim(),
  benefit:document.getElementById('benefit').textContent.trim(),
})"""


def shot(b, w, tag, drive=None, target="#result", open_row=False):
    p = b.new_page(viewport={"width": w, "height": 900},
                   is_mobile=(w < 600), has_touch=(w < 600), device_scale_factor=2)
    p.goto(f"{BASE}/embed/?part=calc", wait_until="load")
    p.wait_for_timeout(450)
    if drive:
        drive(p, w)
        p.wait_for_timeout(350)
    data = p.evaluate(READ)
    el = p.query_selector(target)
    path = os.path.join(OUT, f"{tag}.png")
    el.screenshot(path=path)
    size = os.path.getsize(path)
    box = el.bounding_box()
    print(f"{tag:26} {w}px  {int(box['width'])}x{int(box['height'])}px  {size:,}B")
    print(f"{'':26} saved {data['saved']}  ({data['label']})")
    print(f"{'':26} net {data['net']}  rate {data['rate']}  ({data['rlabel']})")
    print(f"{'':26} caption {data['caption']}")
    p.close()
    return path


with sync_playwright() as pw:
    b = pw.chromium.launch(channel="chrome", headless=True)

    def large_gift(p, w):
        p.fill("#gift", "250000")
        # below 721px the picker is a native <select>; above it, radios
        if w < 721:
            p.select_option("#band-mobile", "r17")
        else:
            p.click('input[name="band"][value="r17"]')

    def exact(p, w):
        p.fill("#gift", "250000")
        p.evaluate("()=>{document.getElementById('exact-row').open = true;}")
        p.fill("#exact", "500000")

    print("— result block —")
    shot(b, 390, "range-large-gift-390", large_gift)
    shot(b, 1440, "range-large-gift-1440", large_gift)
    shot(b, 390, "exact-income-390", exact)
    shot(b, 1440, "exact-income-1440", exact)

    print("\n— calculator block (the new collapsed row) —")
    shot(b, 390, "exact-row-closed-390", None, target="#calculator")
    shot(b, 390, "exact-row-open-390", exact, target="#calculator")
    b.close()

print(f"\n-> {OUT}")
