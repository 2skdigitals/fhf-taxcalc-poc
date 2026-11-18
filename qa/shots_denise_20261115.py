#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Screenshots for the Denise revision, and the measurement behind them.

Each shot is taken at viewport = the height the client is told to set, so the
image IS what a donor sees inside the iframe. If a block's content were taller
than its declared height, the image would clip and the numbers printed beside
it would say so — the screenshot and the claim cannot drift apart.

Usage: python3 qa/shots_denise_20261115.py [base-url]
"""
import json
import os
import sys
from playwright.sync_api import sync_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8765"
OUT = os.path.expanduser("~/2SK/fred-hollows/work/iframe-poc/screens/denise-20261115")
DECLARED = {"calc": 1560, "pay": 1040}
WIDTHS = [(390, "390"), (568, "568"), (1440, "1440")]

os.makedirs(OUT, exist_ok=True)
manifest = []

with sync_playwright() as pw:
    b = pw.chromium.launch(channel="chrome", headless=True)
    for part in ("calc", "pay"):
        h = DECLARED[part]
        for w, tag in WIDTHS:
            p = b.new_page(viewport={"width": w, "height": h},
                           is_mobile=(w < 600), has_touch=(w < 600),
                           device_scale_factor=2)
            p.goto(f"{BASE}/embed/?part={part}", wait_until="load")
            p.wait_for_timeout(500)
            m = p.evaluate("""()=>({
                sh: document.documentElement.scrollHeight,
                ch: document.documentElement.clientHeight,
                sw: document.documentElement.scrollWidth,
                cw: document.documentElement.clientWidth,
                inner: (()=>{const d=document.documentElement;
                        return d.scrollHeight - d.clientHeight;})()
            })""")
            path = os.path.join(OUT, f"{part}-{tag}.png")
            p.screenshot(path=path, full_page=False)
            size = os.path.getsize(path)
            fits = m["sh"] <= h + 1
            print(f"{part:5} {tag:>5}px  content {m['sh']:>5}  box {h:>5}  "
                  f"inner-overflow {max(0, m['sh']-h):>4}px  "
                  f"h-overflow {max(0, m['sw']-m['cw']):>3}px  "
                  f"{'FITS' if fits else 'CLIPS'}  {os.path.basename(path)} {size:,}B")
            manifest.append(dict(part=part, width=w, declared=h, content=m["sh"],
                                 h_overflow=max(0, m["sw"] - m["cw"]),
                                 fits=fits, file=f"{part}-{tag}.png", bytes=size))
            p.close()
    b.close()

with open(os.path.join(OUT, "measurements.json"), "w") as f:
    json.dump(manifest, f, indent=2)
print(f"\n{len(manifest)} shots -> {OUT}")
