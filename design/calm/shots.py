#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Shoot each block at its recommended declared height, 390 and 1280, English.

    python3 shots.py --dir shots
"""
import argparse, os
from playwright.sync_api import sync_playwright

ap = argparse.ArgumentParser()
ap.add_argument("--base", default="http://127.0.0.1:8766/index.html")
ap.add_argument("--dir", default="shots")
ap.add_argument("--lang", default="en")
ap.add_argument("--prefix", default="")
a = ap.parse_args()

# declared height per block at each width class, filled from measurement
H = {
    "390":  {"calc": 0, "pay": 0, "receipt": 0},
    "1280": {"calc": 0, "pay": 0, "receipt": 0},
}
import json, sys
cfgpath = "heights.json"
if os.path.exists(cfgpath):
    H = json.load(open(cfgpath))

os.makedirs(a.dir, exist_ok=True)
with sync_playwright() as pw:
    br = pw.chromium.launch(channel="chrome", headless=True)
    for w in ("390", "1280"):
        for part in ("calc", "pay", "receipt"):
            h = H[w][part]
            p = br.new_page(viewport={"width": int(w), "height": h},
                            is_mobile=(int(w) < 600), has_touch=(int(w) < 600),
                            device_scale_factor=2)
            p.goto(f"{a.base}?part={part}&lang={a.lang}", wait_until="load")
            p.wait_for_timeout(500)
            name = f"{a.dir}/{a.prefix}{part}-{a.lang}-{w}.png"
            p.screenshot(path=name, full_page=False)
            print(f"{name}  {os.path.getsize(name)} bytes  (viewport {w}x{h})")
            p.close()
    br.close()
