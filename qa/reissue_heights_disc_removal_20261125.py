#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""25 Nov 2026 — reissue every contractual height after the disclaimer left the widget.

The disclaimer was the one block every part carried (page level, outside every
panel), so removing it shortens EVERY document, in both languages, by 170px at
desktop widths and by up to 336px at 320px, where the five sentences wrapped
hardest. Measured by qa/sweep_heights.py at 22 widths (320–1440px), peak over the
default / monthly / monthly+exact shapes:

    block     zh-HK peak        en peak          declared (peak + 62..70 slack)
    calc      1425 @944         1541 @320        1495 / 1610   (was 1720 / 2030)
    input      817 @900          875 @900         880 /  940   (was 1050 / 1180)
    result     660 @320          792 @320         725 /  860   (was  980 / 1190)
    pay        443 @900          472 @900         505 /  535   (was  690 /  800)
    receipt   empty frame        empty frame       60 /   60   (unchanged — phase 1)
    all       1942 @944         2062 @320        2010 / 2130   (was 2225 / 2550)

`?part=receipt` is still the empty phase-1 frame at 60px. When PayMe ships and
section 5 returns, the receipt block is **745 / 855**, not 990 / 1185: the same
~214px leaves it (measured with `data-phase` removed and the module visible, at
the five widths — 675 / 783 at 320px).

A stale height is silent, so every artefact that carries one is written here: the
three QA tables, the live contract (docs/INTERFACE.md §2), the four sibling pages
and docs/EMBED-SNIPPETS.md, plus the GTM handover appendix that answers "should we
change the height=2200 on the English page?" — it does not have to (2130 is the
exact number, 2200 keeps 138px of slack).

Run: /Library/Developer/CommandLineTools/usr/bin/python3 qa/reissue_heights_disc_removal_20261125.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

ZH = {"calc": 1495, "input": 880, "result": 725, "pay": 505, "receipt": 60, "all": 2010}
EN = {"calc": 1610, "input": 940, "result": 860, "pay": 535, "receipt": 60, "all": 2130}

# ── the three QA tables ─────────────────────────────────────────────────────
SWEEP_OLD = '''DECLARED = {
    "zh-HK": {"calc": 1720, "input": 1050, "result": 980, "pay": 690, "receipt": 60, "all": 2225},
    "en":    {"calc": 2030, "input": 1180, "result": 1190, "pay": 800, "receipt": 60, "all": 2550},
}'''
SWEEP_NEW = '''DECLARED = {
    "zh-HK": {"calc": 1495, "input": 880, "result": 725, "pay": 505, "receipt": 60, "all": 2010},
    "en":    {"calc": 1610, "input": 940, "result": 860, "pay": 535, "receipt": 60, "all": 2130},
}'''
SWEEP_NOTE_OLD = '''# the numbers to the desktop ones: the frame has to clear the phone.
'''
SWEEP_NOTE_NEW = '''# the numbers to the desktop ones: the frame has to clear the phone.
# Reissued 25 Nov 2026 (the disclaimer left the widget for the client's own Rich Text
# Editor block, qa/apply_remove_disclaimer_20261125.py): the block closed EVERY part, so
# every block shortens — 170px at desktop widths, 317–336px at 320px where the five
# sentences wrapped hardest. Peaks now: calc 1425/1541, input 817/875, result 660/792,
# pay 443/472, receipt 0 (empty phase-1 frame), all 1942/2062.
'''
GATE_OLD = '''DECLARED = {
    "zh-HK": {"calc": 1720, "input": 1050, "result": 980, "pay": 690, "receipt": 60, "all": 2225},
    "en": {"calc": 2030, "input": 1180, "result": 1190, "pay": 800, "receipt": 60, "all": 2550},
}'''
GATE_NEW = '''DECLARED = {
    "zh-HK": {"calc": 1495, "input": 880, "result": 725, "pay": 505, "receipt": 60, "all": 2010},
    "en": {"calc": 1610, "input": 940, "result": 860, "pay": 535, "receipt": 60, "all": 2130},
}'''
POC_BUDGET_OLD = '''    BUDGET = {"calc": 1720, "input": 1050, "result": 980, "pay": 690, "receipt": 60, "all": 2225}'''
POC_BUDGET_NEW = '''    BUDGET = {"calc": 1495, "input": 880, "result": 725, "pay": 505, "receipt": 60, "all": 2010}'''
POC_COMMENT_OLD = '''    # zh-HK: 1720 / 1050 / 980 / 690 / 60 / 2225.'''
POC_COMMENT_NEW = '''    # 25 Nov 2026 (the disclaimer left the widget): every block sheds 170px at desktop
    # widths and 317-336px at 320px, so the zh set is reissued as 1495 / 880 / 725 /
    # 505 / 60 / 2010, and the en set as 1610 / 940 / 860 / 535 / 60 / 2130.
    # zh-HK: 1495 / 880 / 725 / 505 / 60 / 2010.'''
