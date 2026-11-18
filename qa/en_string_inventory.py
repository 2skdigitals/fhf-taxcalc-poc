#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Emit the EN string inventory straight out of the shipped file.

The doc's change list must not be able to disagree with `embed/index.html`, so
the table is generated from the I18N block rather than transcribed. Keys are
listed in table order; `--md` prints a markdown table, plain output prints a
padded list.

Usage: python3 qa/en_string_inventory.py [--md]
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HTML = ROOT / "embed" / "index.html"
MD = "--md" in sys.argv

src = HTML.read_text(encoding="utf-8")
m = re.search(r"  var I18N = \{(.*?)\n  \};\n", src, re.S)
if not m:
    sys.exit("FAIL  no I18N block found")
block = m.group(1)

# split into the two language objects
langs = {}
for name in ("zh-HK", "en"):
    start = block.index(f'"{name}": {{')
    depth = 0
    i = start
    while True:
        ch = block[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                break
        i += 1
    langs[name] = block[start:i + 1]

TABLES = {}
for name, body in langs.items():
    tab = {}
    for line in body.splitlines():
        mm = re.match(r'\s*"([^"]+)":\s*"(.*)",?\s*$', line)
        if mm:
            tab[mm.group(1)] = json.loads('"' + mm.group(2) + '"')
    TABLES[name] = tab

zh, en = TABLES["zh-HK"], TABLES["en"]
missing = [k for k in zh if k not in en] + [k for k in en if k not in zh]
if missing:
    sys.exit("FAIL  key mismatch: " + str(missing))
print(f"# {len(zh)} keys, both languages, no gaps\n", file=sys.stderr if MD else sys.stdout)

GROUP = []
for k in zh:
    g = k.split(".")[0]
    if not GROUP or GROUP[-1][0] != g:
        GROUP.append((g, []))
    GROUP[-1][1].append(k)

if MD:
    print("| key | zh-HK | en |")
    print("|---|---|---|")
    for g, keys in GROUP:
        for k in keys:
            z = zh[k].replace("|", "\\|").replace("\n", "⏎")
            e = en[k].replace("|", "\\|").replace("\n", "⏎")
            print(f"| `{k}` | {z} | {e} |")
else:
    for g, keys in GROUP:
        print(f"\n== {g} ==")
        for k in keys:
            print(f"  {k}\n    zh: {zh[k]!r}\n    en: {en[k]!r}")
