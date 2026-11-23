#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""23 Nov 2026 — reissue the contractual heights for phase 1 + the AlipayHK line.

Two changes move the numbers and a third one removes a whole block:

  · section 5 (the receipt module) is hidden for phase 1, so `?part=all` loses the
    receipt block and `?part=receipt` becomes an EMPTY frame that reports ~60px —
    a CMS frame still pointed at it must not render a form that cannot submit;
  · the payment block gains the AlipayHK receipt line + its trigger (+43px peak zh,
    +43px en);
  · the disclaimer stays exactly where it was (page level, outside every panel),
    so the blocks that carry it are unchanged.

Measured by qa/sweep_heights.py at 22 widths (320–1440px), both languages, peak
over the default / monthly / monthly+exact shapes — except `?part=receipt`, which
is measured at the frame height it will actually be given (60px: content = 0,
scrollHeight = viewport because .wrap carries min-height:100vh).

    block     zh-HK peak        en peak          declared (peak + 45..70 slack)
    calc      1656 @320         1962 @320        1720 / 2030   (unchanged)
    input      987 @900         1113 @320        1050 / 1180   (unchanged)
    result     913 @320         1129 @320         980 / 1190   (unchanged)
    pay        628 @320          739 @320         690 /  800   (was 640 / 750)
    receipt    empty frame       empty frame      60 /   60   (was 990 / 1185)
    all       2160 @944 monthly 2482 @320 monthly 2225 / 2550  (was 2790 / 3260)

A stale height in a sibling page is silent clipping, so every artefact that carries
one is written here: the two test tables, the live contract (docs/INTERFACE.md §2),
the four sibling pages that embed the widget, and docs/EMBED-SNIPPETS.md.

Run: /Library/Developer/CommandLineTools/usr/bin/python3 qa/reissue_heights_phase1_20261123.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

ZH = {"calc": 1720, "input": 1050, "result": 980, "pay": 690, "receipt": 60, "all": 2225}
EN = {"calc": 2030, "input": 1180, "result": 1190, "pay": 800, "receipt": 60, "all": 2550}

DECL_Z_OLD = ('    "zh-HK": {"calc": 1720, "input": 1050, "result": 980, "pay": 640, '
              '"receipt": 990, "all": 2790},')
DECL_Z_NEW = ('    "zh-HK": {"calc": 1720, "input": 1050, "result": 980, "pay": 690, '
              '"receipt": 60, "all": 2225},')
# the en line is aligned differently in the two files, so each keeps its own spacing
DECL_E_OLD = [('    "en":    {"calc": 2030, "input": 1180, "result": 1190, "pay": 750, '
               '"receipt": 1185, "all": 3260},'),
              ('    "en": {"calc": 2030, "input": 1180, "result": 1190, "pay": 750, '
               '"receipt": 1185, "all": 3260},')]
DECL_E_NEW = [('    "en":    {"calc": 2030, "input": 1180, "result": 1190, "pay": 800, '
               '"receipt": 60, "all": 2550},'),
              ('    "en": {"calc": 2030, "input": 1180, "result": 1190, "pay": 800, '
               '"receipt": 60, "all": 2550},')]

NOTE = """> **Revised 23 Nov 2026 (phase 1 + the AlipayHK receipt route, `qa/apply_phase1_alipay_20261123.py`).**
> Phase 1 ships **AlipayHK and the credit card only**, so section 5 — the receipt-request form, which exists to
> claim a **PayMe** receipt — is switched off behind one constant (`PHASE1`) and renders nothing. It is hidden,
> never deleted: flipping that constant brings the section, its form, its popover and `?part=receipt` back with no
> other edit. Three consequences for this table:
> - **`?part=receipt` is now an EMPTY frame.** A CMS component may still point at it, and a frame must never
>   render a form that cannot submit — so the block renders nothing and reports the viewport, i.e. **60px**.
>   Delete the component if it is still on the page; the URL stays valid.
> - **`?part=all` ends after "How you give".** The receipt block leaves the one-link arrangement:
>   **2790 → 2225px** zh-HK, **3260 → 2550px** en (peaks 2724 → **2160** at 944px monthly / 3194 → **2482**
>   at 320px monthly).
> - **The payment block gains the AlipayHK receipt line** — one sentence plus the same disclosure the
>   payment-reference field uses, carrying five client screencaps (cropped to remove the transaction reference,
>   resized to 400px, 27 KB for all five). Peak 585 → **628** zh-HK, 696 → **739** en, so **pay 640 → 690px**
>   and **750 → 800px**. The panel is bounded by the space the payment frame leaves: full width below the
>   trigger on a phone, opening upward from 720px where the trigger sits low — measured at 12 widths in both
>   languages, it never leaves the frame, and the steps scroll inside the panel.
> **The disclaimer is unchanged and still closes every block that carries content.** It was already outside the
> panels (page level), so hiding section 5 does not touch it; only the empty `?part=receipt` frame suppresses it,
> because that frame renders nothing at all. Calc / input / result are unchanged (**1720 / 1050 / 980** zh-HK,
> **2030 / 1180 / 1190** en): same disclaimer, same content.
> **This is a client-side CMS edit** — the six heights they were given are superseded by these six.
> **The IRD link is unchanged and stays per language:** disclaimer item 4 is `https://www.ird.gov.hk/eng/welcome.htm`
> in English and `https://www.ird.gov.hk/chi/welcome.htm` in Chinese (the client supplied both pages). A shared
> `/chi/` URL was considered for one turn and withdrawn, because the client's English page exists.
> `qa/lang_parity.py` asserts the two hrefs **differ** per language, so neither can be "tidied" into one.

"""