POC_PHASE2_OLD = '''    #     PHASE1 flips. Its frame numbers are the phase-2 declarations (990 / 1185).'''
POC_PHASE2_NEW = '''    #     PHASE1 flips. Its frame numbers are the phase-2 declarations (745 / 855 —
    #     reissued 25 Nov: the removed disclaimer took ~214px off this block too).'''
POC_FRAME_OLD = '''    for lang_q, frame_h in (("", 990), ("&lang=en", 1185)):'''
POC_FRAME_NEW = '''    for lang_q, frame_h in (("", 745), ("&lang=en", 855)):'''

QA = [
    ("qa/sweep_heights.py", [(SWEEP_OLD, SWEEP_NEW), (SWEEP_NOTE_OLD, SWEEP_NOTE_NEW)]),
    ("qa/design_gate.py", [(GATE_OLD, GATE_NEW)]),
    ("qa/poc_test.py", [(POC_BUDGET_OLD, POC_BUDGET_NEW),
                        (POC_COMMENT_OLD, POC_COMMENT_NEW),
                        (POC_PHASE2_OLD, POC_PHASE2_NEW),
                        (POC_FRAME_OLD, POC_FRAME_NEW)]),
]

# ── docs/INTERFACE.md — the live contract ───────────────────────────────────
INT_ROWS = [
    ("Version **1.4.0** · POC · 2SK Solutions", "Version **1.5.0** · POC · 2SK Solutions"),
    ("**Write the height as a bare integer — `height=2550`, never `height=2,550`.**",
     "**Write the height as a bare integer — `height=2130`, never `height=2,130`.**"),
    ("| 0 | **One link (calculator → result → payment)** | `/embed/?part=all` (also the bare `/embed/`) | "
     "**2225px** | **2550px** | 2160 (at 944px, monthly) | 2482 (at 320px, monthly) |",
     "| 0 | **One link (calculator → result → payment)** | `/embed/?part=all` (also the bare `/embed/`) | "
     "**2010px** | **2130px** | 1942 (at 944px, monthly) | 2062 (at 320px, monthly) |"),
    ("| 1 | Calculator + result | `/embed/?part=calc` | **1720px** | **2030px** | "
     "1656 (at 320px, monthly) | 1962 (at 320px, monthly) |",
     "| 1 | Calculator + result | `/embed/?part=calc` | **1495px** | **1610px** | "
     "1425 (at 944px, monthly) | 1541 (at 320px, monthly) |"),
    ("| 1a | Calculator only | `/embed/?part=input` | **1050px** | **1180px** | "
     "987 (at 900px, monthly) | 1113 (at 320px, monthly) |",
     "| 1a | Calculator only | `/embed/?part=input` | **880px** | **940px** | "
     "817 (at 900px, monthly) | 875 (at 900px, monthly) |"),
    ("| 1b | Result only | `/embed/?part=result` | **980px** | **1190px** | 913 (at 320px) | 1129 (at 320px) |",
     "| 1b | Result only | `/embed/?part=result` | **725px** | **860px** | 660 (at 320px) | 792 (at 320px) |"),
    ("| 2 | Payment | `/embed/?part=pay` | **690px** | **800px** | 628 (at 320px) | 739 (at 320px) |",
     "| 2 | Payment | `/embed/?part=pay` | **505px** | **535px** | 443 (at 900px) | 472 (at 900px) |"),
    ("**Quoted at the five widths the client asked for (content height, px) — re-measured 24 Nov 2026**",
     "**Quoted at the five widths the client asked for (content height, px) — re-measured 25 Nov 2026**"),
    ("| `?part=input` · zh | 942 | 818 | 976 | 987 | 987 |",
     "| `?part=input` · zh | 689 | 627 | 807 | 817 | 817 |"),
    ("| `?part=input` · en | 1113 | 997 | 1029 | 1006 | 1006 |",
     "| `?part=input` · en | 777 | 744 | 859 | 836 | 836 |"),
    ("| `?part=result` · zh | 913 | 781 | 808 | 822 | 822 |",
     "| `?part=result` · zh | 660 | 591 | 638 | 652 | 652 |"),
    ("| `?part=result` · en | 1129 | 971 | 808 | 822 | 822 |",
     "| `?part=result` · en | 792 | 718 | 638 | 652 | 652 |"),
    ("| `?part=pay` · zh | 628 | 566 | 568 | 613 | 613 |",
     "| `?part=pay` · zh | 375 | 375 | 398 | 443 | 443 |"),
    ("| `?part=pay` · en | 739 | 656 | 596 | 641 | 641 |",
     "| `?part=pay` · en | 403 | 403 | 426 | 472 | 472 |"),
    ("| `?part=calc` · zh | 1656 | 1452 | 1615 | 1639 | 1639 |",
     "| `?part=calc` · zh | 1339 | 1218 | 1401 | 1425 | 1425 |"),
    ("| `?part=calc` · en | 1962 | 1751 | 1695 | 1689 | 1689 |",
     "| `?part=calc` · en | 1541 | 1434 | 1481 | 1475 | 1475 |"),
    ("| `?part=all` · zh | 2121 | 1917 | 2086 | 2156 | 2156 |",
     "| `?part=all` · zh | 1803 | 1682 | 1872 | 1942 | 1942 |"),
    ("| `?part=all` · en | 2482 | 2244 | 2194 | 2234 | 2234 |",
     "| `?part=all` · en | 2062 | 1926 | 1981 | 2020 | 2020 |"),
]

