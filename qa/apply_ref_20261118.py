#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Add the payment-reference field to the receipt form (18 Nov 2026).

Why: a QR donation happens inside the donor's own PayMe / AlipayHK app, so the
page never sees it. The receipt form has to carry the transaction reference or
the charity cannot match the claim to the money that arrived — and a receipt on
an unverified self-report is exactly what the receipt promise must not rest on.

Every replacement asserts that its old string occurs EXACTLY ONCE, so a string
that has already drifted (or appears twice, i.e. would land in two places) fails
the run instead of corrupting the file. Re-runnable from the .bak.

    python3 qa/apply_ref_20261118.py            # apply (writes a .bak first)
    python3 qa/apply_ref_20261118.py --check    # report without writing
"""
import shutil
import sys

SRC = "embed/index.html"
BAK = "embed/index.html.bak-pre-ref-20261118"
CHECK = "--check" in sys.argv

# ── markup ────────────────────────────────────────────────────────────────────
OLD_FIELDS = """      <div class="consent">
        <input id="consent" type="checkbox">"""

NEW_FIELDS = """      <div>
        <label for="rref" data-i18n="rc.ref">付款參考編號</label>
        <input id="rref" type="text" autocomplete="off" placeholder="例如 2026111800123"
               aria-describedby="rref-hint rref-msg" data-i18n-ph="rc.ref.ph">
        <p class="hint" id="rref-hint" style="margin:6px 0 0" data-i18n="rc.ref.hint">請填寫付款 App 交易紀錄或信用卡收據上的交易編號；我們憑此核對您的捐款，再發出正式收據。</p>
        <p class="msg" id="rref-msg" hidden></p>
      </div>
      <div class="consent">
        <input id="consent" type="checkbox">"""

# ── zh-HK strings ─────────────────────────────────────────────────────────────
ZH = [
    ('"rc.h": "需要扣稅收據？只需留下姓名及電郵。"',
     '"rc.h": "需要扣稅收據？留下姓名、電郵及付款參考編號。"'),
    ('"rc.lede": "我們只需收據抬頭及電郵，用以發出正式收據。課稅年度內捐款總額滿 HK$100，方可獲發正式收據。"',
     '"rc.lede": "我們需要收據抬頭、電郵，以及付款交易編號，用以核對您的捐款並發出正式收據。課稅年度內捐款總額滿 HK$100，方可獲發正式收據。"'),
    ('"rc.consent": "本人同意護瞳行動使用本人的姓名及電郵，以發出扣稅收據。"',
     '"rc.consent": "本人同意護瞳行動使用上述資料核對本人的捐款，並發出扣稅收據。"'),
    ('"rc.submit": "留下資料"', '"rc.submit": "提交收據申請"'),
    ('"rc.poc": "POC 示範：資料只保留於本測試頁的記憶體，不會傳送至任何伺服器，亦不會儲存。正式版將由 2SK 建立的收據系統接收，並依客戶指示傳送至其 CRM。"',
     '"rc.poc": "POC 示範：資料只保留於本測試頁的記憶體，不會傳送至任何伺服器，亦不會儲存。正式版將由 2SK 建立的收據系統接收（包括付款參考編號，供核對捐款之用），並依客戶指示傳送至其 CRM。"'),
    ('"d.rv.ok": "多謝您。我們會於您捐款後跟進發出收據（POC：尚未接駁後端）。"',
     '"d.rv.ok": "多謝您。我們會先核對您的付款，核對後發出扣稅收據（POC：尚未接駁後端）。"'),
]

# ── en strings ────────────────────────────────────────────────────────────────
EN = [
    ('"rc.h": "Need a tax receipt? Leave your name and email."',
     '"rc.h": "Need a tax receipt? Leave your name, email and payment reference."'),
    ('"rc.lede": "We need only the name for the receipt and an email address. A receipt is issued once your total for the year of assessment reaches HK$100."',
     '"rc.lede": "We need the name for the receipt, an email address, and the transaction reference from your payment, so we can match your gift before issuing the receipt. A receipt is issued once your total for the year of assessment reaches HK$100."'),
    ('"rc.consent": "I agree that the Fred Hollows Foundation may use my name and email to issue a tax receipt."',
     '"rc.consent": "I agree that the Fred Hollows Foundation may use the details above to match my donation and issue a tax receipt."'),
    ('"rc.submit": "Leave your details"', '"rc.submit": "Request my receipt"'),
    ('"rc.poc": "POC demo: what you type stays in this test page\'s memory. It is not sent anywhere and not stored. In the live build a receipt system built by 2SK receives it and passes it to the charity\'s CRM as they direct."',
     '"rc.poc": "POC demo: what you type stays in this test page\'s memory. It is not sent anywhere and not stored. In the live build a receipt system built by 2SK receives it — including the payment reference, which is used to match your gift — and passes it to the charity\'s CRM as they direct."'),
    ('"d.rv.ok": "Thank you. We will follow up with your receipt once the donation is in (POC: not connected to a backend yet)."',
     '"d.rv.ok": "Thank you. We will match your payment first, then issue the tax receipt (POC: not connected to a backend yet)."'),
]

# ── NEW keys, one per language ────────────────────────────────────────────────
ZH_NEW = '''    "rc.ref": "付款參考編號",
    "rc.ref.ph": "例如 2026111800123",
    "rc.ref.hint": "請填寫付款 App 交易紀錄或信用卡收據上的交易編號；我們憑此核對您的捐款，再發出正式收據。",
    "d.rv.ref": "請輸入付款交易編號（見付款 App 的交易紀錄）。",
'''
EN_NEW = '''    "rc.ref": "Payment reference",
    "rc.ref.ph": "e.g. 2026111800123",
    "rc.ref.hint": "The transaction ID shown in your payment app, or on your card receipt. We use it to match your donation before issuing the receipt.",
    "d.rv.ref": "Please enter the payment reference from your app or receipt.",
'''

ANCHOR_ZH = '    "rc.name.ph": "陳大文",\n'
ANCHOR_EN = '    "rc.name.ph": "Chan Tai Man",\n'

# ── disclaimer wording: the form now takes three things, not two ──────────────
DISC = [
    ("本計算機不會收集或儲存任何資料；您在本表格自願提供的姓名及電郵，只用作發出扣稅收據。",
     "本計算機不會收集或儲存任何資料；您在本表格自願提供的姓名、電郵及付款參考編號，只用於核對捐款及發出扣稅收據。"),
    ("The calculator itself collects and stores nothing; the name and email you choose to give in this form are used only to issue your tax receipt.",
     "The calculator itself collects and stores nothing; the name, email and payment reference you choose to give in this form are used only to match your donation and issue your tax receipt."),
]

# ── validation + event payload ────────────────────────────────────────────────
JS = [
    ('    var name = $("#rname").value.trim(), mail = $("#rmail").value.trim(), ok = true;\n'
     '    $("#rname-msg").hidden = $("#rmail-msg").hidden = true;',
     '    var name = $("#rname").value.trim(), mail = $("#rmail").value.trim(), ok = true;\n'
     '    /* the reference is the only thing that ties this claim to money that actually\n'
     '       arrived — a QR gift is invisible to this page, so without it the charity is\n'
     '       issuing a receipt on a self-report. Kept deliberately permissive: donors\n'
     '       will paste whatever their app shows them. */\n'
     '    var ref = $("#rref").value.trim().replace(/\\s+/g, " ");\n'
     '    $("#rname-msg").hidden = $("#rmail-msg").hidden = $("#rref-msg").hidden = true;'),
    ('    if (!$("#consent").checked)',
     '    if (ref.length < 4 || ref.length > 40) { $("#rref-msg").textContent = t("d.rv.ref"); $("#rref-msg").hidden = false; ok = false; }\n'
     '    if (!$("#consent").checked)'),
    ('    track("receipt_request", {method: "web_form", has_reference: "no"});',
     '    /* the reference itself never leaves the browser in the POC; only whether one\n'
     '       was given is reported, because a transaction ID is an identifier, not a metric */\n'
     '    track("receipt_request", {method: "web_form", has_reference: ref ? "yes" : "no"});'),
    ('  ["#rname","#rmail"].forEach(function(sel){ $(sel).addEventListener("input", scheduleHeight); });',
     '  ["#rname","#rmail","#rref"].forEach(function(sel){ $(sel).addEventListener("input", scheduleHeight); });'),
]


def one(data, old, new, label, want=1):
    n = data.count(old)
    if n != want:
        raise SystemExit(f"FAIL [{label}]: expected {want} occurrence(s), found {n}\n  {old[:90]}")
    return data.replace(old, new)


def main():
    html = open(SRC, encoding="utf-8").read()

    # guards: the two language tables must be distinguishable by their anchors
    if html.count(ANCHOR_ZH) != 1 or html.count(ANCHOR_EN) != 1:
        raise SystemExit("FAIL: language anchors not unique — refusing to guess which table is which")

    html = one(html, OLD_FIELDS, NEW_FIELDS, "markup: reference field")
    html = one(html, ANCHOR_ZH, ANCHOR_ZH + ZH_NEW, "zh: new keys")
    html = one(html, ANCHOR_EN, ANCHOR_EN + EN_NEW, "en: new keys")

    for i, (old, new) in enumerate(ZH + EN + JS):
        html = one(html, old, new, f"edit {i}: {old[:45]}")
    # the disclaimer sentence appears twice in zh (string table + static copy) and
    # once in en: both surfaces must move together or the JS-off view contradicts the table
    html = one(html, DISC[0][0], DISC[0][1], "zh disclaimer", want=2)
    html = one(html, DISC[1][0], DISC[1][1], "en disclaimer", want=1)

    # the zh and en tables must still hold the same number of keys
    import re
    def keys(block):
        return set(re.findall(r'^\s{4}"([a-zA-Z0-9._]+)":', block, re.M))
    if html.count('  "zh-HK": {') != 1 or html.count('  "en": {') != 1:
        raise SystemExit("FAIL: cannot locate the two string tables unambiguously")
    zh_block = html.split('  "zh-HK": {', 1)[1].split('  "en": {', 1)[0]
    en_block = html.split('  "en": {', 1)[1].split('  };', 1)[0]
    kz, ke = keys(zh_block), keys(en_block)
    missing_en, missing_zh = sorted(kz - ke), sorted(ke - kz)
    print("keys zh:", len(kz), "keys en:", len(ke))
    if missing_en or missing_zh:
        raise SystemExit(f"FAIL: key parity broken — missing in en: {missing_en} / missing in zh: {missing_zh}")

    if CHECK:
        print("CHECK OK — every replacement matched exactly once (nothing written)")
        return

    shutil.copyfile(SRC, BAK)
    open(SRC, "w", encoding="utf-8").write(html)
    print(f"applied → {SRC} (backup {BAK})")

    # before → after table for the record
    print("\n| # | change |")
    print("|---|---|")
    for i, (old, new) in enumerate(ZH + EN + DISC + JS, 1):
        print(f"| {i} | {old[:64]!r} → {new[:64]!r} |")


if __name__ == "__main__":
    main()
