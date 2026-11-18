#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Drive the calculator for real against the six verified worked examples.

The examples are frozen (skill `fred-hollows-tax-calculator` §4, YA2026/27,
single person). This script types the gift, opens the optional exact-income row,
types the assessable income, and reads the rendered saving / net back out of the
DOM — it does not re-implement the maths, so it tests what a donor actually sees.

It drives the EXACT-INCOME path on purpose. The band picker intentionally shows
a range (the saving is computed at both ends of the selected band), so a band
cannot express a single verified figure; the exact path can, and there the
number must be exact — including the 35% cap and the band crossings that the
old flat-multiplier engine got wrong by up to 46%.

It runs per language. The figures are figures, not copy: both builds must render
the same six numbers, and the only thing `?lang=` may change is the words around
them (including the range separator: 「至」 vs "to").

Exits non-zero unless 6/6 are exact.

Usage:
    python3 qa/verify_six_examples.py                     # zh-HK
    python3 qa/verify_six_examples.py --lang en
    python3 qa/verify_six_examples.py http://127.0.0.1:8765 --lang en
"""
import sys
from playwright.sync_api import sync_playwright

ARGS = sys.argv[1:]
BASE = "http://127.0.0.1:8765"
LANG = "zh-HK"
pos = []
for i, a in enumerate(ARGS):
    if a == "--lang" and i + 1 < len(ARGS):
        LANG = ARGS[i + 1]
    elif not a.startswith("--") and (i == 0 or ARGS[i - 1] != "--lang"):
        pos.append(a)
if pos:
    BASE = pos[0]

# how a range is written in each language — the separator is copy, the numbers
# either side of it are not
SEP = {"zh-HK": "至", "en": " to "}[LANG]

# (gift, assessable income, verified saved, verified net paid, note)
CASES = [
    (500, 400000, 85, 415, "inside the 17% slice"),
    (1800, 600000, 306, 1494, "inside the 17% slice"),
    (250000, 500000, 29150, 220850, "CAP BINDS: 35% of 500k = 175k deductible"),
    (500, 140000, 0, 500, "below the allowance, saves nothing"),
    (10000, 2500000, 1500, 8500, "standard-rate zone 15%"),
    (175000, 500000, 29150, 145850, "at the 35% ceiling; gift crosses bands"),
]

READ = """() => ({
  gift:  document.getElementById('gift-out').textContent.trim(),
  saved: document.getElementById('saved').textContent.trim(),
  net:   document.getElementById('net').textContent.trim(),
  rate:  document.getElementById('rate').textContent.trim(),
  rlabel: document.getElementById('rate-label').textContent.trim(),
  label: document.getElementById('saved-label').textContent.trim(),
  caption: document.getElementById('net-caption').textContent.trim(),
  cap:   document.getElementById('cap').textContent.trim(),
  benefit: document.getElementById('benefit').textContent.trim(),
  exactOpen: document.getElementById('exact-row').open,
  giftLabel: document.getElementById('gift-label').textContent.trim(),
})"""


def num(s):
    """Pull the integer out of '−HK$42,500' / 'HK$1,079'."""
    d = "".join(ch for ch in s if ch.isdigit())
    return int(d) if d else None


ok = bad = 0
print(f"?lang={LANG}  base={BASE}\n")
print(f"{'gift':>9} {'income':>9} {'rendered saved':>15} {'verified':>9} "
      f"{'rendered net':>14} {'verified':>9}  verdict  note")
with sync_playwright() as pw:
    b = pw.chromium.launch(channel="chrome", headless=True)
    p = b.new_page(viewport={"width": 390, "height": 900}, is_mobile=True, has_touch=True)
    for gift, income, v_saved, v_net, note in CASES:
        p.goto(f"{BASE}/embed/?part=calc&lang={LANG}", wait_until="load")
        p.wait_for_timeout(350)
        p.fill("#gift", str(gift))
        p.wait_for_timeout(120)
        # the row is collapsed by default; a donor (and this test) has to open it
        p.evaluate("() => { document.getElementById('exact-row').open = true; }")
        p.fill("#exact", str(income))
        p.wait_for_timeout(250)
        g = p.evaluate(READ)
        saved, net = num(g["saved"]), num(g["net"])
        single = SEP not in g["saved"]
        exact = (saved == v_saved and net == v_net and single and g["exactOpen"])
        if exact:
            ok += 1
            verdict = "EXACT"
        else:
            bad += 1
            verdict = "MISMATCH"
        print(f"{gift:>9,} {income:>9,} {g['saved']:>15} {v_saved:>9,} {g['net']:>14} "
              f"{v_net:>9,}  {verdict:<8} {note}")
        print(f"{'':20} rate {g['rate']:>6} · {g['rlabel']} · label {g['label']}")
        print(f"{'':20} caption: {g['caption']}")
        print(f"{'':20} cap: {g['cap']}")
        print(f"{'':20} benefit: {g['benefit']}")
    b.close()

print(f"\n=== ?lang={LANG}: {ok}/{len(CASES)} exact, {bad} mismatched ===")
sys.exit(1 if bad else 0)
