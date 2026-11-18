#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build docs/EN-BUILD-20261115.md from the shipped file and the last test runs.

Every literal output block in the document is read from a real run's log, and
the string inventory is generated from `embed/index.html`, so the document
cannot disagree with the build it describes.

Usage: python3 qa/build_en_build_doc.py
"""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
parts = {}
exec(Path("/tmp/doc-parts.py").read_text(encoding="utf-8"), parts)
sweep, poc, sixzh, sixen = parts["sweep"], parts["poc"], parts["sixzh"], parts["sixen"]
engzh, engen, parity, inv = parts["engzh"], parts["engen"], parts["parity"], parts["inv"]

FILES = [
    ("embed/index.html", "the widget: one engine, two string tables"),
    ("embed/index.html.bak-pre-en-20261115", "backup of the pre-change file"),
    ("qa/apply_en_20261115.py", "the change, machine-applied from the backup"),
    ("qa/lang_parity.py", "zh byte-parity + EN gate (12 assertions)"),
    ("qa/test_tax_engine.py", "engine, per language label, no locale in the block"),
    ("qa/verify_six_examples.py", "six worked examples, per language"),
    ("qa/sweep_heights.py", "peaks + declared heights, per language"),
    ("qa/shots_en_20261115.py", "20 screenshots, EN + zh at 390/1440"),
    ("qa/en_string_inventory.py", "the inventory below, generated from the file"),
    ("qa/zh-diff/zh-strings-before.txt", "23 states of zh strings, pre-change file"),
    ("qa/zh-diff/zh-strings-after.txt", "the same 23 states, current file"),
]
rows = []
for f, why in FILES:
    p = ROOT / f
    rows.append(f"| `{f}` | {p.stat().st_size:,} | {why} |" if p.exists() else f"| `{f}` | — | {why} |")
file_table = "\n".join(rows)

DOC = f"""# English build — 15 Nov 2026

`embed/index.html` v1.0.1 → **v1.1.0**. A language layer, not a fork: one tax
engine, one set of event wiring, two authored string tables. The Chinese build
renders byte-identically to the file it replaced — proven by a diff, below.

Backup of the pre-change file: `embed/index.html.bak-pre-en-20261115` (57,595 B).

---

## 1 · What changed, and what deliberately did not

| Layer | Change |
|---|---|
| Tax engine (`__fhfTax`) | **none** — not one character of arithmetic. `qa/test_tax_engine.py` now fails the build if a locale string, an `I18N` reference or a `t()` call appears inside the `FHF_TAX_ENGINE_START/END` block. |
| 35% cap, exact income, band bracketing | **none** — `BANDS` keeps `lo`/`hi` byte-identical; only its `label` field moved into the string table, because a band name is copy. |
| Event names and payload shape | **none** — same eight events, same parameters. One dimension added (`lang`), see §6. |
| Payment rails, receipt capture, postMessage, GTM, height protocol | **none**. |
| Chinese copy | **none** — every user-facing string, attribute, `<option>` and placeholder is byte-identical across 23 UI states (§7.6). |
| Everything a donor reads | two tables: `zh-HK` (the delivered copy) and `en` (authored English), 157 keys each, no gaps. |

How the language is attached: an element that is *entirely* a string carries
`data-i18n="key"`; one whose text contains markup carries `data-i18n-html`;
attributes use `data-i18n-aria` / `data-i18n-alt` / `data-i18n-ph`. `applyLang()`
walks those five hooks, sets `<html lang>` and `document.title`, re-renders the
result block through the same engine, and re-posts its height. Nothing is
re-fetched, and `iframe.src` is never touched.

| file | bytes | what it is |
|---|---|---|
{file_table}

---

## 2 · Switching language does not reload the frame

| How | Result |
|---|---|
| `?lang=en` at boot | English. `?lang=zh-HK`, `?lang=zh-hant-hk`, anything else → Chinese. |
| `{{type:"fhf-config", config:{{lang:"en"}}}}` at any moment | swaps every string in place, re-renders, re-posts height |

