#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Drive the calculator for real against the six verified worked examples.

The examples are frozen (skill `fred-hollows-tax-calculator` §4, YA2026/27,
single person). This script types the gift, swaps in the exact-income field,
types the assessable income, and reads the rendered saving and the rendered net
support back out of the DOM — it does not re-implement the maths, so it tests
what a donor actually sees.

READING NET AFTER 23 NOV: the hero figure is the DONATION (the client's own
label, 您的全額捐款 / Your donation) and the ledger row that repeated the gift was
removed, so the net cost is no longer a field of its own — it is the 實際支持 /
"net support" figure inside the benefit sentence. That is a stronger place to
check it from, not a weaker one: the sentence's figures have to compute from the
gift, and this asserts them against the frozen examples.

It drives the EXACT-INCOME path on purpose. The band picker intentionally shows
a range (the saving is computed at both ends of the selected band), so a band
cannot express a single verified figure; the exact path can, and there the
number must be exact — including the 35% cap and the band crossings that the
old flat-multiplier engine got wrong by up to 46%.

It runs per language. The figures are figures, not copy: both builds must render
the same six numbers, and the only thing `?lang=` may change is the words around
them. The one exception is checked explicitly: the client's own HK$1,300 sample
sentence must render CHARACTER FOR CHARACTER in each language.

Exits non-zero unless 6/6 are exact and the sample sentence matches.

Usage:
    python3 qa/verify_six_examples.py                     # zh-HK
    python3 qa/verify_six_examples.py --lang en
    python3 qa/verify_six_examples.py http://127.0.0.1:8765 --lang en
"""
import re
import sys
from playwright.sync_api import sync_playwright

ARGS = sys.argv[1:]
BASE = "http://127.0.0.1:8765"
LANG = "zh-HK"
pos = []
for i, a in enumerate(ARGS):
    if a == "--lang" and i + 1 < len(ARGS):
        LANG = ARGS[i + 1]
    # `--lang=en` was silently ignored: it fell through to nothing, the run stayed
    # in Chinese, and the summary still printed a green "6/6" — an English check
    # that never loaded English. Accept both spellings.
    elif a.startswith("--lang="):
        LANG = a.split("=", 1)[1]
    elif not a.startswith("--") and (i == 0 or ARGS[i - 1] != "--lang"):
        pos.append(a)
if pos:
    BASE = pos[0]

# how a range is written in each language — the separator is copy, the numbers
# either side of it are not
SEP = {"zh-HK": "至", "en": " to "}[LANG]

# the client's sample sentence, for a HK$1,300 gift in the default band
SAMPLE = {
    "zh-HK": "您的 HK$1,300 捐款可全數扣稅，享約 HK$182 – 221 稅務扣減；"
             "只需約 HK$1,079 – 1,118 實際支持，即可成就全額100%救盲力量。",
    "en": "Your HK$1,300 gift qualifies for full tax deduction (est. HK$182 – 221 relief), "
          "meaning just HK$1,079 – 1,118 net support delivers the full sight-saving impact.",
}

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
  gift:  document.getElementById('net').textContent.trim(),
  saved: document.getElementById('saved').textContent.trim(),
  rate:  document.getElementById('rate').textContent.trim(),
  rlabel: document.getElementById('rate-label').textContent.trim(),
  label: document.getElementById('saved-label').textContent.trim(),
  caption: document.getElementById('net-caption').textContent.trim(),
  cap:   document.getElementById('cap').textContent.trim(),
  benefit: document.getElementById('benefit').textContent.trim(),
  exactOpen: !document.getElementById('exact-wrap').hidden,
})"""


def num(s):
    """Pull the integer out of 'HK$42,500' / 'HK$1,079'."""
    d = "".join(ch for ch in s if ch.isdigit())
    return int(d) if d else None


def hk_values(s):
    """Every figure written as a currency amount, in reading order.

    Deliberately HK$-anchored: '35%' and '100%' are rates, not money, and a
    bare digits-only sweep picks them up and shifts every value one place.
    """
    return [int(x.replace(",", "")) for x in re.findall(r"HK\$([\d,]+)", s)]


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
        # exact income is a swap inside the income card: open it, then type
        p.click("#exact-toggle")
        p.fill("#exact", str(income))
        p.wait_for_timeout(250)
        g = p.evaluate(READ)
        saved, hero = num(g["saved"]), num(g["gift"])
        vals = hk_values(g["benefit"])
        # The sentence names the gift, the relief and the net support, in order.
        # Below the allowance there is no relief to state, so that branch says so in
        # words instead of quoting a HK$0 relief — there the sentence carries the
        # gift alone, and net = gift follows by arithmetic.
        if len(vals) == 3:
            sent_gift, sent_saved, sent_net = vals
        elif len(vals) == 1 and v_saved == 0:
            sent_gift, sent_saved, sent_net = vals[0], 0, gift
        else:
            sent_gift = sent_saved = sent_net = None
        single = SEP not in g["saved"]
        exact = (saved == v_saved and hero == gift and single and g["exactOpen"]
                 and sent_gift == gift and sent_saved == v_saved and sent_net == v_net)
        if exact:
            ok += 1
            verdict = "EXACT"
        else:
            bad += 1
            verdict = "MISMATCH"
        shown_net = ("HK$" + format(sent_net, ",")) if sent_net is not None else "-"
        print(f"{gift:>9,} {income:>9,} {g['saved']:>15} {v_saved:>9,} {shown_net:>14} "
              f"{v_net:>9,}  {verdict:<8} {note}")
        print(f"{'':20} hero {g['gift']:>10} · rate {g['rate']:>6} · {g['rlabel']} · label {g['label']}")
        print(f"{'':20} caption: {g['caption']}")
        print(f"{'':20} cap: {g['cap']}")
        print(f"{'':20} benefit: {g['benefit']}")

    # ── the client's own sample sentence, verbatim ───────────────────────────
    # This is the acceptance string from the copy sheet. It is not a range the
    # test computes: it is the sentence the client wrote, and it has to render
    # exactly — the same figures, the same spacing, the same punctuation.
    # 23 Nov: the calculator now opens on HK$100, so the sample is reached the
    # way a donor reaches it — by typing 1,300 — rather than by being the default.
    p.goto(f"{BASE}/embed/?part=calc&lang={LANG}", wait_until="load")
    p.wait_for_timeout(450)
    p.fill("#gift", "1300")
    p.wait_for_timeout(350)
    sample = p.evaluate("()=>document.getElementById('benefit').textContent")
    if sample == SAMPLE[LANG]:
        print(f"\nPASS  the HK$1,300 sample sentence matches the copy sheet character for character")
    else:
        bad += 1
        i = next((i for i in range(min(len(sample), len(SAMPLE[LANG])))
                  if sample[i] != SAMPLE[LANG][i]), min(len(sample), len(SAMPLE[LANG])))
        print(f"\nFAIL  the HK$1,300 sample sentence drifted at {i}:")
        print(f"      got  …{sample[max(0,i-30):i+40]!r}")
        print(f"      want …{SAMPLE[LANG][max(0,i-30):i+40]!r}")
    b.close()

print(f"\n=== ?lang={LANG}: {ok}/{len(CASES)} exact, {bad} mismatched ===")
sys.exit(1 if bad else 0)