INT_NOTE = """> **Revised 25 Nov 2026 (the disclaimer left the widget, `qa/apply_remove_disclaimer_20261125.py`).**
> The client added a Rich Text Editor block on their own page to carry the legal disclaimer, so the widget
> stopped carrying it: the five-sentence `<section id="disclaimer">` and the one-line "Based on IRD tax
> rates…" note above it are gone, in both languages, along with their i18n keys. Their copy is now written
> **once**, on their page — the widget does not render it in any part.
> - **Every declared height moves down**, because the block closed *every* part: `?part=all`
>   **2225 → 2010px** zh-HK, **2550 → 2130px** en; `calc` **1720 → 1495 / 2030 → 1610**;
>   `input` **1050 → 880 / 1180 → 940**; `result` **980 → 725 / 1190 → 860**;
>   `pay` **690 → 505 / 800 → 535**. `?part=receipt` stays **60px** (it is the empty phase-1 frame).
>   New peaks: calc 1425 / 1541, input 817 / 875, result 660 / 792, pay 443 / 472, all 1942 / 2062.
> - **The English page carries `height=2200`, and it does not have to change.** The English content peak is
>   **2062px** (at 320px), so 2200 still fits with 138px to spare; **2130** is the exact declaration if they
>   want to trim it. The Chinese frame at 2225 is likewise safe, or 2010 exactly.
> - **The disclaimer's CSS is deliberately left in place** (`.disc-global`, `.disc-list`, `.disc-h`, the
>   focus rules, and the phase-1 rule for the empty `?part=receipt` frame). It is the record of what
>   shipped; nothing matches it, so it costs nothing. Do not rebuild the block to "use" it.
> - **The consent line inside the phase-2 receipt form lost its anchor** — it read "Read the disclaimer
>   before you send anything." with a link to the block, and the block is gone. It is plain text now, both
>   languages, and `qa/lang_parity.py` + `qa/poc_test.py` fail if the link or the block returns.
> - **When PayMe ships and section 5 returns**, `?part=receipt` becomes a real block at **745px** zh-HK /
>   **855px** en (it was quoted as 990 / 1185; the same ~214px leaves it).

"""

INT_ANCHOR = "> **Revised 24 Nov 2026 (Option B payment pair, `qa/apply_pay_optionb_20261124.py`).**"