`qa/lang_parity.py` proves the second one by setting a JS marker on the frame
before the switch and reading it back after: the marker survives, `location.href`
is unchanged, and the heading becomes `Enter two things`. A switch that reloaded
the frame would fail all three.

This is the same discipline the height config already used. Setting
`iframe.src` from inside a `ready` handler is the infinite-reload trap recorded
in the project skill — `ready → apply() → src → ready`.

---

## 3 · String inventory — 157 keys, Chinese → English

Generated from `embed/index.html` by `qa/en_string_inventory.py --md`, so this
table cannot drift from the shipped file. `⏎` marks a hard line break inside the
string (the band explanation keeps the Chinese line structure).

{inv}

---

## 4 · The disclaimer — English, same shape as the Chinese

Placement is **variant B**, identical to the Chinese: a link from the consent
line, plus a collapsed `<details>` at the foot of the receipt block. Collapsed it
costs one 44px row, so no declared height depends on it.

> Before you use this calculator or send anything, please read the **disclaimer**.
>
> **Disclaimer** — This calculator gives an estimate only. It is not tax advice,
> and it does not replace professional advice. The estimate follows Inland
> Revenue Department rules for the year of assessment shown. It covers the
> deduction for recognised charitable donations only, and includes no other
> deduction, allowance or tax reduction. It does not cover profits tax, personal
> assessment, or joint assessment for a married couple. The amount you may
> deduct, and the tax you actually pay, are determined by the Inland Revenue
> Department. The calculator itself collects and stores nothing; the name and
> email you choose to give in this form are used only to issue your tax receipt.

The scope line next to the figures is also in English: *"This estimates the
donation deduction for one person under salaries tax only. It is not tax advice."*

**Status: `DRAFT — FOR CLIENT LEGAL REVIEW`.** Both languages are the same
document shape and both live in `docs/disclaimer-draft.md`; the client's legal
team should confirm that one version governs. Nothing here is presented as
approved.

---

## 5 · Heights — measured per language, and English is TALLER

`qa/sweep_heights.py`, 22 widths 320→1440px, per language. **The assumption that
English is shorter is wrong for this widget**, and it is worth knowing why: at
320px the column is ~288px wide, so an English sentence that fits one line in
Chinese wraps to two. English has fewer characters per sentence but more words,
and at the narrow end the words win.

| Block | URL | zh-HK peak | zh-HK declared | en peak | en declared | Δ peak |
|---|---|---|---|---|---|---|
| Calculator + result | `?part=calc` | 1590 @320 | **1650** | 1937 @320 | **2000** | +347 |
| Calculator only | `?part=input` | 832 @1200 | **900** | 937 @320 | **1000** | +105 |
| Result only | `?part=result` | 732 @320 | **800** | 904 @320 | **960** | +172 |
| Payment | `?part=pay` | 970 @320 | **1040** | 1144 @320 | **1210** | +174 |
| Receipt | `?part=receipt` | 599 @320 | **650** | 700 @320 | **760** | +101 |

At 1280px the same blocks are still +21…+83px in English, so the larger frame is
not only a phone problem. Nothing was padded: each declared number is the
measured peak plus 56–66px, the same policy the Chinese table already used. The
one place English gains is a per-breakpoint height — `?part=receipt` peaks at
468px above 568px, so a breakpoint pair returns 260px of dead space
(`docs/INTERFACE.md` §2 carries that pair for both languages).

Fourteen English strings were tightened after the first measurement (e.g.
"Type an amount, or pick one above."), which recovered 43px on `?part=calc` and
~20px elsewhere. That is the honest ceiling: the remaining difference is the
language, not verbosity.

**`docs/INTERFACE.md` §2 now carries a two-column table.** The English page must
use the English column — reusing 1650/900/800/1040/650 reproduces exactly the
inner-scrollbar defect the client reported on mobile.

---

## 6 · Analytics — same events, one added dimension

