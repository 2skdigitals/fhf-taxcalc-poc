#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Measure every embed block's real content height at the widths the host page
actually hands the frame, plus tap-target sizes (WCAG 2.5.5 wants 44x44 CSS px).

Usage: python3 qa/measure_blocks.py [base-url]
"""
import json
import sys
from playwright.sync_api import sync_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8765"
PARTS = ["calc", "input", "result", "pay", "receipt"]
WIDTHS = [328, 360, 390, 568, 944, 1280]

TAP = """() => {
  const sel = ['#calculator .chips button', '.seg label', '#months', '#band-mobile',
               '.rform input[type=text]', '.rform input[type=email]',
               '.rform .consent', '.rform .consent label', '#rsubmit',
               '.rails button', '.rails a', 'details.q summary'];
  const out = {};
  for (const s of sel) {
    const els = [...document.querySelectorAll(s)].filter(e => e.offsetParent !== null);
    if (!els.length) continue;
    const hs = els.map(e => Math.round(e.getBoundingClientRect().height));
    out[s] = {n: els.length, min: Math.min(...hs), max: Math.max(...hs)};
  }
  return out;
}"""

with sync_playwright() as pw:
    b = pw.chromium.launch(channel="chrome", headless=True)
    print(f"{'part':10} " + "  ".join(f"{w:>6}" for w in WIDTHS))
    res = {}
    for part in PARTS:
        row = []
        for w in WIDTHS:
            # vh is deliberately tiny: .wrap has min-height:100vh, so a 900px
            # viewport masks any content shorter than 900. A short viewport
            # reveals the true content height instead of the floor.
            p = b.new_page(viewport={"width": w, "height": 240},
                           is_mobile=(w < 600), has_touch=(w < 600))
            p.goto(f"{BASE}/embed/?part={part}", wait_until="load")
            p.wait_for_timeout(420)
            h = p.evaluate("()=>document.documentElement.scrollHeight")
            row.append(h)
            res[f"{part}@{w}"] = h
            p.close()
        print(f"{'?part='+part:10} " + "  ".join(f"{v:>6}" for v in row))

    # overflow direction: does the document scroll horizontally anywhere?
    print("\ntap targets (min height px) at 390:")
    p = b.new_page(viewport={"width": 390, "height": 900}, is_mobile=True, has_touch=True)
    for part in ("calc", "pay", "receipt"):
        p.goto(f"{BASE}/embed/?part={part}", wait_until="load")
        p.wait_for_timeout(350)
        t = p.evaluate(TAP)
        print(f"  [{part}]")
        for k, v in t.items():
            flag = "" if v["min"] >= 44 else "  <-- under 44px"
            print(f"    {k:34} n={v['n']} h={v['min']}..{v['max']}{flag}")
    p.close()
    b.close()

with open("/tmp/fhf-heights.json", "w") as f:
    json.dump(res, f, indent=2)
print("\nwrote /tmp/fhf-heights.json")