# ── docs/INTERFACE.md ───────────────────────────────────────────────────────
INT_ROWS = [
    ("Version **1.2.0** · POC · 2SK Solutions", "Version **1.3.0** · POC · 2SK Solutions"),
    ("Every message carries `source:\"fhf-taxcalc\"`, `v:\"1.2.0\"`",
     "Every message carries `source:\"fhf-taxcalc\"`, `v:\"1.3.0\"`"),
    ("| The receipt-request capture form | The receipt generator / CRM (that is the backend, Phase 1) |",
     "| The receipt-request capture form — **phase 2, returns with PayMe** | The receipt generator / CRM "
     "(that is the backend, Phase 1) |"),
    ("| 0 | **One link (all four)** | `/embed/?part=all` (also the bare `/embed/`) | "
     "**2790px** | **3260px** | 2724 (at 320px, monthly) | 3194 (at 320px, monthly) |",
     "| 0 | **One link (calculator → result → payment)** | `/embed/?part=all` (also the bare `/embed/`) | "
     "**2225px** | **2550px** | 2160 (at 944px, monthly) | 2482 (at 320px, monthly) |"),
    ("| 2 | Payment | `/embed/?part=pay` | **640px** | **750px** | 585 (at 320px) | 696 (at 320px) |",
     "| 2 | Payment | `/embed/?part=pay` | **690px** | **800px** | 628 (at 320px) | 739 (at 320px) |"),
    ("| 3 | Receipt | `/embed/?part=receipt` | **990px** | **1185px** | 928 (at 320px) | 1119 (at 320px) |",
     "| 3 | Receipt — **empty frame in phase 1** | `/embed/?part=receipt` | **60px** | **60px** | "
     "renders nothing | renders nothing |"),
    ("| `?part=pay` · zh | 585 | 522 | 575 | 583 | 583 |",
     "| `?part=pay` · zh | 628 | 566 | 610 | 618 | 618 |"),
    ("| `?part=pay` · en | 696 | 613 | 603 | 611 | 611 |",
     "| `?part=pay` · en | 739 | 656 | 638 | 646 | 646 |"),
    ("| `?part=receipt` · zh | 928 | 865 | 773 | 780 | 780 |",
     "| `?part=receipt` · zh | 60 | 60 | 60 | 60 | 60 |"),
    ("| `?part=receipt` · en | 1119 | 968 | 781 | 789 | 789 |",
     "| `?part=receipt` · en | 60 | 60 | 60 | 60 | 60 |"),
    ("| `?part=all` · zh | 2724 | 2520 | 2652 | 2691 | 2691 |",
     "| `?part=all` · zh | 2121 | 1917 | 2128 | 2160 | 2160 |"),
    ("| `?part=all` · en | 3194 | 2887 | 2789 | 2798 | 2798 |",
     "| `?part=all` · en | 2482 | 2244 | 2257 | 2259 | 2259 |"),
    # the advisory breakpoint table, restated on current measurements
    ("| Calculator + result · zh-HK | 1650 | 1450 |\n"
     "| Calculator + result · en | 2000 | 1500 |\n"
     "| Payment · zh-HK | 1040 | 900 |\n"
     "| Payment · en | 1210 | 900 |\n"
     "| Receipt · en | 1030 | 790 |",
     "| Calculator + result · zh-HK | 1656 | 1639 |\n"
     "| Calculator + result · en | 1962 | 1748 |\n"
     "| Payment · zh-HK | 628 | 618 |\n"
     "| Payment · en | 739 | 675 |\n"
     "| All in one · zh-HK | 2121 | 2160 |\n"
     "| All in one · en | 2482 | 2317 |\n"
     "| Receipt · both | 60 | 60 |"),
]
INT_ANCHOR = "> **Revised 23 Nov 2026 (disclaimer as a numbered list"

