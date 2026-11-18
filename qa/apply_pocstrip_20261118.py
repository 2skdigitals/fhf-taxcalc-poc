#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Strip POC chrome and fake payment assets from the widget (18 Nov 2026).

What this removes, and why it is safe:
  · the POC bar and the "POC test mode" badge — they were scaffolding, not page content
  · the two test QR figures and every caption that called them test codes — a QR that
    nobody can pay is worse than no QR: it looks live and does nothing
  · the "App open test (POC)" deep-link panel — an internal bench control on a client page
  · the receipt block's POC paragraph and the "(POC: not connected…)" parenthetical
  · sticky static strings that still carried the pre-payment-reference copy, so the page
    reads correctly even before the language layer runs

What it does NOT do: touch the tax engine, the events, the receipt validation, or any
fact a donor or the client's legal team relies on. Copy tightening and visual design are
a separate, reviewed pass.

    python3 qa/apply_pocstrip_20261118.py --check
    python3 qa/apply_pocstrip_20261118.py
"""
import re
import shutil
import sys

SRC = "embed/index.html"
BAK = "embed/index.html.bak-pre-pocstrip-20261118"
CHECK = "--check" in sys.argv

EDITS = []


def add(old, new, want=1, label=""):
    EDITS.append((old, new, want, label))


# ── 1 · the payment block: no badge, no note about becoming live, rails point out ──
add('''    <span class="badge"><span class="dot"></span><span style="display:contents" data-i18n-html="s3.badge">POC 測試 <span style="opacity:.6">test mode</span></span></span>
    <p class="note" style="margin:0 0 14px" data-i18n="s3.note">PayMe 及 AlipayHK 以二維碼於您自己的 App 內完成；信用卡則前往護瞳行動現有的捐款頁。正式上線時會換成客戶提供的商戶碼。</p>
''', '', 1, "poc badge + note")

# ── 2 · the two test QR figures and the block that explained how to scan them ──
add('''    <div class="qr-grid">
      <figure class="qr-fig">
        <img id="qr-payme" src="../assets/qr-payme.svg" alt="PayMe 測試二維碼（POC，非真實收款碼）" width="150" height="150" data-i18n-alt="s3.qr.alt.payme">
        <figcaption><span data-i18n="s3.qr.payme">PayMe 二維碼</span><span class="poc" data-i18n="s3.qr.poc">POC 測試碼</span></figcaption>
      </figure>
      <figure class="qr-fig">
        <img id="qr-alipay" src="../assets/qr-alipay.svg" alt="AlipayHK 測試二維碼（POC，非真實收款碼）" width="150" height="150" data-i18n-alt="s3.qr.alt.alipay">
        <figcaption><span data-i18n="s3.qr.alipay">AlipayHK 二維碼</span><span class="poc" data-i18n="s3.qr.poc">POC 測試碼</span></figcaption>
      </figure>
    </div>

    <div class="qr-copy">
      <div class="qr-desk">
        <h3 data-i18n="s3.qr.desk.h">用手機掃描二維碼捐款</h3>
        <p data-i18n-html="s3.qr.desk.p">請以另一部手機的相機或付款 App 掃描，然後輸入 <strong class="qr-amount">HK$1,300</strong>。</p>
      </div>
      <div class="qr-mob">
        <h3 data-i18n="s3.qr.mob.h">以手機捐款：長按二維碼，分享至付款 App</h3>
        <p data-i18n-html="s3.qr.mob.p">長按上方<strong>對應的</strong>二維碼儲存圖片（每個 App 一個碼），再開啟 <b>PayMe</b> 或 <b>AlipayHK</b>，使用該 App 內的「掃描」或「相簿」功能選取該二維碼，然後輸入 <strong class="qr-amount">HK$1,300</strong>。</p>
      </div>
      <p class="fine" data-i18n="s3.qr.fine">二維碼為靜態碼，本身不包含金額，須於付款 App 內自行輸入金額。</p>
    </div>

    <div class="field" id="deeplink-test" style="border-top:1px solid var(--line);padding-top:12px;margin-top:14px">
      <p class="hint" style="margin:0 0 8px" data-i18n-html="s3.dl.hint"><b>App 開啟測試（POC）：</b>點按下方按鈕，測試 iframe 內能否開啟付款 App。正式版將採用商戶提供的 deep link。</p>
      <div class="chips">
        <button type="button" data-deeplink="payme" data-i18n="s3.dl.payme">測試叫起 PayMe</button>
        <button type="button" data-deeplink="alipay" data-i18n="s3.dl.alipay">測試叫起 AlipayHK</button>
      </div>
      <p class="hint" id="deeplink-msg" aria-live="polite"></p>
    </div>
''', '''    <!-- Merchant QR panel returns here when the charity supplies the PayMe and AlipayHK
         merchant codes. Until then the two wallet rails open the charity's own giving page,
         so every route on this block works. -->
''', 1, "test QR grid + scan copy + deeplink bench")

# ── 3 · the two wallet rails now link out instead of selecting an empty QR panel ──
add('''      <button class="rail" type="button" data-rail="payme">
        <span class="nm">PayMe</span>
        <span class="sub"><span class="qr-desk" data-i18n="s3.payme.desk">用手機掃描下方二維碼完成捐款</span><span class="qr-mob" data-i18n="s3.payme.mob">長按下方二維碼儲存，並於 PayMe 內完成捐款</span></span>
        <span class="go" aria-hidden="true">→</span>
      </button>
      <button class="rail" type="button" data-rail="alipay">
        <span class="nm">AlipayHK</span>
        <span class="sub"><span class="qr-desk" data-i18n="s3.alipay.desk">用手機掃描下方二維碼完成捐款</span><span class="qr-mob" data-i18n="s3.alipay.mob">長按下方二維碼儲存，並於 AlipayHK 內完成捐款</span></span>
        <span class="go" aria-hidden="true">→</span>
      </button>''', '''      <a href="https://www.hollows.org/zh-Hant-HK/ways-to-support/ways-to-give/" target="_top" rel="noopener" data-rail="payme">
        <span class="nm">PayMe</span>
        <span class="sub" data-i18n="s3.payme.sub">於護瞳行動捐款頁以 PayMe 完成捐款</span>
        <span class="go" aria-hidden="true">↗</span>
      </a>
      <a href="https://www.hollows.org/zh-Hant-HK/ways-to-support/ways-to-give/" target="_top" rel="noopener" data-rail="alipay">
        <span class="nm">AlipayHK</span>
        <span class="sub" data-i18n="s3.alipay.sub">於護瞳行動捐款頁以 AlipayHK 完成捐款</span>
        <span class="go" aria-hidden="true">↗</span>
      </a>''', 1, "wallet rails → links")

# ── 4 · the receipt block: no POC paragraph, and the static strings catch up ──
# the receipt POC paragraph is located by its i18n key: its static text and its table
# string legitimately differ, so matching the prose would fail on whichever copy drifted
POC_P_RE = r'\n\s*<p class="fine" data-i18n="rc\.poc">[\s\S]*?</p>' 

add('<h2 id="rch" style="font-size:1.05rem" data-i18n="rc.h">需要扣稅收據？只需留下姓名及電郵。</h2>',
    '<h2 id="rch" style="font-size:1.05rem" data-i18n="rc.h">需要扣稅收據？留下姓名、電郵及付款參考編號。</h2>', 1, "static rch")
add('<p class="lede" style="margin-bottom:14px" data-i18n="rc.lede">我們只需收據抬頭及電郵，用以發出正式收據。課稅年度內捐款總額滿 HK$100，方可獲發正式收據。</p>',
    '<p class="lede" style="margin-bottom:14px" data-i18n="rc.lede">我們需要收據抬頭、電郵，以及付款交易編號，用以核對您的捐款並發出正式收據。課稅年度內捐款總額滿 HK$100，方可獲發正式收據。</p>', 1, "static rc.lede")
add('<label for="consent" data-i18n="rc.consent">本人同意護瞳行動使用本人的姓名及電郵，以發出扣稅收據。</label>',
    '<label for="consent" data-i18n="rc.consent">本人同意護瞳行動使用上述資料核對本人的捐款，並發出扣稅收據。</label>', 1, "static consent")
add('<button class="btn" type="submit" id="rsubmit" data-i18n="rc.submit">留下資料</button>',
    '<button class="btn" type="submit" id="rsubmit" data-i18n="rc.submit">提交收據申請</button>', 1, "static submit")

# the English static fallbacks (the page ships zh first, but keep them honest too)
add('data-i18n="rc.h">Need a tax receipt? Leave your name and email.</h2>',
    'data-i18n="rc.h">Need a tax receipt? Leave your name, email and payment reference.</h2>', 0, "skip")

# ── 4b · the page titles carried a POC marker (the browser tab is client-visible) ──
add('"title": "慈善捐款扣稅計算機 — POC"', '"title": "慈善捐款扣稅計算機"', 1, "zh title")
add('"title": "Donation tax calculator — POC"', '"title": "Donation tax calculator"', 1, "en title")

# ── 4c · a code comment is not donor-visible, but the sweep reads it as a leftover ──
add('/* receipt capture (POC: memory only) */', '/* receipt capture: this build keeps the form in page memory only */', 1, "js comment")

# ── 5 · the two strings that carried a (POC: …) parenthetical ──
add('"d.rv.ok": "多謝您。我們會先核對您的付款，核對後發出扣稅收據（POC：尚未接駁後端）。"',
    '"d.rv.ok": "多謝您。我們會先核對您的付款，核對後發出扣稅收據。"', 1, "zh d.rv.ok")
add('"d.rv.ok": "Thank you. We will match your payment first, then issue the tax receipt (POC: not connected to a backend yet)."',
    '"d.rv.ok": "Thank you. We will match your payment first, then issue the tax receipt."', 1, "en d.rv.ok")

# ── 6 · payment intro + wallet sub-copy, both languages ──
add('"s3.lede": "PayMe、AlipayHK 二維碼，以及前往護瞳行動網站的信用卡。"',
    '"s3.lede": "PayMe、AlipayHK 及信用卡，全部於護瞳行動的捐款頁完成。"', 1, "zh s3.lede")
add('"s3.lede": "PayMe and AlipayHK QR codes, and a credit card that takes you to the Fred Hollows Foundation site."',
    '"s3.lede": "PayMe, AlipayHK or a credit card — all completed on the Foundation\'s donation page."', 1, "en s3.lede")

add('"s3.payme.desk": "用手機掃描下方二維碼完成捐款",',
    '"s3.payme.sub": "於護瞳行動捐款頁以 PayMe 完成捐款",', 1, "zh payme sub")
add('"s3.payme.desk": "Scan the QR code below on your phone to give",',
    '"s3.payme.sub": "Give by PayMe on the Foundation\'s donation page",', 1, "en payme sub")
add('"s3.alipay.desk": "用手機掃描下方二維碼完成捐款",',
    '"s3.alipay.sub": "於護瞳行動捐款頁以 AlipayHK 完成捐款",', 1, "zh alipay sub")
add('"s3.alipay.desk": "Scan the QR code below on your phone to give",',
    '"s3.alipay.sub": "Give by AlipayHK on the Foundation\'s donation page",', 1, "en alipay sub")


def main():
    html = open(SRC, encoding="utf-8").read()
    applied, skipped = 0, 0
    removed_keys = {}
    for old, new, want, label in EDITS:
        n = html.count(old)
        if want == 0:
            skipped += 1
            continue
        if n != want:
            raise SystemExit(f"FAIL [{label}]: expected {want}, found {n}\n  {old[:100]}")
        html = html.replace(old, new)
        applied += 1

    # the POC bar sits at the top of the manifest of scaffolding
    html, n_bar = re.subn(r'\n?<div class="pocbar"[\s\S]*?</div>\n', '\n', html, count=1)
    if n_bar != 1:
        raise SystemExit(f"FAIL: POC bar not found (n={n_bar})")

    html, n_p = re.subn(POC_P_RE, '', html, count=1)
    if n_p != 1:
        raise SystemExit(f"FAIL: receipt POC paragraph not found (n={n_p})")

    # the two keys that no longer have an element must not linger in the tables
    for key in ("s3.payme.desk", "s3.payme.mob", "s3.alipay.desk", "s3.alipay.mob",
                "s3.badge", "s3.note", "s3.qr.payme", "s3.qr.alipay", "s3.qr.poc",
                "s3.qr.alt.payme", "s3.qr.alt.alipay", "s3.qr.desk.h", "s3.qr.desk.p",
                "s3.qr.mob.h", "s3.qr.mob.p", "s3.qr.fine", "s3.dl.hint", "s3.dl.payme",
                "s3.dl.alipay", "rc.poc", "poc.demo"):
        # a key may sit in one table or both (some strings are language-specific markup),
        # so any count is legal; parity is asserted once, after the whole sweep
        key_pat = re.compile(r'\n\s*"' + re.escape(key) + r'": "(?:[^"\\]|\\.)*",')
        html, k = key_pat.subn("", html)
        removed_keys[key] = k

    leftovers = [t for t in ("POC 測試", "POC 測試碼", "test mode", "POC test", "非真實收款碼",
                             "(POC:", "POC demo", "POC 示範") if t in html]
    if leftovers:
        raise SystemExit(f"FAIL: POC chrome still present: {leftovers}")

    # key parity between the two tables
    def keys(block):
        return set(re.findall(r'^\s{4}"([a-zA-Z0-9._]+)":', block, re.M))
    if html.count('  "zh-HK": {') != 1 or html.count('  "en": {') != 1:
        raise SystemExit("FAIL: cannot locate the string tables")
    kz = keys(html.split('  "zh-HK": {', 1)[1].split('  "en": {', 1)[0])
    ke = keys(html.split('  "en": {', 1)[1].split('  };', 1)[0])
    if kz != ke:
        raise SystemExit(f"FAIL: key parity broken. only-zh={sorted(kz-ke)} only-en={sorted(ke-kz)}")
    print(f"keys: {len(kz)} per language, parity ok")

    print(f"edits applied: {applied} (+POC bar); orphaned keys removed: "
          + ", ".join(f"{k}×{v}" for k, v in sorted(removed_keys.items()) if v))
    if CHECK:
        print("CHECK OK — nothing written")
        return
    shutil.copyfile(SRC, BAK)
    open(SRC, "w", encoding="utf-8").write(html)
    print(f"applied → {SRC} (backup {BAK})")


if __name__ == "__main__":
    main()
