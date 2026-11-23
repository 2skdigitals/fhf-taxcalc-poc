#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""23 Nov 2026 — reissue the contractual heights after the disclaimer became a list.

The always-visible five-item disclaimer is ~130-190px taller than the collapsed
summary it replaced, so every block that contains it moves. This writes the new
numbers into every artefact that carries them — the two test tables, the live
contract (docs/INTERFACE.md §2), and the four sibling pages that embed the widget
at a fixed height. A stale height in a sibling page is silent clipping.

Numbers measured by qa/sweep_heights.py at 22 widths (320-1440px), both
languages, taking the peak over the default / monthly / monthly+exact shapes:

    block     zh-HK peak        en peak          declared (peak + 45..70 slack)
    calc      1656 @320         1962 @320        1720 / 2030
    input      987 @900         1113 @320        1050 / 1180
    result     913 @320         1129 @320         980 / 1190
    pay        585 @320          696 @320         640 / 750
    receipt    928 @320         1119 @320         990 / 1185
    all       2724 @320         3194 @320        2790 / 3260

Run: /Library/Developer/CommandLineTools/usr/bin/python3 qa/reissue_heights_20261123.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

NOTE = """> **Revised 23 Nov 2026 (disclaimer as a numbered list, `qa/apply_disc_list_20261123.py`).**
> The collapsed `<details class="q disc-global">` at the foot of the widget becomes an always-visible
> `<h3>` + `<ol>` of five `<li>`, in both languages, with the IRD website linked from item 4. The block
> is fine print (13px, full column) and it now always occupies ~130–190px more than the 48px summary
> row did, so **every block that carries it grew and every declared height is reissued**:
> calc 1610 → **1720** zh / 1770 → **2030** en, input 950 → **1050** / 1020 → **1180**,
> result 800 → **980** / 935 → **1190**, pay 545 → **640** / 585 → **750**,
> receipt 820 → **990** / 925 → **1185**, all 2665 → **2790** / 3000 → **3260**.
> Peaks moved with them: calc 1546 → **1656** / 1703 → **1962**, input 894 → **987** / 952 → **1113**,
> result 737 → **913** / 869 → **1129**, pay 490 → **585** / 518 → **696**,
> receipt 752 → **928** / 860 → **1119**, all 2599 → **2724** / 2935 → **3194**.
> English grew more than Chinese (1962 vs 1656 on `?part=calc`) because the English list wraps to more
> lines at phone widths; **the two columns are not interchangeable.** The peak also moved to 320px in
> almost every block, so a desktop-only sweep no longer finds it.
> **This is a client-side CMS edit**: the six heights they have already been given are superseded.
> The link inside item 4 is `https://www.ird.gov.hk/eng/welcome.htm` in English and
> `/chi/welcome.htm` in Chinese — the client supplied the `/chi/` URL, but sending an English reader to
> a Chinese page is a defect; say the word and it goes back to one URL.

"""

# ── docs/INTERFACE.md ───────────────────────────────────────────────────────
INT_ROWS = [
    ("| 0 | **One link (all four)** | `/embed/?part=all` (also the bare `/embed/`) | "
     "**2665px** | **3000px** | 2599 (at 944px, monthly) | 2935 (at 320px, monthly) |",
     "| 0 | **One link (all four)** | `/embed/?part=all` (also the bare `/embed/`) | "
     "**2790px** | **3260px** | 2724 (at 320px, monthly) | 3194 (at 320px, monthly) |"),
    ("| 1 | Calculator + result | `/embed/?part=calc` | **1610px** | **1770px** | "
     "1546 (at 944px, monthly) | 1703 (at 320px, monthly) |",
     "| 1 | Calculator + result | `/embed/?part=calc` | **1720px** | **2030px** | "
     "1656 (at 320px, monthly) | 1962 (at 320px, monthly) |"),
    ("| 1a | Calculator only | `/embed/?part=input` | **950px** | **1020px** | "
     "894 (at 900px, monthly) | 952 (at 900px, monthly) |",
     "| 1a | Calculator only | `/embed/?part=input` | **1050px** | **1180px** | "
     "987 (at 900px, monthly) | 1113 (at 320px, monthly) |"),
    ("| 1b | Result only | `/embed/?part=result` | **800px** | **935px** | 737 (at 320px) | 869 (at 320px) |",
     "| 1b | Result only | `/embed/?part=result` | **980px** | **1190px** | 913 (at 320px) | 1129 (at 320px) |"),
    ("| 2 | Payment | `/embed/?part=pay` | **545px** | **585px** | 490 (at 900px) | 518 (at 900px) |",
     "| 2 | Payment | `/embed/?part=pay` | **640px** | **750px** | 585 (at 320px) | 696 (at 320px) |"),
    ("| 3 | Receipt | `/embed/?part=receipt` | **820px** | **925px** | 752 (at 320px) | 860 (at 320px) |",
     "| 3 | Receipt | `/embed/?part=receipt` | **990px** | **1185px** | 928 (at 320px) | 1119 (at 320px) |"),
]