# ── index.html — the handover page ──────────────────────────────────────────
INDEX_ROWS = [
    ("<td><b>640px</b></td><td>480 – 696</td>", "<td><b>690px</b></td><td>523 – 739</td>"),
    ("<td><b>990px</b> / 1185 en</td><td>757 – 1119</td>",
     "<td><b>60px</b> — empty frame, phase 1</td><td>renders nothing</td>"),
    ("<td><b>2790px</b> / 3260 en</td><td>2367 – 3194</td>",
     "<td><b>2225px</b> / 2550 en</td><td>1857 – 2482</td>"),
    ("It is 2,724px (zh) / 3,194px (en) at its tallest reachable state",
     "It is 2,160px (zh) / 2,482px (en) at its tallest reachable state"),
    ("<b>4 · Receipt</b>", "<b>4 · Receipt</b> (phase 2 — returns with PayMe)"),
    ("<b>All four combined</b>", "<b>Calc → result → payment</b>"),
]

# ── the sibling demo pages ─────────────────────────────────────────────────
PREVIEW = [
    ('src="../embed/?part=pay"     title="第三步 · 付款方式" scrolling="no" style="height:640px"',
     'src="../embed/?part=pay"     title="第三步 · 付款方式" scrolling="no" style="height:690px"'),
    ('    <iframe id="f4" data-part="receipt" src="../embed/?part=receipt" title="扣稅收據" '
     'scrolling="no" style="height:990px"></iframe>\n', ''),
    ("the height the CMS component requires: 1050 / 980 / 640 / 990.",
     "the height the CMS component requires: 1050 / 980 / 690 — the receipt block is phase 2\n"
     "    and returns with PayMe."),
    ("the height the CMS component requires for English: 1180 / 1190 / 750 / 1185.",
     "the height the CMS component requires for English: 1180 / 1190 / 800."),
]
EVENTS = [
    ('src="../embed/?part=pay"     title="捐款方式" scrolling="no" style="height:640px"',
     'src="../embed/?part=pay"     title="捐款方式" scrolling="no" style="height:690px"'),
    ('      <iframe src="../embed/?part=receipt" title="扣稅收據" scrolling="no" '
     'style="height:990px"></iframe>\n', ''),
]
SNIPPETS = [
    ("height:2790px", "height:2225px"),
    ("height:3260px", "height:2550px"),
    ("| Chinese, all-in-one | **2790** | 2724 |", "| Chinese, calculator → payment | **2225** | 2160 |"),
    ("| English, all-in-one | **3260** | 3194 |", "| English, calculator → payment | **2550** | 2482 |"),
    ("Verified live 23 Nov 2026: `/embed/` → `lang=zh-Hant-HK`, four sections; `/embed/?lang=en` → `lang=en`, four\nsections. Both return 200.",
     "Verified live 23 Nov 2026: `/embed/` → `lang=zh-Hant-HK`, three content sections (calculator, result, payment);\n`/embed/?lang=en` → `lang=en`, three sections. Both return 200. **Phase 1 has no receipt block** — it returns\nwith PayMe, and `?part=receipt` currently renders an empty 60px frame."),
    ("`?part=receipt`, with heights 1800 · 580 · 810 (zh) / 910 (en).",
     "`?part=receipt`, with heights 1720 / 690 / 60 (zh) and 2030 / 800 / 60 (en) — the receipt block is 990 / 1185\nwhen it returns in phase 2."),
    ("are current as of 23 Nov 2026**, measured by `qa/sweep_heights.py` after the disclaimer became an always-visible\nfive-item list — that pass added ~130–190px to every block, so any height issued before it is stale. English is\n~470px taller than Chinese at its peak: set the column for the language you are embedding, never reuse the other.",
     "are current as of 23 Nov 2026**, measured by `qa/sweep_heights.py` after phase 1 (the receipt block hidden, the\nAlipayHK receipt line added) — that pass REMOVED ~560–710px from the one-link frame and added ~43px to the payment\nblock, so any height issued before it is stale. English is still ~260px taller than Chinese at its peak: set the\ncolumn for the language you are embedding, never reuse the other."),
]

PAGES = [("index.html", INDEX_ROWS), ("preview/index.html", PREVIEW),
         ("events/index.html", EVENTS), ("docs/EMBED-SNIPPETS.md", SNIPPETS)]

