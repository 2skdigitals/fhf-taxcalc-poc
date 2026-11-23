#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kevin's client call, 23 Nov 2026 — three changes, applied as one re-runnable pass.

  1 · defaults move to the bottom of each input
      · donation amount 1,300 -> 100 (HK$100 is the floor of the field)
      · the manual/exact-income field "" -> 145,000 (the single person's
        basic allowance, i.e. the bottom of the income input). It is a starting
        value, not a floor: opening the swap adopts it into the engine so the
        figure on screen and the figure used are never two different numbers.
  2 · width follows the Foundation's own component
      · .wrap 56rem (896px) -> 80rem (1280px), the width their iframe gets
        inside div.container at a 1440 viewport. Gutters and the phone
        arrangement are untouched; running text stays on --measure (34em), so
        panels and cards fill the column while a paragraph never runs 1,280px.
  3 · type follows the Foundation (18px body / 1.56, from their 18/28)
      · body 17 -> 18, line-height 1.6 -> 1.56
      · step heading 28 -> 32, lede 19 -> 20, sm 15 -> 16, num 21 -> 22,
        display 68 -> 72 (still the largest thing in its block)
      · 13px notes and the 12px eyebrow are unchanged — their page has 13px
        fine print in the same components
      · heading leading 1.14 -> 1.2 so two-line CJK headings get room; every
        step keeps one ratio for both languages, so Chinese is never tighter
        than Latin.

No copy, colour, shadow or font-family change. Engine and event names untouched.