QW = {
    "input":   ("766 | 704 | 884 | 894 | 894", "854 | 821 | 936 | 913 | 913",
                "942 | 818 | 976 | 987 | 987", "1113 | 997 | 1029 | 1006 | 1006"),
    "result":  ("737 | 668 | 715 | 729 | 729", "869 | 795 | 715 | 729 | 729",
                "913 | 781 | 808 | 822 | 822", "1129 | 971 | 808 | 822 | 822"),
    "pay":     ("409 | 409 | 482 | 490 | 490", "437 | 437 | 510 | 518 | 518",
                "585 | 522 | 575 | 583 | 583", "696 | 613 | 603 | 611 | 611"),
    "receipt": ("752 | 752 | 680 | 688 | 688", "860 | 792 | 688 | 696 | 696",
                "928 | 865 | 773 | 780 | 780", "1119 | 968 | 781 | 789 | 789"),
    "calc":    ("1480 | 1339 | 1522 | 1546 | 1546", "1703 | 1575 | 1622 | 1617 | 1617",
                "1656 | 1452 | 1615 | 1639 | 1639", "1962 | 1751 | 1715 | 1709 | 1709"),
    "all":     ("2548 | 2407 | 2560 | 2599 | 2599", "2935 | 2712 | 2697 | 2706 | 2706",
                "2724 | 2520 | 2652 | 2691 | 2691", "3194 | 2887 | 2789 | 2798 | 2798"),
}
QW_ROWS = []
for part, (z0, e0, z1, e1) in QW.items():
    QW_ROWS.append((f"| `?part={part}` · zh | {z0} |", f"| `?part={part}` · zh | {z1} |"))
    QW_ROWS.append((f"| `?part={part}` · en | {e0} |", f"| `?part={part}` · en | {e1} |"))

ANCHOR = "> **Revised 23 Nov 2026 (client call, `qa/apply_client_call_20261123.py`)"