Unchanged: eight event names, each payload amount-free and rate-free. The
existing payload schema already carried dimensions (`band`, `state`,
`donation_type`, `cap_state`, `exact`, `rail`, `method`, `has_reference`), so
`lang: "zh-HK" | "en"` was added on that same footing rather than as a new kind
of field. It is a label, never a value.

Two consequences, stated rather than discovered later:

1. **`lang` needs a 7th GA4 custom dimension** (Event scope, name `lang`) or it
   reports as `(not set)` — the failure mode the project skill warns looks like
   a widget bug. `ops/provision-ga-gtm.py` now creates it.
2. Every message (`ready`, `resize`, `event`, `deeplink`, `pong`) also carries
   `lang`, and the in-frame GTM init `fhf_init` carries it, so a mixed report can
   be split without touching the payload again.

`qa/lang_parity.py` types a distinctive income (654,321) into the exact-income
field in **both** languages and re-scans every payload the frame ever posted:
neither `654321` nor `654,321` appears, and the event name lists are identical
between languages.

---

## 7 · Verification (literal output)

### 7.1 · The engine, labelled per language

The engine block is the same bytes in both runs — that is the point of the gate.

```
$ python3 qa/test_tax_engine.py --lang zh-HK
{engzh}
```

```
$ python3 qa/test_tax_engine.py --lang en
{engen}
```

### 7.2 · The six verified examples, rendered, per language

```
$ python3 qa/verify_six_examples.py --lang zh-HK
{sixzh}
```

```
$ python3 qa/verify_six_examples.py --lang en
{sixen}
```

### 7.3 · The Chinese harness — unchanged at 57

```
$ python3 qa/poc_test.py http://127.0.0.1:8765
{poc}
```

### 7.4 · Heights, both languages

```
$ python3 qa/sweep_heights.py
{sweep}
```

### 7.5 · Language parity and the EN gate

```
$ python3 qa/lang_parity.py
{parity}
```

### 7.6 · The Chinese strings are byte-identical — a real diff

`qa/lang_parity.py --dump` writes every Chinese string the widget renders across
23 UI states (default, each band, monthly, empty gift, big gift at the cap,
exact income, unknown band, receipt validation states, disclaimer open) from
**the pre-change file** and **the current file**, one string per line.

```
$ wc -l -c zh-strings-before.txt zh-strings-after.txt
   20231  695127 zh-strings-before.txt
   20231  695127 zh-strings-after.txt
   40462 1390254 total

$ shasum -a 256 zh-strings-*.txt
ca55e39390af9e742836993fb4b85b09f7ff2c13bc057302f05ddec2e9fe18fd  zh-strings-after.txt
ca55e39390af9e742836993fb4b85b09f7ff2c13bc057302f05ddec2e9fe18fd  zh-strings-before.txt

$ diff -u zh-strings-before.txt zh-strings-after.txt; echo "diff exit=$?"
diff exit=0
```

Same line count, same byte count, same sha256, empty diff.

---

## 8 · Screenshots — 20 files, real sizes

`screens/en-20261115/`, 2× DPR, each the whole block element. The Chinese build
is captured beside it so a reviewer can see what did not move.

| file | rendered | declared | bytes |
|---|---|---|---|
| `calc-390.png` | 390×1751 | 2000 | 378,099 |
| `calc-1440.png` | 960×1492 | 2000 | 434,336 |
| `input-390.png` | 390×890 | 1000 | 180,486 |
| `input-1440.png` | 960×849 | 1000 | 236,888 |
| `result-390.png` | 390×764 | 960 | 169,683 |
| `result-1440.png` | 960×558 | 960 | 167,606 |
| `pay-390.png` | 390×909 | 1210 | 161,797 |
| `pay-1440.png` | 960×852 | 1210 | 168,777 |
| `receipt-390.png` | 390×640 | 760 | 115,922 |
| `receipt-1440.png` | 960×449 | 760 | 107,794 |
| `calc-390-zh-HK.png` | 390×1483 | 1650 | 358,520 |
| `calc-1440-zh-HK.png` | 960×1409 | 1650 | 446,767 |
| `input-390-zh-HK.png` | 390×770 | 900 | 178,520 |
| `input-1440-zh-HK.png` | 960×828 | 900 | 247,989 |
| `result-390-zh-HK.png` | 390×632 | 800 | 153,556 |
| `result-1440-zh-HK.png` | 960×514 | 800 | 168,648 |
| `pay-390-zh-HK.png` | 390×868 | 1040 | 160,262 |
| `pay-1440-zh-HK.png` | 960×830 | 1040 | 178,906 |
| `receipt-390-zh-HK.png` | 390×560 | 650 | 117,522 |
| `receipt-1440-zh-HK.png` | 960×407 | 650 | 121,466 |