Run:  /Library/Developer/CommandLineTools/usr/bin/python3 qa/apply_client_call_20261123.py
"""
import pathlib
import sys

SRC = pathlib.Path(__file__).resolve().parent.parent / "embed" / "index.html"
BAK = SRC.with_name(SRC.name + ".bak-pre-clientcall-20261123")

EDITS = [
    # ── 3 · type scale ───────────────────────────────────────────────────
    ("type · sm 15 -> 16",
     "  --t-sm:.9375rem;                     /* 15 · controls, ledger rows */",
     "  --t-sm:1rem;                         /* 16 · controls, ledger rows */"),
    ("type · body 17 -> 18",
     "  --t-body:1.0625rem;                  /* 17 · running text */",
     "  --t-body:1.125rem;                   /* 18 · running text */"),
    ("type · num 21 -> 22",
     "  --t-num:1.3125rem;                   /* 21 · ledger figures */",
     "  --t-num:1.375rem;                    /* 22 · ledger figures */"),
    ("type · block heading 22→28 -> 24→32",
     "  --t-h:clamp(1.375rem,3.4vw,1.75rem); /* 22→28 · block heading */",
     "  --t-h:clamp(1.5rem,3.6vw,2rem);      /* 24→32 · block heading */"),
    ("type · lede 17→19 -> 18→20",
     "  --t-lede:clamp(1.0625rem,2.2vw,1.1875rem); /* 17→19 · one statement */",
     "  --t-lede:clamp(1.125rem,2.2vw,1.25rem); /* 18→20 · one statement */"),
    ("type · display 44→68 -> 46→72",
     "  --t-display:clamp(2.75rem,11vw,4.25rem);   /* 44→68 · the number */",
     "  --t-display:clamp(2.875rem,11vw,4.5rem);   /* 46→72 · the number */"),
    ("type · body leading 1.6 -> 1.56",
     "  font-family:var(--sans);font-weight:400;font-size:var(--t-body);line-height:1.6;",
     "  font-family:var(--sans);font-weight:400;font-size:var(--t-body);line-height:1.56;"),
    ("type · heading leading 1.14 -> 1.2 (two-line CJK)",
     "  font-size:var(--t-h);line-height:1.14;font-weight:700;letter-spacing:-.024em;",
     "  font-size:var(--t-h);line-height:1.2;font-weight:700;letter-spacing:-.024em;"),
    ("type · lede leading 1.5 -> 1.56",
     ".lede{font-size:var(--t-body);line-height:1.5;color:var(--ink-2);margin:var(--s3) 0 0;max-width:var(--measure)}",
     ".lede{font-size:var(--t-body);line-height:1.56;color:var(--ink-2);margin:var(--s3) 0 0;max-width:var(--measure)}"),
    ("type · benefit sentence leading 1.48 -> 1.56",
     "  font-size:var(--t-lede);line-height:1.48;letter-spacing:-.008em;",
     "  font-size:var(--t-lede);line-height:1.56;letter-spacing:-.008em;"),

    # ── 2 · width ────────────────────────────────────────────────────────
    ("width · .wrap 56rem (896px) -> 80rem (1280px)",
     ".wrap{max-width:56rem;margin:0 auto;padding:clamp(18px,3.4vw,26px) var(--gut) 24px}",
     ".wrap{max-width:80rem;margin:0 auto;padding:clamp(18px,3.4vw,26px) var(--gut) 24px}"),

    # The legal block was given the whole column when the column was 896px; at
    # 1280 it would run ~180 characters a line at 13px. It keeps the fine-print
    # size and takes the same measure every other paragraph uses.
    ("width · disclaimer keeps the readable measure",
     "details.q.disc-global p,details.q.disc-global ul{font-size:var(--t-cap);line-height:1.6;max-width:none}",
     "details.q.disc-global p,details.q.disc-global ul{font-size:var(--t-cap);line-height:1.6;max-width:var(--measure)}"),

    # ── 1 · defaults ─────────────────────────────────────────────────────
    ("default · gift field 1,300 -> 100",
     '<input id="gift" type="text" inputmode="numeric" autocomplete="off" value="1,300">',
     '<input id="gift" type="text" inputmode="numeric" autocomplete="off" value="100">'),
    ("default · engine state amount 1300 -> 100",
     '  var st = {amount:1300, band:"r17", mode:"once", exact:0};',
     '  var st = {amount:100, band:"r17", mode:"once", exact:0};'),
    ("default · exact-income field \"\" -> 145,000",
     '<input id="exact" type="text" inputmode="numeric" autocomplete="off" value="" placeholder="e.g. 500,000"',
     '<input id="exact" type="text" inputmode="numeric" autocomplete="off" value="145,000" placeholder="e.g. 500,000"'),
    ("default · hero figure fallback 1,300 -> 100",
     '<p class="net" id="net"><span class="cur">HK$</span>1,300</p>',
     '<p class="net" id="net"><span class="cur">HK$</span>100</p>'),
    ("default · saved figure fallback 221 -> 14–17",
     '<dd id="saved">HK$221</dd>',
     '<dd id="saved">HK$14 至 HK$17</dd>'),
    ("default · rate fallback 17% -> 14%–17%",
     '<dd id="rate">17%</dd>',
     '<dd id="rate">14% – 17%</dd>'),

    # the exact swap adopts its starting value, so the visible field and the
    # engine always agree about which figure is in force
    ("default · opening the exact swap adopts the starting value",
     """    if (!exactMode) clearExact();
    else { var ex0 = $("#exact"); if (ex0) ex0.focus(); }""",
     """    if (!exactMode) clearExact();
    else {
      /* the field carries a starting value (the basic allowance), so opening
         it adopts that value rather than leaving the box ahead of the maths */
      var ex0 = $("#exact");
      if (ex0) { if (!digits(ex0.value)) ex0.value = fmt(EXACT_DEFAULT); st.exact = digits(ex0.value); ex0.focus(); }
    }"""),
    ("default · clearExact resets to the starting value, not an empty box",
     """  function clearExact(){
    if (!st.exact) return;
    st.exact = 0;
    var ex = $("#exact");
    if (ex) ex.value = "";
  }""",
     """  /* 23 Nov: the exact-income field has a starting value — the single person's
     basic allowance (HK$145,000), the bottom of the income input — rather than an
     empty box. It is a default, never a floor: typing replaces it, nothing clamps,
     and picking a band puts it back so the two controls cannot disagree. */
  var EXACT_DEFAULT = 145000;
  function clearExact(){
    var ex = $("#exact");
    if (ex) ex.value = fmt(EXACT_DEFAULT);
    if (!st.exact) return;
    st.exact = 0;
  }"""),
]

# the two static copies of the benefit sentence are only a no-JS fallback (render()
# rewrites them on boot), but a stale HK$1,300 sample in the file is a lie waiting
# for someone to read it. Recomputed for the new default: HK$100 at the 17% band.
BENEFIT_ZH_OLD = '"s2.benefit": "您的 HK$1,300 捐款可全數扣稅，享約 HK$182 – 221 稅務扣減；只需約 HK$1,079 – 1,118 實際支持，即可成就全額100%救盲力量。",'
BENEFIT_ZH_NEW = '"s2.benefit": "您的 HK$100 捐款可全數扣稅，享約 HK$14 – 17 稅務扣減；只需約 HK$83 – 86 實際支持，即可成就全額100%救盲力量。",'
BENEFIT_EN_OLD = '"s2.benefit": "Your HK$1,300 gift qualifies for full tax deduction (est. HK$182 \\u2013 221 relief), meaning just HK$1,079 \\u2013 1,118 net support delivers the full sight-saving impact.",'
BENEFIT_EN_NEW = '"s2.benefit": "Your HK$100 gift qualifies for full tax deduction (est. HK$14 \\u2013 17 relief), meaning just HK$83 \\u2013 86 net support delivers the full sight-saving impact.",'
BENEFIT_HTML_OLD = '<p class="benefit" id="benefit" data-i18n="s2.benefit">Your HK$1,300 gift qualifies for full tax deduction (est. HK$182 – 221 relief), meaning just HK$1,079 – 1,118 net support delivers the full sight-saving impact.</p>'
BENEFIT_HTML_NEW = '<p class="benefit" id="benefit" data-i18n="s2.benefit">Your HK$100 gift qualifies for full tax deduction (est. HK$14 – 17 relief), meaning just HK$83 – 86 net support delivers the full sight-saving impact.</p>'

EDITS += [
    ("default · zh benefit fallback recomputed for HK$100",
     BENEFIT_ZH_OLD, BENEFIT_ZH_NEW),
    ("default · en benefit fallback recomputed for HK$100",
     BENEFIT_EN_OLD, BENEFIT_EN_NEW),
    ("default · markup benefit fallback recomputed for HK$100",
     BENEFIT_HTML_OLD, BENEFIT_HTML_NEW),
]


def main():
    src = SRC.read_text(encoding="utf-8")
    if not BAK.exists():
        BAK.write_text(src, encoding="utf-8")
        print(f"backup -> {BAK.name}")
    out = src
    rows = []
    bad = []
    for label, old, new in EDITS:
        n = out.count(old)
        if n != 1:
            bad.append(f"{label}: found {n} occurrences of the source string")
            continue
        out = out.replace(old, new)
        rows.append((label, n))
    if bad:
        print("REFUSED — nothing written:")
        for b in bad:
            print("  " + b)
        return 1
    SRC.write_text(out, encoding="utf-8")
    print(f"{len(rows)}/{len(EDITS)} edits applied to embed/index.html")
    for label, _ in rows:
        print(f"  · {label}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