# ── the sibling pages and the snippet doc ───────────────────────────────────
PAGES = [
    ("index.html", [
        ("<td><b>950px</b></td><td>688 – 952</td>", "<td><b>1050px</b></td><td>781 – 1113</td>"),
        ("<td><b>800px</b></td><td>668 – 869</td>", "<td><b>980px</b></td><td>781 – 1129</td>"),
        ("<td><b>545px</b></td><td>387 – 518</td>", "<td><b>640px</b></td><td>480 – 696</td>"),
        ("<td><b>820px</b> / 925 en</td><td>664 – 860</td>",
         "<td><b>990px</b> / 1185 en</td><td>757 – 1119</td>"),
        ("<td><b>1610px</b></td><td>1328 – 1703</td>", "<td><b>1720px</b></td><td>1421 – 1962</td>"),
        ("<td><b>2665px</b> / 3000 en</td><td>2274 – 2935</td>",
         "<td><b>2790px</b> / 3260 en</td><td>2367 – 3194</td>"),
        ("It is 2,546px (zh) / 2,835px (en) at its tallest reachable state",
         "It is 2,724px (zh) / 3,194px (en) at its tallest reachable state"),
    ]),
    ("preview/index.html", [
        ('src="../embed/?part=input"   title="第一步 · 計算機" scrolling="no" style="height:950px"',
         'src="../embed/?part=input"   title="第一步 · 計算機" scrolling="no" style="height:1050px"'),
        ('src="../embed/?part=result"  title="第二步 · 估算結果" scrolling="no" style="height:800px"',
         'src="../embed/?part=result"  title="第二步 · 估算結果" scrolling="no" style="height:980px"'),
        ('src="../embed/?part=pay"     title="第三步 · 付款方式" scrolling="no" style="height:545px"',
         'src="../embed/?part=pay"     title="第三步 · 付款方式" scrolling="no" style="height:640px"'),
        ('src="../embed/?part=receipt" title="扣稅收據" scrolling="no" style="height:820px"',
         'src="../embed/?part=receipt" title="扣稅收據" scrolling="no" style="height:990px"'),
        ("the height the CMS component requires: 1000 / 890 / 580 / 810.",
         "the height the CMS component requires: 1050 / 980 / 640 / 990."),
        ("the height the CMS component requires for English: 1000 / 890 / 580 / 910.",
         "the height the CMS component requires for English: 1180 / 1190 / 750 / 1185."),
    ]),
    ("events/index.html", [
        ('src="../embed/?part=input"   title="慈善捐款扣稅計算機" scrolling="no" style="height:950px"',
         'src="../embed/?part=input"   title="慈善捐款扣稅計算機" scrolling="no" style="height:1050px"'),
        ('src="../embed/?part=result"  title="估算結果" scrolling="no" style="height:800px"',
         'src="../embed/?part=result"  title="估算結果" scrolling="no" style="height:980px"'),
        ('src="../embed/?part=pay"     title="捐款方式" scrolling="no" style="height:545px"',
         'src="../embed/?part=pay"     title="捐款方式" scrolling="no" style="height:640px"'),
        ('src="../embed/?part=receipt" title="扣稅收據" scrolling="no" style="height:820px"',
         'src="../embed/?part=receipt" title="扣稅收據" scrolling="no" style="height:990px"'),
    ]),
    ("docs/EMBED-SNIPPETS.md", [
        ("height:2665px", "height:2790px"),
        ("height:3000px", "height:3260px"),
        ("| Chinese, all-in-one | **2665** | 2599 |", "| Chinese, all-in-one | **2790** | 2724 |"),
        ("| English, all-in-one | **3000** | 2935 |", "| English, all-in-one | **3260** | 3194 |"),
        ("Both sizes carry slack, so nothing clips if a string wraps differently at their column width. **These numbers\nare current as of 23 Nov and will be re-confirmed after the copy pass lands** — the copy changes remove the\namount chips and one accordion and add a help popup, so the content height moves and the declared value will be\nreissued with it.",
         "Both sizes carry slack, so nothing clips if a string wraps differently at their column width. **These numbers\nare current as of 23 Nov 2026**, measured by `qa/sweep_heights.py` after the disclaimer became an always-visible\nfive-item list — that pass added ~130–190px to every block, so any height issued before it is stale. English is\n~470px taller than Chinese at its peak: set the column for the language you are embedding, never reuse the other."),
    ]),
]


def main():
    problems = []

    # docs/INTERFACE.md — rows, then the five-width table, then the note
    p = ROOT / "docs" / "INTERFACE.md"
    s = p.read_text(encoding="utf-8")
    for old, new in INT_ROWS + QW_ROWS:
        if s.count(old) != 1:
            problems.append(f"INTERFACE.md: {s.count(old)}x {old[:50]}")
            continue
        s = s.replace(old, new)
    if s.count(ANCHOR) != 1:
        problems.append("INTERFACE.md: revision-note anchor not found exactly once")
    else:
        s = s.replace(ANCHOR, NOTE + ANCHOR)
    p.write_text(s, encoding="utf-8")

    for rel, pairs in PAGES:
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

    # the artefacts must agree with each other now
    import json
    import re
    sweep = (ROOT / "qa" / "sweep_heights.py").read_text(encoding="utf-8")
    gate = (ROOT / "qa" / "design_gate.py").read_text(encoding="utf-8")
    m1 = re.search(r'"zh-HK": \{"calc": (\d+), "input": (\d+), "result": (\d+), "pay": (\d+), '
                   r'"receipt": (\d+), "all": (\d+)\}', sweep)
    m2 = re.search(r'"zh-HK": \{"calc": (\d+), "input": (\d+), "result": (\d+), "pay": (\d+), '
                   r'"receipt": (\d+), "all": (\d+)\}', gate)
    if not m1 or not m2 or m1.groups() != m2.groups():
        print("VERIFY FAIL: sweep_heights and design_gate disagree")
        return 1
    iface = (ROOT / "docs" / "INTERFACE.md").read_text(encoding="utf-8")
    for n in m1.groups():
        if f"**{n}px**" not in iface:
            print(f"VERIFY FAIL: INTERFACE.md does not declare {n}px")
            return 1
    print("All height artefacts agree on zh-HK:", " / ".join(m1.groups()))
    print("Reissued in: qa/sweep_heights.py, qa/design_gate.py, qa/poc_test.py,")
    print("             docs/INTERFACE.md, docs/EMBED-SNIPPETS.md,")
    print("             index.html, preview/index.html, events/index.html")
    return 0


if __name__ == "__main__":
    sys.exit(main())
