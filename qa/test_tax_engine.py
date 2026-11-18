#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Headless test of the widget's tax engine — no browser.

The engine lives in `embed/index.html` between two markers and is assigned to
`var __fhfTax`. This script extracts exactly that block, runs it in node, and
compares the result against the six worked examples verified for YA2026/27
(skill `fred-hollows-tax-calculator` §4).

Why it exists: the widget used to multiply the gift by a flat marginal rate.
That is correct while the gift stays inside one tax slice and under the 35%
ceiling, and wrong the moment it does not — HK$250,000 at HK$500,000 income
rendered -HK$42,500 against a true -HK$29,150 (+46%). Two of the six examples
were wrong and nothing failed, because only small gifts were ever compared.

Language: since the EN build this file has two string tables. The engine must
stay single-source, so this script asserts that the extracted block contains no
locale string, no I18N key and no `t()` call, and that the file holds exactly
one engine block. `--lang` only labels the run — the same bytes are executed for
both languages, which is the point: `?lang=en` cannot reach the arithmetic.
The per-language *rendered* figures are proven by qa/verify_six_examples.py.

Exit non-zero on any mismatch.

Usage:
    python3 qa/test_tax_engine.py            # zh-HK label (default)
    python3 qa/test_tax_engine.py --lang en
    python3 qa/test_tax_engine.py other.html
