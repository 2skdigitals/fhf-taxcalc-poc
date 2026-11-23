#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Screenshots for the 23 Nov client-call pass: default state + result block."""
import pathlib
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8765"
OUT = pathlib.Path(__file__).resolve().parent.parent / "shots" / "clientcall-20261123"
OUT.mkdir(parents=True, exist_ok=True)

with sync_playwright() as pw:
    b = pw.chromium.launch(channel="chrome")
    for lang, qs in (("zh", ""), ("en", "&lang=en")):
        for w, h in ((390, 900), (1440, 1100)):
            p = b.new_page(viewport={"width": w, "height": h}, is_mobile=(w < 600), has_touch=(w < 600))
            # calculator with the new default (top of the document)
            p.goto(f"{BASE}/embed/?part=input{qs}", wait_until="load")
            p.wait_for_timeout(600)
            p.screenshot(path=str(OUT / f"input-{lang}-{w}.png"), full_page=True)
            # the result block on its own
            p.goto(f"{BASE}/embed/?part=result{qs}", wait_until="load")
            p.wait_for_timeout(600)
            p.screenshot(path=str(OUT / f"result-{lang}-{w}.png"), full_page=True)
            # the one-link document at the top, in its declared frame
            p.goto(f"{BASE}/embed/?part=all{qs}", wait_until="load")
            p.wait_for_timeout(600)
            p.screenshot(path=str(OUT / f"all-top-{lang}-{w}.png"))
            p.close()
    b.close()
print("shots in", OUT)
for f in sorted(OUT.glob("*.png")):
    print(" ", f.name, f.stat().st_size // 1024, "KB")