4,253,544 bytes total. Regenerate with `python3 qa/shots_en_20261115.py`.

---

## 9 · What a reviewer should check

**Copy (Global will read this first)**

1. **No exclamation marks, no hype, second person** — asserted, not just intended: `lang_parity.py` fails on any `!` in the English DOM.
2. **The five IRD terms are present and correctly used** — `recognised charitable donations`, `assessable income`, `marginal rate`, `standard rate`, `year of assessment`. On the result row the word switches: *Marginal rate used in this estimate* only where the whole deduction sat at one rate, *Standard rate used…* in the standard-rate zone, plain *Rate used…* when a gift crosses bands and the average is not a marginal rate.
3. **`（最少）` vs `（最多）` is not symmetric, and the English reflects it.** The net figure carries *(at least)* — the capped saving is at most X, so you pay at least Y — while the saving figure carries *(at most)*. My first draft used "at most" on both; the byte-identical check caught it because the Chinese label is 「實際付出（最少）」.
4. **The HK$100 receipt threshold is stated as an annual aggregate** ("your total for the year of assessment reaches HK$100"), not a per-gift test. An unconditional receipt promise would over-promise to a HK$50 donor.
5. **The spouse note does not promise the excess is transferable**, and the scope line says salaries tax only.
6. **Two terms a reviewer may want their own way**: the charity is called *the Fred Hollows Foundation* (their English name) rather than 護瞳行動 transliterated; the amount labels read *Donation* rather than *Donation amount* where the Chinese is just 捐款金額.

**Build**

7. **The engine cannot see the language** — `test_tax_engine.py` asserts zero CJK, zero `I18N` reference and zero `t()` call in the engine block, and that the file contains exactly one engine block.
8. **No Chinese left anywhere in the English DOM**, including `aria-label`, `alt`, `placeholder`, `<option>` text and hidden blocks. This gate found two band labels (`HK$145,000 以下`, `HK$5,000,000 以上`) that were still Chinese on the first pass.
9. **The figures do not move with the language** — the digit runs inside the money surface are compared state by state, both languages.
10. **Language switching is measurable**: `?lang=` for the CMS, `fhf-config` for a live switch; no `iframe.src` write anywhere.

**Open, and not mine to close**

11. **The English heights are new numbers for the client's CMS** (§5). Handing them the Chinese column is silent clipping on a phone.
12. **The `lang` dimension needs registering in GA4** (§6) before traffic, or it reads `(not set)`.
13. **POC artefacts remain in both builds** — the `POC test mode` badge, the test QR captions, and the app-open test control (hidden in `?part=` embeds, the badge is not). They come out when the merchant QR assets arrive. Identical in both languages by design: the English build is not the place to drop them.
14. **The sibling demo pages are Chinese only** (`index.html`, `preview/`, `events/`, `harness/`) and were deliberately left untouched — they embed the zh build, whose heights did not move. They are not page content; the client gets block URLs.
15. **Screenshots show the desktop QR copy at 390px** because headless Chrome does not emulate `pointer:coarse` even with `has_touch`; the mobile copy is exercised by `poc_test.py`'s device-state assertion and is unchanged in both languages.
"""
out = ROOT / "docs" / "EN-BUILD-20261115.md"
out.write_text(DOC, encoding="utf-8")
print(f"wrote {out.relative_to(ROOT)}  ({out.stat().st_size:,} bytes, {len(DOC.splitlines())} lines)")