# ── the two QA tables and the poc BUDGET ───────────────────────────────────
QA = [
    ("qa/sweep_heights.py", [
        (DECL_Z_OLD, DECL_Z_NEW),
        (DECL_E_OLD[0], DECL_E_NEW[0]),
        ("# Peaks now: calc 1656/1962, input 987/1113, result 913/1129, pay 585/696,\n"
         "# receipt 928/1119, all 2724/3194. Every declared value below is reissued.",
         "# Reissued AGAIN 23 Nov 2026 (phase 1, qa/apply_phase1_alipay_20261123.py): section 5\n"
         "# is hidden (PHASE1) and ?part=receipt is an empty 60px frame, while the payment block\n"
         "# gains the AlipayHK receipt line. Peaks now: calc 1656/1962, input 987/1113,\n"
         "# result 913/1129, pay 628/739, receipt 0 (empty frame), all 2160/2482."),
    ]),
    ("qa/design_gate.py", [(DECL_Z_OLD, DECL_Z_NEW),
                           (DECL_E_OLD[1], DECL_E_NEW[1])]),
    ("qa/poc_test.py", [
        ('    BUDGET = {"calc": 1720, "input": 1050, "result": 980, "pay": 640, '
         '"receipt": 990, "all": 2790}',
         '    BUDGET = {"calc": 1720, "input": 1050, "result": 980, "pay": 690, '
         '"receipt": 60, "all": 2225}'),
        ("    # zh-HK: 1720 / 1050 / 980 / 640 / 990 / 2790.",
         "    # zh-HK: 1720 / 1050 / 980 / 690 / 60 / 2225."),
    ]),
]


def main():
    problems = []

    iface = ROOT / "docs" / "INTERFACE.md"
    s = iface.read_text(encoding="utf-8")
    for old, new in INT_ROWS:
        if s.count(old) != 1:
            problems.append(f"INTERFACE.md: {s.count(old)}x {old[:60]}")
            continue
        s = s.replace(old, new)
    if s.count(INT_ANCHOR) != 1:
        problems.append("INTERFACE.md: revision-note anchor not found exactly once")
    else:
        s = s.replace(INT_ANCHOR, NOTE + INT_ANCHOR)
    iface.write_text(s, encoding="utf-8")

    for rel, pairs in PAGES + QA:
        f = ROOT / rel
        t = f.read_text(encoding="utf-8")
        for old, new in pairs:
            n = t.count(old)
            if n != 1:
                problems.append(f"{rel}: {n}x {old[:60]}")
                continue
            t = t.replace(old, new)
        f.write_text(t, encoding="utf-8")

    if problems:
        print("VERIFY FAIL:")
        for x in problems:
            print("  -", x)
        return 1

    # every artefact must now agree
    sweep = (ROOT / "qa" / "sweep_heights.py").read_text(encoding="utf-8")
    gate = (ROOT / "qa" / "design_gate.py").read_text(encoding="utf-8")
    poc = (ROOT / "qa" / "poc_test.py").read_text(encoding="utf-8")
    pat = (r'"zh-HK": \{"calc": (\d+), "input": (\d+), "result": (\d+), "pay": (\d+), '
           r'"receipt": (\d+), "all": (\d+)\}')
    m1, m2 = re.search(pat, sweep), re.search(pat, gate)
    if not m1 or not m2 or m1.groups() != m2.groups():
        print("VERIFY FAIL: sweep_heights and design_gate disagree")
        return 1
    if tuple(int(x) for x in m1.groups()) != tuple(ZH[k] for k in
                                                   ("calc", "input", "result", "pay", "receipt", "all")):
        print("VERIFY FAIL: declared table is not the reissued set")
        return 1
    for k, v in ZH.items():
        if f'"{k}": {v}' not in poc:
            print(f"VERIFY FAIL: poc_test BUDGET does not carry {k}={v}")
            return 1
    for n in m1.groups():
        if n != "60" and f"**{n}px**" not in iface.read_text(encoding="utf-8"):
            print(f"VERIFY FAIL: INTERFACE.md does not declare {n}px")
            return 1
    print("All height artefacts agree:")
    print("  zh-HK:", " / ".join(f"{k} {v}" for k, v in ZH.items()))
    print("  en   :", " / ".join(f"{k} {v}" for k, v in EN.items()))
    print("Reissued in: qa/sweep_heights.py, qa/design_gate.py, qa/poc_test.py,")
    print("             docs/INTERFACE.md, docs/EMBED-SNIPPETS.md,")
    print("             index.html, preview/index.html, events/index.html")
    return 0


if __name__ == "__main__":
    sys.exit(main())
