#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Give the AlipayHK receipt tooltip an ENGLISH capture set, and fix the copy that
named Chinese labels.

The tooltip shipped with the client's own Chinese app screens for both locales,
and the English sentences deliberately kept the app labels in Chinese
(「需要收據」, 慈善捐款, 我的捐款, 捐款記錄, 申請收據) because that is what the donor
saw in the picture. Denise then sent the same six steps captured in the app's
English interface, so from now on:

  * the frame shows the crops for ITS OWN language — zh-Hant-HK keeps the six
    Chinese crops, en gets the six English ones (same 320px width, red highlight
    redrawn, transaction reference and amount masked — see
    qa/make_alipay_help_crops_en.py);
  * the English sentences name the labels that are actually on screen
    (Receipt request, Charity, Mine, Donation record), instead of a Chinese
    label the English reader can no longer find;
  * the outro stops saying "the app is shown in Chinese" on the English page.

One img element per step still: src and the pre-load aspect box are swapped
together from data-src-zh / data-src-en, because the Chinese and English crops
for the same step are different heights (213 vs 92 on step 1) and a stale
width/height pair distorts the panel until the file decodes.

Also: the income-range label said 年薪 ("annual salary") while the field takes
total income of any kind — the client's copy fix to 全年收入 lands here.

Run from the repo root:  python3 qa/apply_alipay_en_crops_20261127.py
"""
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HTML = ROOT / "embed" / "index.html"
VERIFY = ROOT / "qa" / "verify_live.py"
BAK = HTML.with_suffix(".html.bak-pre-alipay-en-crops-20261127")

src = HTML.read_bytes().decode("utf-8")
verify_src = VERIFY.read_bytes().decode("utf-8")
orig = src


def must(hay, needle, what):
    n = hay.count(needle)
    if n != 1:
        raise SystemExit(f"anchor {what!r}: found {n} times, expected 1 — already applied?")
    return hay.index(needle)


def sub(text, old, new, what):
    must(text, old, what)
    return text.replace(old, new, 1)


# ── 1 · language-specific image sources on the six crops ─────────────────────
IMGS = [
    ("alipay-receipt-o1-step-1", "320x213", "320x92"),
    ("alipay-receipt-o1-step-2", "320x452", "320x479"),
    ("alipay-receipt-o2-step-1", "320x370", "320x375"),
    ("alipay-receipt-o2-step-2", "320x239", "320x253"),
    ("alipay-receipt-o2-step-3", "320x207", "320x163"),
    ("alipay-receipt-o2-step-4", "320x88", "320x92"),
]
for zh, whz, whe in IMGS:
    key = f"{zh}.webp"
    i = must(src, key, "img src " + zh)
    start = src.rfind("<img", 0, i)
    end = src.index(">", i)
    en = zh.replace("alipay-receipt-", "alipay-receipt-en-")
    attrs = (f'\n                           data-src-zh="../assets/help/{zh}.webp?v=20261124b" '
             f'data-wh-zh="{whz}"'
             f'\n                           data-src-en="../assets/help/{en}.webp?v=20261127" '
             f'data-wh-en="{whe}"')
    src = src[:end] + attrs + src[end:]

# ── 2 · swap them on every language apply ────────────────────────────────────
src = sub(
    src,
    '    $$("[data-i18n-alt]").forEach(function(e){ e.setAttribute("alt", t(e.getAttribute("data-i18n-alt"))); });\n',
    '    $$("[data-i18n-alt]").forEach(function(e){ e.setAttribute("alt", t(e.getAttribute("data-i18n-alt"))); });\n'
    '    /* The receipt-help crops are the client\'s own app screens, so they exist\n'
    '       per language: the Chinese build for zh-Hant-HK, the English interface\n'
    '       for en. src and the pre-load aspect box move together, or the panel is\n'
    '       distorted until the file decodes (the same step is 213px tall in\n'
    '       Chinese and 92px in English). */\n'
    '    $$("[data-src-zh]").forEach(function(e){\n'
    '      var k = (L === "en") ? "en" : "zh";\n'
    '      var s = e.getAttribute("data-src-" + k);\n'
    '      var d = (e.getAttribute("data-wh-" + k) || "").split("x");\n'
    '      if (s && e.getAttribute("src") !== s) e.setAttribute("src", s);\n'
    '      if (d.length === 2) { e.setAttribute("width", d[0]); e.setAttribute("height", d[1]); }\n'
    '    });\n',
    "applyLang image swap",
)

# ── 3 · the block comment above the trigger, now only half true ──────────────
src = sub(
    src,
    """                 The crops are the client's own donor-side screens at 320x529 (67 KB
                 for all six). AlipayHK's UI is Chinese, which is why the app labels
                 stay in Chinese inside the English sentences — a donor matches what
                 they see — and why the outro says the interface is Chinese. -->""",
    """                 The crops are the client's own donor-side screens, 320 wide, in
                 BOTH app languages: the Chinese set (24 Nov) for zh-Hant-HK and the
                 English set Denise captured (27 Nov) for en. Each frame shows its own
                 language's crops via data-src-zh / data-src-en, and the English
                 sentences therefore name the English labels (Receipt request,
                 Charity, Mine, Donation record) instead of Chinese ones the English
                 reader cannot find on screen. The English crops carry the same
                 treatment as the Chinese: red highlight redrawn, transaction
                 reference and gift amount masked (qa/make_alipay_help_crops_en.py). -->""",
    "crop comment block",
)

# ── 4 · English sentences that named Chinese labels ─────────────────────────
EN_STRINGS = [
    ('"s3.rcpt.o1.s1": "Tick 「需要收據」 (need a receipt) under the amount.",',
     '"s3.rcpt.o1.s1": "Tick Receipt request under the amount.",'),
    ('"s3.rcpt.o1.s2": "The donor form appears — name in English, email, phone. Fill it in, then confirm the gift.",',
     '"s3.rcpt.o1.s2": "The Donor information form appears — name in English, email, phone. Fill it in, then confirm the gift.",'),
    ('"s3.rcpt.o2.s1": "Open AlipayHK and go to 慈善捐款.",',
     '"s3.rcpt.o2.s1": "Open AlipayHK and go to Charity.",'),
    ('"s3.rcpt.o2.s2": "Tap 我的捐款 at the bottom, then 捐款記錄.",',
     '"s3.rcpt.o2.s2": "Tap Mine at the bottom, then Donation record.",'),
    ('"s3.rcpt.o2.s4": "Tap 申請收據 and submit your details.",',
     '"s3.rcpt.o2.s4": "Tap Receipt request and submit your details.",'),
    ('"s3.rcpt.o1.alt1": "AlipayHK donation detail screen: the charity, the suggested amounts and, at the foot, the unticked 「需要收據」 box",',
     '"s3.rcpt.o1.alt1": "AlipayHK donation detail screen with the Variable Amount row and, below it, the unticked Receipt request box",'),
    ('"s3.rcpt.o1.alt2": "The same screen with 「需要收據」 ticked and the 「捐款人資料」 form open below it: name in English, email, phone and address",',
     '"s3.rcpt.o1.alt2": "The same screen with Receipt request ticked and the Donor information form open below it: name in English, receipt header, email, phone and postal address, all still blank",'),
    ('"s3.rcpt.o2.alt1": "AlipayHK home screen with 慈善捐款 in the shortcut grid, fourth in the first row",',
     '"s3.rcpt.o2.alt1": "AlipayHK home screen with Charity in the shortcut grid, fourth in the first row",'),
    ('"s3.rcpt.o2.alt2": "The 慈善捐款 page with its menu of donation options, including the 捐款記錄 row",',
     '"s3.rcpt.o2.alt2": "The Mine menu listing Donor Profile, My e-Flag, Monthly donation management, Fiscal year summary, Donation record and User Guide",'),
    ('"s3.rcpt.o2.alt3": "The 交易記錄 list showing one gift to 護瞳行動 with its date and amount",',
     '"s3.rcpt.o2.alt3": "The Transaction record list showing one gift to The Fred Hollows Foundation with its date",'),
    ('"s3.rcpt.o2.alt4": "The 捐款結果 screen with the blue 申請收據 button at the foot, above the return link",',
     '"s3.rcpt.o2.alt4": "The donation result screen with the blue Receipt request button, above the Back to Charity page link",'),
    ('"s3.rcpt.outro": "The app is shown in Chinese; the buttons sit in the same place on your screen.",',
     '"s3.rcpt.outro": "These screens are from AlipayHK\'s English interface; your buttons sit in the same place.",'),
]
for old, new in EN_STRINGS:
    src = sub(src, old, new, old.split('"')[1])

# ── 5 · 年薪 → 全年收入 (income of any kind, not salary) ─────────────────────
src = sub(src,
          '"s1.band.label": "請選擇您的收入範圍或輸入您的年薪",',
          '"s1.band.label": "請選擇您的收入範圍或輸入您的全年收入",',
          "s1.band.label")
src = sub(src,
          '"s1.band.aria": "請選擇您的收入範圍或輸入您的年薪",',
          '"s1.band.aria": "請選擇您的收入範圍或輸入您的全年收入",',
          "s1.band.aria")
verify_src = sub(verify_src,
                 '"Section 2 heading (zh)": "請選擇您的收入範圍或輸入您的年薪",',
                 '"Section 2 heading (zh)": "請選擇您的收入範圍或輸入您的全年收入",',
                 "verify_live heading")

# ── 6 · write, with a backup of the pre-change file ─────────────────────────
if not BAK.exists():
    shutil.copy2(HTML, BAK)
HTML.write_bytes(src.encode("utf-8"))
VERIFY.write_bytes(verify_src.encode("utf-8"))

print(f"backup  {BAK.name}")
print(f"chars   {len(orig)} -> {len(src)}")
print("\nchange list")
for zh, whz, whe in IMGS:
    print(f"  img {zh:26s} +data-src-en  zh {whz:8s} en {whe}")
print(f"  js  applyLang            +{len(IMGS)} lang-aware sources")
print(f"  copy                     {len(EN_STRINGS)} English strings de-Sinicised")
print("  copy                     s1.band.label + s1.band.aria → 全年收入")
print("  qa                       verify_live.py heading assertion updated")
