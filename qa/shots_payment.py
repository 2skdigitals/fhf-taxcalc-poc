#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Payment-block screenshots at 390 (mobile rows) and 1440 (desktop QR grid),
in both languages. `--tag` names the output folder so a before/after pair can
be compared without overwriting.

    /Library/Developer/CommandLineTools/usr/bin/python3 qa/shots_payment.py --tag before
    /Library/Developer/CommandLineTools/usr/bin/python3 qa/shots_payment.py --tag after
"""
import argparse
import pathlib
import sys

from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8765"
OUT = pathlib.Path(__file__).resolve().parent.parent / "shots"

ap = argparse.ArgumentParser()
ap.add_argument("--tag", default="after")
ap.add_argument("--base", default=BASE)
args = ap.parse_args()
dest = OUT / f"payment-{args.tag}"
dest.mkdir(parents=True, exist_ok=True)

with sync_playwright() as pw:
    b = pw.chromium.launch(channel="chrome", headless=True)
    for lang in ("zh", "en"):
        for w, h in ((390, 1400), (1440, 1200)):
            p = b.new_page(viewport={"width": w, "height": h},
                           device_scale_factor=2, is_mobile=(w < 600), has_touch=(w < 600))
            url = f"{args.base}/embed/?part=pay" + ("&lang=en" if lang == "en" else "")
            p.goto(url, wait_until="load")
            p.wait_for_timeout(900)
            el = p.query_selector("#payment")
            path = dest / f"pay-{lang}-{w}.png"
            el.screenshot(path=str(path))
            box = p.evaluate("""() => {
              const g = document.querySelector('.paygrid'), r = document.querySelector('.rails');
              const vis = e => e && getComputedStyle(e).display !== 'none';
              const items = g ? [...g.children].filter(c => getComputedStyle(c).display !== 'none')
                                .map(c => { const b = c.getBoundingClientRect();
                                            return {x: Math.round(b.x), w: Math.round(b.width), h: Math.round(b.height)}; }) : [];
              const rows = r ? [...r.querySelectorAll('a')].map(a => ({rail: a.dataset.rail,
                                h: Math.round(a.getBoundingClientRect().height)})) : [];
              return {grid: vis(g), rails: vis(r), items, rows,
                      sectionH: Math.round(document.getElementById('payment').getBoundingClientRect().height),
                      docH: document.documentElement.scrollHeight};
            }""")
            print(f"{lang} {w}px  grid={box['grid']} rails={box['rails']} section={box['sectionH']}px "
                  f"doc={box['docH']}px items={box['items']} rows={box['rows']}")
            print(f"   -> {path}")
            p.close()
    b.close()
print("done")
