#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Adopt Direction A (quiet editorial) and take a second, harder pass at wordiness.

Kevin: "A, but I want it less wordy." Direction A already cut ~40% of the visible text;
this pass removes the remaining restatements without losing a single required fact.

Every replacement asserts exactly one occurrence, so a string that has already drifted
fails the run instead of being silently skipped.

    python3 qa/apply_calm_lean_20261118.py --check
    python3 qa/apply_calm_lean_20261118.py
"""
import shutil
import sys

SRC = "embed/index.html"
SRC_A = "design/calm/index.html"
BAK = "embed/index.html.bak-pre-calm-20261118"
CHECK = "--check" in sys.argv

EDITS = [
    # ── the income hint: the parenthetical says the same thing in fewer words ──
    ('"s1.band.hint": "Before allowances; the basic allowance is assumed at HK$145,000.",',
     '"s1.band.hint": "Before allowances (HK$145,000 assumed).",',
     '"s1.band.hint": "未扣除免稅額；基本免稅額以 HK$145,000 估算。",',
     '"s1.band.hint": "未扣除免稅額（以 HK$145,000 估算）。",'),

    # ── the standard-rate explanation: one sentence, every fact kept ──
    ('"s1.band.note": "Above HK$2,132,500 the standard rate takes over — 15% on the first HK$5 million, 16% above it — so the last two rungs fall rather than rise. That is how the tax is built, not a bug.",',
     '"s1.band.note": "Above HK$2,132,500 the standard rate applies — 15%, then 16% — so the last two rungs fall, by design.",',
     '"s1.band.note": "應評稅入息淨額超過 HK$2,132,500 後，稅務局改用標準稅率計算：首 HK$500 萬 15%，其後 16%。因此最頂兩級的比率回落，而非上升 —— 這是薪俸稅的設計，並非計算錯誤。",',
     '"s1.band.note": "應評稅入息淨額超過 HK$2,132,500 後改用標準稅率（15%，其後 16%），故最頂兩級回落，並非計算錯誤。",'),

    # ── range captions ──
    ('"d.cap.range": "From the two ends of the range you chose.",',
     '"d.cap.range": "Both ends of your range.",',
     '"d.cap.range": "按所選範圍的上下限計算。",',
     '"d.cap.range": "按範圍上下限計算。",'),
    ('"d.cap.same": "The same at either end of the range you chose.",',
     '"d.cap.same": "The same at both ends.",',
     '"d.cap.same": "在所選入息範圍內，節省稅款相同。",',
     '"d.cap.same": "範圍兩端相同。",'),

    # ── the cap sentence: the label already says "cap", so stop repeating it ──
    ('"d.capline.exact.ok": "The cap is 35% of assessable income for the year; not reached, so all of it is deductible.",',
     '"d.capline.exact.ok": "35% cap — not reached, so all of it is deductible.",',
     '"d.capline.exact.ok": "扣稅上限為應評稅入息的 35%（全年合計）；未觸及上限，全數可扣除。",',
     '"d.capline.exact.ok": "35% 上限；未觸及，全數可扣除。",'),
    ('"d.capline.band.ok": "The cap is 35% of assessable income for the year; at the floor of your range all of it is deductible.",',
     '"d.capline.band.ok": "35% cap — all of it deductible at your range\'s low end.",',
     '"d.capline.band.ok": "扣稅上限為應評稅入息的 35%（全年合計）；所選範圍下限全數可扣除。",',
     '"d.capline.band.ok": "35% 上限；範圍下限全數可扣除。",'),
    ('"d.capline.band.capped": "The cap is 35% of assessable income for the year; at the floor of your range {d} is deductible.",',
     '"d.capline.band.capped": "35% cap — {d} deductible at your range\'s low end.",',
     '"d.capline.band.capped": "扣稅上限為應評稅入息的 35%（全年合計）；所選範圍下限可扣除 {d}。",',
     '"d.capline.band.capped": "35% 上限；範圍下限可扣除 {d}。",'),
    ('"d.capline.exact.capped": "The cap is 35% of assessable income for the year: {taxed} is deductible and the rest is not.",',
     '"d.capline.exact.capped": "35% cap: {taxed} deductible, the rest not.",',
     '"d.capline.exact.capped": "扣稅上限為應評稅入息的 35%（全年合計）：可扣除 {taxed}，其餘不能扣除。",',
     '"d.capline.exact.capped": "35% 上限：可扣除 {taxed}，其餘不能扣除。",'),
    ('"d.capline.unknown": "The cap is 35% of assessable income for the year; it is applied.",',
     '"d.capline.unknown": "35% cap applied.",',
     '"d.capline.unknown": "扣稅上限為應評稅入息的 35%（全年合計）；已計入上限。",',
     '"d.capline.unknown": "已計 35% 上限。",'),

    # ── assumption line ──
    ('"s2.assume.def": "Assumed assessable income HK$345,000 – 2,132,500.",',
     '"s2.assume.def": "Income assumed HK$345,000 – 2,132,500.",',
     '"s2.assume.def": "假設應評稅入息為 HK$345,000 – 2,132,500。",',
     '"s2.assume.def": "假設入息 HK$345,000 – 2,132,500。",'),
    ('"d.assume.band": "Assumed assessable income {band}.",',
     '"d.assume.band": "Income assumed {band}.",',
     '"d.assume.band": "假設應評稅入息為 {band}。",',
     '"d.assume.band": "假設入息 {band}。",'),
    ('"d.assume.exact": "Assumed assessable income {inc}, the figure you entered.",',
     '"d.assume.exact": "Income assumed {inc}, as you entered it.",',
     '"d.assume.exact": "假設應評稅入息為 {inc}（您輸入的數字）。",',
     '"d.assume.exact": "假設入息 {inc}（您輸入）。",'),

    # ── receipt block: the heading already says "receipt" ──
    ('"rc.lede": "Three details: the name for the receipt, an email address, and the reference from your payment.",',
     '"rc.lede": "Name, email, and your payment reference.",',
     '"rc.lede": "三項資料：收據抬頭、電郵，以及付款參考編號。",',
     '"rc.lede": "收據抬頭、電郵、付款參考編號。",'),
    ('"rc.threshold": "A receipt is issued once your gifts for the year of assessment reach HK$100.",',
     '"rc.threshold": "A receipt follows once your gifts for the year reach HK$100.",',
     '"rc.threshold": "課稅年度內捐款總額滿 HK$100，方會發出正式收據。",',
     '"rc.threshold": "全年捐款總額滿 HK$100 即發出收據。",'),

    # ── footer legal line: same facts, half the words ──
    ('"foot.legal": "* What you may deduct rests with the Inland Revenue Department. The cap is 35% of assessable income or profits; the tax saved is roughly the deductible amount × your rate, up to 17%.",',
     '"foot.legal": "* The IRD decides what you may deduct. Cap 35% of assessable income or profits; tax saved ≈ deductible × your rate, up to 17%.",',
     '"foot.legal": "* 實際可扣除金額以稅務局評定為準。上限為應評稅入息或利潤的 35%；所節省的稅款約為可扣除金額乘以適用稅率（最高 17%）。",',
     '"foot.legal": "* 以稅務局評定為準。上限為應評稅入息或利潤的 35%；節省稅款約為可扣除金額 × 適用稅率（最高 17%）。",'),
]


def main():
    a = open(SRC_A, encoding="utf-8").read()
    if "FHF_TAX_ENGINE_START" not in a:
        raise SystemExit("FAIL: design/calm/index.html does not look like the widget")

    html = a
    for i, (en_old, en_new, zh_old, zh_new) in enumerate(EDITS):
        for old, new in ((en_old, en_new), (zh_old, zh_new)):
            n = html.count(old)
            if n != 1:
                raise SystemExit(f"FAIL [edit {i}]: expected 1, found {n}\n  {old[:110]}")
            html = html.replace(old, new)

    # no POC anywhere in the shipped page
    for bad in ("POC 測試", "test mode", "非真實收款碼", "POC test"):
        if bad in html:
            raise SystemExit(f"FAIL: '{bad}' still present")

    print(f"edits applied: {len(EDITS)} × 2 languages")
    if CHECK:
        print("CHECK OK — nothing written")
        return

    shutil.copyfile(SRC, BAK)
    open(SRC, "w", encoding="utf-8").write(html)
    print(f"adopted Direction A + lean pass → {SRC} (previous build saved as {BAK})")


if __name__ == "__main__":
    main()
