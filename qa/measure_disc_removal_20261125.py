#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""25 Nov 2026 — A/B the height of every block before and after the disclaimer left.

The block used to close every part, so its removal shortens every document. This
prints old → new at the five widths the client quotes, per part per language, and
writes the pairs to /tmp/fhf-disc-removal.json for the reissue.

States are the ones that can be tallest, exactly as qa/sweep_heights.py takes
them: default, monthly, and monthly + the exact-income swap.

    /Library/Developer/CommandLineTools/usr/bin/python3 qa/measure_disc_removal_20261125.py
"""
import json
import subprocess
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
BASE = "http://127.0.0.1:8765"
# The pre-change build is regenerated from the commit that enabled the in-frame GTM
# container — the last build that still carried the disclaimer. Served as .html so
# Chrome treats it as a document rather than text.
BEFORE_REV = "a9bdd2a"
FIXTURE = ROOT / "qa" / "_pre_remove_20261125.html"
if not FIXTURE.exists():
    FIXTURE.write_bytes(subprocess.run(["git", "-C", str(ROOT), "show",
                                       f"{BEFORE_REV}:embed/index.html"],
                                      capture_output=True, check=True).stdout)
BEFORE = f"{BASE}/qa/_pre_remove_20261125.html"
AFTER = f"{BASE}/embed/"
PARTS = ("calc", "pay", "receipt", "all")
WIDTHS = (320, 390, 768, 1024, 1440)


def h(page, url, part, floor, q=""):
    page.goto(f"{url}?part={part}{q}", wait_until="load")
    page.wait_for_timeout(350)
    once = page.evaluate("()=>document.documentElement.scrollHeight")
    monthly = exact = once
    if part in ("calc", "all"):
        try:
            page.click('input[name="mode"][value="monthly"]', timeout=1500)
            page.wait_for_timeout(280)
            monthly = page.evaluate("()=>document.documentElement.scrollHeight")
            page.click("#exact-toggle", timeout=1500)
            page.fill("#exact", "800000", timeout=1500)
            page.wait_for_timeout(280)
            exact = page.evaluate("()=>document.documentElement.scrollHeight")
        except Exception:
            monthly = exact = once
    return max(once, monthly, exact, floor)


def main():
    out = {}
    with sync_playwright() as pw:
        b = pw.chromium.launch(channel="chrome", headless=True)
        for lang, q in (("zh-HK", ""), ("en", "&lang=en")):
            out[lang] = {}
            for part in PARTS:
                out[lang][part] = {}
                for w in WIDTHS:
                    # the empty phase-1 receipt frame can only report its viewport
                    floor = 60 if part == "receipt" else 0
                    p = b.new_page(viewport={"width": w, "height": 240},
                                   is_mobile=(w < 600), has_touch=(w < 600))
                    old = h(p, BEFORE, part, floor, q)
                    p.close()
                    p = b.new_page(viewport={"width": w, "height": 240},
                                   is_mobile=(w < 600), has_touch=(w < 600))
                    new = h(p, AFTER, part, floor, q)
                    p.close()
                    out[lang][part][w] = {"old": old, "new": new, "delta": new - old}
                    print(f"{lang:6} ?part={part:8} {w:>5}px  {old:>5} -> {new:>5}  ({new-old:+d})")
        b.close()
    with open("/tmp/fhf-disc-removal.json", "w") as f:
        json.dump(out, f, indent=2)
    print("\nwrote /tmp/fhf-disc-removal.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