"""
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARGS = sys.argv[1:]
LANG = "zh-HK"
HTML = None
i = 0
while i < len(ARGS):
    a = ARGS[i]
    if a == "--lang" and i + 1 < len(ARGS):
        LANG = ARGS[i + 1]
        i += 2
        continue
    if not a.startswith("--"):
        HTML = Path(a)
    i += 1
HTML = HTML or ROOT / "embed" / "index.html"

# (gift, assessable income, verified saving, verified net paid, note)
CASES = [
    (500, 400000, 85, 415, "inside the 17% slice, under the cap"),
    (1800, 600000, 306, 1494, "inside the 17% slice, under the cap"),
    (250000, 500000, 29150, 220850, "CAP BINDS: 35% x 500,000 = 175,000 deductible"),
    (500, 140000, 0, 500, "below the allowance: no tax, no saving"),
    (10000, 2500000, 1500, 8500, "standard-rate zone, 15%"),
    (175000, 500000, 29150, 145850, "exactly at the ceiling; gift crosses bands"),
]

src = HTML.read_text(encoding="utf-8")
blocks = re.findall(r"/\* FHF_TAX_ENGINE_START \*/(.*?)/\* FHF_TAX_ENGINE_END \*/", src, re.S)
if not blocks:
    print(f"FAIL  no FHF_TAX_ENGINE_START/END block found in {HTML}")
    sys.exit(1)
if len(blocks) > 1:
    print(f"FAIL  {len(blocks)} engine blocks in {HTML} — the maths must exist once")
    sys.exit(1)
engine = blocks[0]
if "__fhfTax" not in engine:
    print("FAIL  the engine block does not define __fhfTax")
    sys.exit(1)

driver = engine + """
const OUT = [];
for (const [gift, inc] of CASES) {
  OUT.push({
    gift: gift, income: inc,
    saving: __fhfTax.saving(gift, inc),
    rounded: Math.round(__fhfTax.saving(gift, inc)),
    deductible: __fhfTax.deductible(gift, inc),
    tax: __fhfTax.taxOn(inc),
    marginal: __fhfTax.marginal(inc)
  });
}
console.log(JSON.stringify({
  cases: OUT,
  crossover: __fhfTax.taxOn(2132500),
  stdAt5m: __fhfTax.taxOn(5000000),
  noTax: __fhfTax.taxOn(145000)
}));
"""

with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as fh:
    fh.write("const CASES = " + json.dumps([[c[0], c[1]] for c in CASES]) + ";\n" + driver)
    js_path = fh.name

try:
    proc = subprocess.run(["node", js_path], capture_output=True, text=True, timeout=60)
except FileNotFoundError:
    print("FAIL  node is not installed; cannot run the engine headlessly")
    sys.exit(1)
finally:
    Path(js_path).unlink(missing_ok=True)

if proc.returncode != 0:
    print("FAIL  the engine threw in node")
    print(proc.stderr.strip()[:2000])
    sys.exit(1)

data = json.loads(proc.stdout)
bad = 0
print(f"engine: {HTML.relative_to(ROOT)}  (block {len(engine)} chars, run in node, no browser)")
print(f"language label: {LANG}  —  the block above is the only engine in the file, so both")
print(f"                  languages execute these same bytes\n")
print(f"{'gift':>9} {'income':>10} {'saved':>9} {'want':>9} {'net paid':>10} {'want':>9}  verdict  note")
for row, (gift, inc, want_saved, want_net, note) in zip(data["cases"], CASES):
    got_saved, got_net = row["rounded"], gift - row["rounded"]
    ok = got_saved == want_saved and got_net == want_net
    bad += 0 if ok else 1
    print(f"{gift:>9,} {inc:>10,} {got_saved:>9,} {want_saved:>9,} {got_net:>10,} {want_net:>9,}"
          f"  {'EXACT' if ok else 'WRONG'}  {note}")

# invariants that a flat marginal multiplier cannot satisfy
guards = []
guards.append(("cap is 35% of income",
               data["cases"][2]["deductible"] == 175000 and data["cases"][5]["deductible"] == 175000,
               f"deductible 250,000@500,000 = {data['cases'][2]['deductible']:,.0f}, "
               f"175,000@500,000 = {data['cases'][5]['deductible']:,.0f}"))
guards.append(("progressive = standard at the single-person crossover (319,875)",
               abs(data["crossover"] - 319875) < 0.01,
               f"taxOn(2,132,500) = {data['crossover']:,.2f}"))
guards.append(("standard rate is two-tier above 5M (750,000 + 16%)",
               abs(data["stdAt5m"] - 750000) < 0.01,
               f"taxOn(5,000,000) = {data['stdAt5m']:,.2f} (progressive is higher there)"))
guards.append(("income at the allowance pays nothing", data["noTax"] == 0,
               f"taxOn(145,000) = {data['noTax']}"))
guards.append(("no saving ever exceeds 17% of the gift",
               all(r["rounded"] <= r["gift"] * 0.17 + 1 for r in data["cases"]),
               "max rounded saving / gift = "
               + f"{max(r['rounded'] / r['gift'] for r in data['cases']) * 100:.2f}%"))

# the language layer must not be able to reach the maths. Comments are stripped
# first: a comment may explain the Chinese terms, a STRING may not carry them.
engine_code = re.sub(r"/\*.*?\*/", "", engine, flags=re.S)
engine_code = re.sub(r"(?m)//[^\n]*", "", engine_code)
cjk = re.findall(r"[\u3400-\u9fff\uff00-\uffef]", engine_code)
strings = re.findall(r"\"(?:[^\"\\]|\\.)*\"|'(?:[^'\\]|\\.)*'", engine_code)
guards.append(("the engine block carries no locale string (no CJK, no I18N, no t())",
               not cjk and "I18N" not in engine_code and not re.search(r"\bt\(", engine_code)
               and not any(re.search(r"[\u3400-\u9fff]", s) for s in strings),
               f"cjk={len(cjk)} chars, I18N refs={engine_code.count('I18N')}, "
               f"t() calls={len(re.findall(r'(?<![A-Za-z_.])t[(]', engine_code))}, "
               f"strings checked={len(strings)}"))

print()
for label, ok, detail in guards:
    bad += 0 if ok else 1
    print(f"{'PASS' if ok else 'FAIL'}  {label} — {detail}")

exact = len(CASES) - sum(1 for row, c in zip(data["cases"], CASES)
                         if not (row["rounded"] == c[2] and c[0] - row["rounded"] == c[3]))
print(f"\n=== [{LANG}] {exact}/{len(CASES)} verified examples exact, {bad} failure(s) ===")
sys.exit(1 if bad else 0)