# ── docs/EMBED-SNIPPETS.md ─────────────────────────────────────────────────
SNIPPETS = [
    ('style="border:0;width:100%;height:2225px;display:block"',
     'style="border:0;width:100%;height:2010px;display:block"'),
    ('style="border:0;width:100%;height:2550px;display:block"',
     'style="border:0;width:100%;height:2130px;display:block"'),
    ("| Chinese, calculator → payment | **2225** | 2160 |",
     "| Chinese, calculator → payment | **2010** | 1942 |"),
    ("| English, calculator → payment | **2550** | 2482 |",
     "| English, calculator → payment | **2130** | 2062 |"),
    ('''Both sizes carry slack, so nothing clips if a string wraps differently at their column width. **These numbers
are current as of 23 Nov 2026**, measured by `qa/sweep_heights.py` after phase 1 (the receipt block hidden, the
AlipayHK receipt line added) — that pass REMOVED ~560–710px from the one-link frame and added ~43px to the payment
block, so any height issued before it is stale. English is still ~260px taller than Chinese at its peak: set the
column for the language you are embedding, never reuse the other.''',
     '''Both sizes carry slack, so nothing clips if a string wraps differently at their column width. **These numbers
are current as of 25 Nov 2026**, measured by `qa/sweep_heights.py` after the disclaimer left the widget for the
client's own Rich Text Editor block — that pass removed 170px from every block at desktop widths and up to 336px at
320px, so any height issued before it is stale (2225 / 2550 → **2010 / 2130**). English is still ~120px taller than
Chinese at its peak: set the column for the language you are embedding, never reuse the other.
**The English page's `height=2200` still fits** (peak 2062) — 2130 is the exact number if they want to trim it, and
2225 on the Chinese page is safe the same way.'''),
    ('''`?part=receipt`, with heights 1720 / 690 / 60 (zh) and 2030 / 800 / 60 (en) — the receipt block is 990 / 1185
when it returns in phase 2.''',
     '''`?part=receipt`, with heights 1495 / 505 / 60 (zh) and 1610 / 535 / 60 (en) — the receipt block is 745 / 855
when it returns in phase 2.'''),
]

# ── index.html — the handover page ─────────────────────────────────────────
INDEX = [
    ("<td><b>1050px</b></td><td>781 – 1113</td>", "<td><b>880px</b></td><td>627 – 817</td>"),
    ("<td><b>980px</b></td><td>781 – 1129</td>", "<td><b>725px</b></td><td>591 – 792</td>"),
    ("<td><b>690px</b></td><td>523 – 739</td>", "<td><b>505px</b></td><td>375 – 472</td>"),
    ("<td><b>1720px</b></td><td>1421 – 1962</td>", "<td><b>1495px</b></td><td>1218 – 1541</td>"),
    ("<td><b>2225px</b> / 2550 en</td><td>1857 – 2482</td>",
     "<td><b>2010px</b> / 2130 en</td><td>1682 – 2062</td>"),
    ("It is 2,160px (zh) / 2,482px (en) at its tallest reachable state",
     "It is 1,942px (zh) / 2,062px (en) at its tallest reachable state"),
    ("<li>Paste <b>Block 1</b> at <b>1120px</b>.", "<li>Paste <b>Block 1</b> at <b>880px</b>."),
    ("Repeat for Blocks 2–4 at 920 / 600 / 780px.",
     "Repeat for Blocks 2–4 at 725 / 505 / 60px (block 4 is an empty frame in phase 1)."),
]

# ── the sibling demo pages ─────────────────────────────────────────────────
PREVIEW = [
    ('src="../embed/?part=input"   title="第一步 · 計算機" scrolling="no" style="height:1050px"',
     'src="../embed/?part=input"   title="第一步 · 計算機" scrolling="no" style="height:880px"'),
    ('src="../embed/?part=result"  title="第二步 · 估算結果" scrolling="no" style="height:980px"',
     'src="../embed/?part=result"  title="第二步 · 估算結果" scrolling="no" style="height:725px"'),
    ('src="../embed/?part=pay"     title="第三步 · 付款方式" scrolling="no" style="height:690px"',
     'src="../embed/?part=pay"     title="第三步 · 付款方式" scrolling="no" style="height:505px"'),
]
EVENTS = [
    ('<iframe src="../embed/?part=input"   title="慈善捐款扣稅計算機" scrolling="no" style="height:1050px"></iframe>',
     '<iframe src="../embed/?part=input"   title="慈善捐款扣稅計算機" scrolling="no" style="height:880px"></iframe>'),
    ('<iframe src="../embed/?part=result"  title="估算結果" scrolling="no" style="height:980px"></iframe>',
     '<iframe src="../embed/?part=result"  title="估算結果" scrolling="no" style="height:725px"></iframe>'),
    ('<iframe src="../embed/?part=pay"     title="捐款方式" scrolling="no" style="height:690px"></iframe>',
     '<iframe src="../embed/?part=pay"     title="捐款方式" scrolling="no" style="height:505px"></iframe>'),
]

