#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sweep widths to find the real maximum content height of every block.

A responsive change measured only at one width is how a block ships with an
inner scrollbar: the peak is usually at the narrow end, or in the band where a
control switches type (here: the income picker becomes a native <select> below
721px and a two-column radio list from 721px).

Two languages, two height contracts. English is not automatically shorter than
Chinese: at phone widths it costs more lines (more words per sentence), while at
desktop widths it costs fewer. The peak of each block is therefore measured per
language and declared separately — see docs/INTERFACE.md §2.

Usage:
    python3 qa/sweep_heights.py                  # both languages
    python3 qa/sweep_heights.py --lang en
    python3 qa/sweep_heights.py --base http://127.0.0.1:8765
"""
import json
import sys
try:
    from playwright.sync_api import sync_playwright
except ModuleNotFoundError:                      # the system 3.9 has no playwright
    raise SystemExit(
        "playwright is not in this interpreter.\n"
        "Run: /Library/Developer/CommandLineTools/usr/bin/python3 qa/sweep_heights.py"
    )

ARGS = sys.argv[1:]
BASE = "http://127.0.0.1:8765"
LANGS = ["zh-HK", "en"]
for i, a in enumerate(ARGS):
    if a == "--base" and i + 1 < len(ARGS):
        BASE = ARGS[i + 1]
    if a == "--lang" and i + 1 < len(ARGS):
        LANGS = [ARGS[i + 1]]

PARTS = ["calc", "input", "result", "pay", "receipt", "all"]
WIDTHS = [320, 328, 360, 390, 414, 430, 480, 540, 568, 600, 640, 700, 721, 768,
          820, 900, 944, 1024, 1100, 1200, 1280, 1440]
# the five widths the client asked to be quoted at (docs/INTERFACE.md §2)
REPORT_WIDTHS = (320, 390, 768, 1024, 1440)

# peak + 45..70px of slack, measured not assumed (see the peaks printed below).
# English peaks are HIGHER than Chinese at every width: 35% more lines at 320px,
# where the column is ~288px wide and a sentence costs two lines instead of one.
# Reissued 23 Nov 2026 (client call, qa/apply_client_call_20261123.py): body copy
# 17 -> 18px at 1.56, the block heading 28 -> 32, and the column 896 -> 1280px.
# The wider column shortened most lines and the larger type lengthened them; every
# block's peak moved, so every number here is reissued. Peaks: calc 1546/1703,
# input 894/952, result 737/869, pay 490/518, receipt 752/860, all 2599/2935.
DECLARED = {
    "zh-HK": {"calc": 1610, "input": 950, "result": 800, "pay": 545, "receipt": 820, "all": 2665},
    "en":    {"calc": 1770, "input": 1020, "result": 935, "pay": 585, "receipt": 925, "all": 3000},
}

peaks = {}
with sync_playwright() as pw:
    b = pw.chromium.launch(channel="chrome", headless=True)
    for lang in LANGS:
        peaks[lang] = {}
        print(f"\n=== ?lang={lang} (default + monthly state) ===")
        for part in PARTS:
            rows = []
            for w in WIDTHS:
                # short viewport: .wrap has min-height:100vh, which would mask
                # any content shorter than the viewport and hide the real number
                p = b.new_page(viewport={"width": w, "height": 240},
                               is_mobile=(w < 600), has_touch=(w < 600))
                p.goto(f"{BASE}/embed/?part={part}&lang={lang}", wait_until="load")
                p.wait_for_timeout(400)
                once = p.evaluate("()=>document.documentElement.scrollHeight")
                # The monthly layout is a SECOND shape, not a variation: it adds the
                # months control, a longer caption and an extra ledger row. Measured
                # default-only, this is how a block ships that scrolls the moment a
                # donor picks monthly (found 19 Nov: the live calc clipped by 70px at
                # 320px in exactly this state).
                monthly = once
                exact = once
                if part in ("calc", "input", "all"):
                    try:
                        p.click('input[name="mode"][value="monthly"]', timeout=1500)
                        p.wait_for_timeout(320)
                        monthly = p.evaluate("()=>document.documentElement.scrollHeight")
                        # third shape: monthly AND the exact-income disclosure open — the
                        # tallest reachable state, and the one that was still clipping the
                        # 1950px declaration by 179px at 320px (found 19 Nov)
                        # exact income is now a swap inside the income card, not a
                        # disclosure — the third shape is monthly + exact together
                        p.click("#exact-toggle", timeout=1500)
                        p.fill("#exact", "800000", timeout=1500)
                        p.wait_for_timeout(320)
                        exact = p.evaluate("()=>document.documentElement.scrollHeight")
                    except Exception:
                        monthly, exact = once, once
                rows.append((w, max(once, monthly, exact)))
                p.close()
            top = max(rows, key=lambda r: r[1])
            declared = DECLARED[lang][part]
            peaks[lang][part] = {"max": top[1], "at": top[0], "declared": declared,
                                 "slack": declared - top[1], "curve": rows}
            print(f"?part={part:8} peak {top[1]:>5}px at {top[0]:>4}px | "
                  f"declared {declared:>5} | slack {declared-top[1]:>4} "
                  f"{'OK' if declared >= top[1] else 'OVERFLOW'}")
            lo = min(r[1] for r in rows)
            print(f"{'':16} range {lo}–{top[1]} across {len(WIDTHS)} widths")
            at = {w: h for w, h in rows if w in REPORT_WIDTHS}
            print(f"{'':16} quoted: " + " · ".join(f"{w}px {at[w]}" for w in REPORT_WIDTHS
                                                  if w in at)
                  + "   (client's five widths)")
    b.close()

if len(LANGS) == 2:
    print(f"\n{'block':10} {'zh-HK peak':>12} {'en peak':>9}  width  | "
          f"{'zh declared':>12} {'en declared':>12}")
    for part in PARTS:
        z, e = peaks["zh-HK"][part], peaks["en"][part]
        print(f"?part={part:<4} {z['max']:>8} @{z['at']:<4} {e['max']:>5} @{e['at']:<4}      | "
              f"{z['declared']:>12} {e['declared']:>12}")
    al, ae = peaks["zh-HK"]["all"]["max"], peaks["en"]["all"]["max"]
    print(f"\n?part=all — the one-link arrangement (calculator -> result -> payment -> receipt): "
          f"{al}px zh-HK · {ae}px en. "
          f"{'Inside' if max(al, ae) <= 4000 else 'EXCEEDS'} a sane 4,000px iframe.")

with open("/tmp/fhf-sweep.json", "w") as f:
    json.dump(peaks, f, indent=2)
print("\nwrote /tmp/fhf-sweep.json")

over = [p for l in peaks for p in peaks[l] if peaks[l][p]["max"] > peaks[l][p]["declared"]]
if over:
    print(f"OVERFLOW in {len(over)} block(s): " + ", ".join(f"{l}/{p}" for l in peaks for p in peaks[l]
                                                           if peaks[l][p]["max"] > peaks[l][p]["declared"]))
    sys.exit(1)
