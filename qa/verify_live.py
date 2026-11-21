#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verify the DEPLOYED widget, not the local file.

A push is not a deploy and a 200 is not the build you shipped: GitHub Pages caches
HTML for ~10 minutes, and a catch-all can return 200 with the wrong body. So this
fetches the live document and asserts the markers this pass introduced, then
renders the live URL in a browser and reads the numbers out of the live DOM.

  python3 qa/verify_live.py
  python3 qa/verify_live.py --base https://2skdigitals.github.io/fhf-taxcalc-poc
"""
import re
import sys
import urllib.request

from playwright.sync_api import sync_playwright

BASE = "https://2skdigitals.github.io/fhf-taxcalc-poc"
ARGS = sys.argv[1:]
for i, a in enumerate(ARGS):
    if a == "--base" and i + 1 < len(ARGS):
        BASE = ARGS[i + 1].rstrip("/")

ok = bad = 0


def check(label, errs, detail=""):
    global ok, bad
    if errs:
        bad += 1
        print(f"FAIL  {label}")
        for e in errs:
            print("        ", e)
    else:
        ok += 1
        print(f"PASS  {label}" + (f"   {detail}" if detail else ""))


def fetch(path):
    url = f"{BASE}{path}"
    req = urllib.request.Request(url, headers={"Cache-Control": "no-cache",
                                               "User-Agent": "fhf-verify/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.status, r.read().decode("utf-8"), url


# ── 1 · the shipped document ─────────────────────────────────────────────────
status, body, url = fetch("/embed/?part=all&lang=en")
print(f"GET {url} → HTTP {status}, {len(body)} bytes\n")
check("the live combined URL answers 200", [] if status == 200 else [f"status {status}"])

MUST = {
    "white ground token": "--ground:#fff;",
    "56rem column": ".wrap{max-width:56rem",
    "the two-rail desktop grid": "grid-template-columns:repeat(2,minmax(0,1fr))",
    "the AlipayHK QR tile": "../assets/logos/alipayhk.png",
    "the credit-card tile": 'data-rail="card"',
    "the payment lede names both rails that are left":
        "Scan the AlipayHK code with your phone, or pay by credit card on the Foundation's donation page.",
    "the HK$100 floor line": "Donation amount at HK$100 or above will receive tax deduction receipt",
    "the floor note element": 'id="min-note"',
    "the floor hint on the field": 'id="gift-min"',
    "?part=all in the part map": 'all:     ["calculator","result","payment","receipt"]',
    "all sections shown": 'body[data-part="all"] #calculator',
    "positive saving (no minus in markup)": '<dd id="saved">HK$221</dd>',
    "the client's disclaimer line 1": "Based on IRD tax rates and info for the relevant assessment year; "
                                      "for general reference only.",
    "the client's disclaimer line 5": "The Fred Hollows Foundation (HK) Limited assumes no liability for "
                                      "use or reliance.",
    "the client's Chinese disclaimer": "護瞳行動（香港）有限公司概不承擔相關法律責任。",
}
missing = [k for k, v in MUST.items() if v not in body]
check(f"{len(MUST)} markers of this pass are in the live document", missing)

MUST_NOT = {
    # 21 Nov: PayMe was dropped. Every trace of it must stay gone from the served bytes.
    "the dropped rail's name": "PayMe",
    "its QR asset": "payme.png",
    "its mobile sub-label key": "s3.payme.sub",
    "its CSS rule": "r-payme",
    "its rail value": 'data-rail="payme"',
    "its alt-text key": "s3.qr.alt.payme",
    "months select": 'id="months"',
    "months field": 'id="months-field"',
    "clampMonths": "clampMonths",
    "old ground colour": "--ground:#F3F3F0",
    "44rem column": "max-width:44rem",
    "minus-sign render": '"−" + money',
    "our draft disclaimer": "不能取代專業意見",
    "the monthly reminder link": 'data-i18n="s3.monthly"',
    "the scope reminder": 'data-i18n="s2.scope"',
}
present = [k for k, v in MUST_NOT.items() if v in body]
check(f"{len(MUST_NOT)} removed things are absent from the live document", present)

# ── 2 · the live DOM ─────────────────────────────────────────────────────────
with sync_playwright() as pw:
    b = pw.chromium.launch(channel="chrome", headless=True)
    for w in (390, 1440):
        p = b.new_page(viewport={"width": w, "height": 900},
                       is_mobile=(w < 600), has_touch=(w < 600))
        p.goto(f"{BASE}/embed/?part=all&lang=en&cb={w}", wait_until="load")
        p.wait_for_timeout(900)
        d = p.evaluate("""()=>({
            bg: getComputedStyle(document.documentElement).backgroundColor,
            wrap: Math.round(document.querySelector('.wrap').getBoundingClientRect().width),
            sections: [...document.querySelectorAll('section')]
                        .filter(s=>getComputedStyle(s).display!=='none').map(s=>s.id),
            saved: document.getElementById('saved').textContent,
            h: document.documentElement.scrollHeight,
            monthly: !!document.getElementById('months'),
            overflow: document.documentElement.scrollWidth > document.documentElement.clientWidth + 1
        })""")
        print(f"\nbrowser @ {w}px: {d}")
        errs = []
        if d["bg"] != "rgb(255, 255, 255)":
            errs.append(f"ground {d['bg']}")
        if d["wrap"] != (min(896, w)):
            errs.append(f"column {d['wrap']}px")
        if d["sections"] != ["calculator", "result", "payment", "receipt"]:
            errs.append(f"sections {d['sections']}")
        if "−" in d["saved"] or "HK$" not in d["saved"]:
            errs.append(f"saved {d['saved']!r}")
        if d["monthly"]:
            errs.append("a months control is still in the DOM")
        if d["overflow"]:
            errs.append("horizontal overflow")
        check(f"the live combined document renders correctly at {w}px", errs,
              f"{d['h']}px tall")
        p.close()
    b.close()

print(f"\n=== live verification: {ok} passed, {bad} failed ===\n{BASE}/embed/?part=all&lang=en")
sys.exit(1 if bad else 0)