# ── the GTM handover appendix — the page's own frame ───────────────────────
GTM = [
    ('width="100%" height=2550 frameborder=0', 'width="100%" height=2130 frameborder=0'),
    ("<code>height=2,550</code> parses as <code>3</code>",
     "<code>height=2,130</code> parses as <code>3</code>"),
    ('''<li>The page currently carries <code>height=2200</code>: measured content is 2,162 at desktop and 2,202 at 390px — it fits until a 320px-wide phone, where the block is 2,482 and roughly 280px is cut off.</li>''',
     '''<li>The page currently carries <code>height=2200</code> on the English frame, and <strong>it still fits</strong>: since the disclaimer moved to the page's own Rich Text Editor block the English content peaks at <strong>2,062</strong> (at 320px), so 2,200 carries 138px of slack. <code>height=2130</code> is the exact declaration if you want to trim it. The Chinese frame needs <strong>2,010</strong>; 2,225 is safe the same way.</li>'''),
]

PAGES = [("index.html", INDEX), ("preview/index.html", PREVIEW),
         ("events/index.html", EVENTS),
         ("docs/EMBED-SNIPPETS.md", SNIPPETS),
         ("docs/FHF-Tax-Calculator-GTM-Handover.html", GTM)]


def main():
    problems = []

    iface = ROOT / "docs" / "INTERFACE.md"
    s = iface.read_text(encoding="utf-8")
    for old, new in INT_ROWS:
        if s.count(old) != 1:
            problems.append(f"INTERFACE.md: {s.count(old)}x {old[:70]}")
            continue
        s = s.replace(old, new)
    if s.count(INT_ANCHOR) != 1:
        problems.append("INTERFACE.md: revision-note anchor not found exactly once")
    else:
        s = s.replace(INT_ANCHOR, INT_NOTE + INT_ANCHOR)
    iface.write_text(s, encoding="utf-8")

    for rel, pairs in PAGES + QA:
        f = ROOT / rel
        t = f.read_text(encoding="utf-8")
        for old, new in pairs:
            n = t.count(old)
            if n != 1:
                problems.append(f"{rel}: {n}x {old[:70]}")
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
    me = re.search(r'"en":\s+\{"calc": (\d+), "input": (\d+), "result": (\d+), "pay": (\d+), '
                   r'"receipt": (\d+), "all": (\d+)\}', sweep)
    if not me or tuple(int(x) for x in me.groups()) != tuple(EN[k] for k in
                                                             ("calc", "input", "result", "pay", "receipt", "all")):
        print("VERIFY FAIL: the en declared table is not the reissued set")
        return 1
    for k, v in ZH.items():
        if f'"{k}": {v}' not in poc:
            print(f"VERIFY FAIL: poc_test BUDGET does not carry {k}={v}")
            return 1
    for n in set(ZH.values()) | set(EN.values()):
        if n == 60:
            continue
        for label, want in ((f"**{n}px**", 1),):
            if want and label not in iface.read_text(encoding="utf-8"):
                print(f"VERIFY FAIL: INTERFACE.md does not declare {label}")
                return 1
    print("All height artefacts agree:")
    print("  zh-HK:", " / ".join(f"{k} {v}" for k, v in ZH.items()))
    print("  en   :", " / ".join(f"{k} {v}" for k, v in EN.items()))
    print("Reissued in: qa/sweep_heights.py, qa/design_gate.py, qa/poc_test.py,")
    print("             docs/INTERFACE.md, docs/EMBED-SNIPPETS.md,")
    print("             index.html, preview/index.html, events/index.html,")
    print("             docs/FHF-Tax-Calculator-GTM-Handover.html")
    return 0


if __name__ == "__main__":
    sys.exit(main())
