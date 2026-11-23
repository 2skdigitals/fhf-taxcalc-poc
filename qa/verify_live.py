#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verify the DEPLOYED widget, not the local file.

A push is not a deploy and a 200 is not the build you shipped: GitHub Pages caches
HTML for ~10 minutes, and a catch-all can return 200 with the wrong body. So this
fetches the live document and asserts the markers this pass introduced, then
renders the live URL in a browser and reads the numbers out of the live DOM.

  python3 qa/verify_live.py
  python3 qa/verify_live.py --base https://2skdigitals.github.io/fhf-taxcalc-poc
"""
import re
import sys
import urllib.request

from playwright.sync_api import sync_playwright

BASE = "https://2skdigitals.github.io/fhf-taxcalc-poc"
ARGS = sys.argv[1:]
for i, a in enumerate(ARGS):
    if a == "--base" and i + 1 < len(ARGS):
        BASE = ARGS[i + 1].rstrip("/")

ok = bad = 0


def check(label, errs, detail=""):
    global ok, bad
    if errs:
        bad += 1
        print(f"FAIL  {label}")
        for e in errs:
            print("        ", e)
    else:
        ok += 1
        print(f"PASS  {label}" + (f"   {detail}" if detail else ""))


def fetch(path):
    url = f"{BASE}{path}"
    req = urllib.request.Request(url, headers={"Cache-Control": "no-cache",
                                               "User-Agent": "fhf-verify/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.status, r.read().decode("utf-8"), url


def fetch_status(path):
    """HTTP status of an asset, without decoding it — the screencaps are JPEG."""
    url = f"{BASE}{path}"
    req = urllib.request.Request(url, headers={"Cache-Control": "no-cache",
                                               "User-Agent": "fhf-verify/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, len(r.read())
    except Exception as e:                                     # noqa: BLE001
        return f"error {e}", 0


def strip_comments(s):
    """The document with its comments removed, for the MUST_NOT scan.

    Three of the strings this file bans are also its own record of why they are
    banned: the CSS still says `was color:var(--orange-ink)`, the help-panel
    comment names the merchant console as "PayMe for Business app", and the
    removed chips are described as "quick-amount" in prose. A byte scan that
    cannot tell a comment from a control reports a regression that is a
    sentence — so comments are stripped before the absence check, and the
    markers check above still runs against the raw bytes.
    """
    s = re.sub(r"/\*.*?\*/", " ", s, flags=re.S)      # CSS and JS block comments
    s = re.sub(r"<!--.*?-->", " ", s, flags=re.S)     # HTML comments
    s = re.sub(r"(?m)^\s*//.*$", " ", s)              # JS line comments
    return s


# ── 1 · the shipped document ─────────────────────────────────────────────────
status, body, url = fetch("/embed/?part=all&lang=en")
print(f"GET {url} → HTTP {status}, {len(body)} bytes\n")
check("the live combined URL answers 200", [] if status == 200 else [f"status {status}"])

# ── 1a · the served BYTES are the file in this working tree ──────────────────
# A 200 and a matching marker only prove *a* build is being served. The hash
# proves it is this one: GitHub Pages serves the file verbatim, so the two must
# be identical, not merely similar.
import hashlib
import pathlib
LOCAL = pathlib.Path(__file__).resolve().parent.parent / "embed" / "index.html"
local_bytes = LOCAL.read_bytes()
local_sha = hashlib.sha256(local_bytes).hexdigest()
served_sha = hashlib.sha256(body.encode("utf-8")).hexdigest()
check("the served document is byte-identical to embed/index.html",
      [] if served_sha == local_sha else [f"served {served_sha[:16]} != local {local_sha[:16]}"],
      f"sha256 {local_sha[:16]}…  {len(local_bytes)} bytes")

MUST = {
    "white ground token": "--ground:#fff;",
    # 23 Nov (client call): the column is the Foundation's own 1,280px component width.
    "1280px column": ".wrap{max-width:80rem",
    "18px body at 1.56": "font-size:var(--t-body);line-height:1.56;",
    "32px block heading": "--t-h:clamp(1.5rem,3.6vw,2rem)",
    "the HK$100 default": 'autocomplete="off" value="100"',
    "the HK$145,000 exact-income default": 'value="145,000"',
    "the exact swap adopts its starting value": "st.exact = digits(ex0.value)",
    "the two-rail desktop grid": "grid-template-columns:repeat(2,minmax(0,1fr))",
    "the AlipayHK QR tile": "../assets/logos/alipayhk.png",
    "the credit-card tile": 'data-rail="card"',
    "the payment lede names both rails that are left":
        "Scan the AlipayHK code with your phone, or pay by credit card on the Foundation's donation page.",
    "the HK$100 floor line": "Donation amount at HK$100 or above will receive tax deduction receipt",
    "the floor note element": 'id="min-note"',
    "the floor hint on the field": 'id="gift-min"',
    "?part=all in the part map": 'all:     ["calculator","result","payment","receipt"]',
    "all sections shown": 'body[data-part="all"] #calculator',
    "positive saving (no minus in markup)": '<dd id="saved">HK$14 至 HK$17</dd>',
    "the client's disclaimer line 1": "Based on IRD tax rates and info for the relevant assessment year; "
                                      "for general reference only.",
    "the client's disclaimer line 5": "The Fred Hollows Foundation (HK) Limited assumes no liability for "
                                      "use or reliance.",
    "the client's Chinese disclaimer": "護瞳行動（香港）有限公司概不承擔相關法律責任。",
    # 23 Nov: the design review pass. These four strings only exist in the file
    # that was built — a cached copy of the previous deployment cannot have them.
    "the 4px spacing scale": "--s2:8px; --s3:12px; --s4:16px; --s5:20px; --s6:24px; --s7:32px;",
    "the em measure": "--measure:34em;",
    "the heading/card separation": ".card + .step{margin-top:var(--s6)}",
    "the form's single rhythm": ".rform > *{margin-top:0}",
    # 23 Nov: the client's section-by-section copy sheet.
    "Section 1 heading (zh)": "請選擇並輸入您的捐款金額",
    "Section 1 heading (en)": "Please select and input your donation amount",
    "Section 2 heading (zh)": "請選擇您的收入範圍或輸入您的年薪",
    "Section 2 heading (en)": "Please select your income range or input your yearly income",
    "the single-allowance hint (en)": "Estimated based on a single person’s basic allowance of HK$145,000",
    "the exact-income link": "Enter exact income instead",
    "the CTA": "Check the calculation result",
    "Section 3 heading (zh)": "捐款扣稅計算結果",
    "Section 3 heading (en)": "Tax Deduction Summary",
    "the donation label": "您的全額捐款",
    "the brand caption (en)": "gift powers sight-saving work—with a tax deduction in return",
    "the deduction label": "預計慈善捐款扣稅額",
    # 23 Nov: the ordinal is prepended at render, so the marker is the cap sentence itself.
    "the 35% cap line": '"d.capline.band.ok"',
    "the salaries-tax scope line": "以上僅估算個人薪俸稅下的捐款扣稅，並不構成稅務建議",
    "the payment-reference help button": 'id="ref-help"',
    "the help panel is a dialog": 'role="dialog"',
    "the AlipayHK help screencap": "../assets/help/alipay-step-2.jpg",
    "the help panel's third step": "../assets/help/alipay-step-3.jpg",
}
missing = [k for k, v in MUST.items() if v not in body]
check(f"{len(MUST)} markers of this pass are in the live document", missing)

MUST_NOT = {
    # 21 Nov: PayMe was dropped. Every trace of it must stay gone from the served bytes.
    "the dropped rail's name": "PayMe",
    "its QR asset": "payme.png",
    "its mobile sub-label key": "s3.payme.sub",
    "its CSS rule": "r-payme",
    "its rail value": 'data-rail="payme"',
    "its alt-text key": "s3.qr.alt.payme",
    "months select": 'id="months"',
    "months field": 'id="months-field"',
    "clampMonths": "clampMonths",
    "old ground colour": "--ground:#F3F3F0",
    "44rem column": "max-width:44rem",
    "minus-sign render": '"−" + money',
    "our draft disclaimer": "不能取代專業意見",
    "the monthly reminder link": 'data-i18n="s3.monthly"',
    "the scope reminder": 'data-i18n="s2.scope"',
    # 23 Nov: the hover state pointed at a colour token that never existed.
    "the dead hover colour": "var(--orange-ink)",
    # 23 Nov: the client removed these outright, so their return is a regression.
    "the quick-amount chips": "data-amt=",
    "the chips' group label": "quick-amount",
    "the 'what counts' disclosure": 'id="what-counts"',
    "its summary (zh)": "哪些捐款才可扣稅",
    "its summary (en)": "What counts as a deductible gift",
    "the spouse FAQ": 'id="spouse"',
    "its question (zh)": "夫婦的扣稅額可否合併使用",
    "its question (en)": "Can a couple combine the deduction",
    "the old CTA (zh)": "看實際付出",
    "the old CTA (en)": "See what it costs you",
    "the old band hint (zh)": "未扣除免稅額（以 HK$145,000 估算）",
    "the removed gift ledger row": 'id="gift-out"',
}
body_code = strip_comments(body)
present = [k for k, v in MUST_NOT.items() if v in body_code]
check(f"{len(MUST_NOT)} removed things are absent from the live document", present)

# ── 1b · the three help screencaps are served too ────────────────────────────
# The widget now depends on assets/help/*.jpg. A deploy that pushes index.html and
# forgets the images ships a popover with three dead boxes — and the page itself
# still answers 200, so only fetching them proves it.
for name in ("alipay-step-1.jpg", "alipay-step-2.jpg", "alipay-step-3.jpg"):
    s_img, n_img = fetch_status(f"/assets/help/{name}")
    check(f"the help screencap {name} is served", [] if s_img == 200 and n_img > 5000
          else [f"status {s_img}, {n_img} bytes"], f"{n_img} bytes")

# ── 2 · the live DOM ─────────────────────────────────────────────────────────
with sync_playwright() as pw:
    b = pw.chromium.launch(channel="chrome", headless=True)
    for w in (390, 1440):
        p = b.new_page(viewport={"width": w, "height": 900},
                       is_mobile=(w < 600), has_touch=(w < 600))
        p.goto(f"{BASE}/embed/?part=all&lang=en&cb={w}", wait_until="load")
        p.wait_for_timeout(900)
        d = p.evaluate("""()=>({
            bg: getComputedStyle(document.documentElement).backgroundColor,
            wrap: Math.round(document.querySelector('.wrap').getBoundingClientRect().width),
            sections: [...document.querySelectorAll('section')]
                        .filter(s=>getComputedStyle(s).display!=='none').map(s=>s.id),
            saved: document.getElementById('saved').textContent,
            net: document.getElementById('net').textContent,
            gift: document.getElementById('gift').value,
            exact: document.getElementById('exact').value,
            bodySize: parseFloat(getComputedStyle(document.body).fontSize),
            bodyLH: parseFloat(getComputedStyle(document.body).lineHeight),
            h2Size: parseFloat(getComputedStyle(document.querySelector('h2')).fontSize),
            nlabel: document.getElementById('net-label').textContent,
            benefit: document.getElementById('benefit').textContent,
            whatcounts: !!document.getElementById('what-counts'),
            spouse: !!document.getElementById('spouse'),
            help: !!document.getElementById('ref-help'),
            h: document.documentElement.scrollHeight,
            monthly: !!document.getElementById('months'),
            overflow: document.documentElement.scrollWidth > document.documentElement.clientWidth + 1
        })""")
        print(f"\nbrowser @ {w}px: {d}")
        errs = []
        if d["bg"] != "rgb(255, 255, 255)":
            errs.append(f"ground {d['bg']}")
        if d["wrap"] != (min(1280, w)):
            errs.append(f"column {d['wrap']}px")
        if d["sections"] != ["calculator", "result", "payment", "receipt"]:
            errs.append(f"sections {d['sections']}")
        if "−" in d["saved"] or "HK$" not in d["saved"]:
            errs.append(f"saved {d['saved']!r}")
        if d["net"] != "HK$100":
            errs.append(f"the hero figure is not the default donation: {d['net']!r}")
        if d["nlabel"] != "Your donation":
            errs.append(f"hero label {d['nlabel']!r}")
        if "HK$100" not in d["benefit"] or "net support" not in d["benefit"]:
            errs.append(f"benefit sentence {d['benefit'][:80]!r}")
        if d["gift"] != "100":
            errs.append(f"the gift field does not read 100 on load: {d['gift']!r}")
        if d["exact"] != "145,000":
            errs.append(f"the exact-income field does not read 145,000 on load: {d['exact']!r}")
        if d["bodySize"] != 18.0:
            errs.append(f"body font-size {d['bodySize']}px, not 18px")
        if abs(d["bodyLH"] - 28.08) > 0.2:
            errs.append(f"body line-height {d['bodyLH']}px, not 1.56 x 18px")
        if d["h2Size"] < 32.0 and w >= 1280:
            errs.append(f"block heading {d['h2Size']}px at {w}px, not 32px")
        if d["whatcounts"] or d["spouse"]:
            errs.append(f"a removed block is back: what-counts={d['whatcounts']} spouse={d['spouse']}")
        if not d["help"]:
            errs.append("the transaction-ID help button is missing")
        if d["monthly"]:
            errs.append("a months control is still in the DOM")
        if d["overflow"]:
            errs.append("horizontal overflow")
        check(f"the live combined document renders correctly at {w}px", errs,
              f"{d['h']}px tall")
        p.close()
    b.close()

print(f"\n=== live verification: {ok} passed, {bad} failed ===\n{BASE}/embed/?part=all&lang=en")
sys.exit(1 if bad else 0)
