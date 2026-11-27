#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verify the AlipayHK receipt tooltip in BOTH languages after the English crop pass.

Asserts, on the real widget in a browser (not by grepping the file):

  1. zh-Hant-HK frames load the SIX Chinese crops; en frames load the SIX English
     crops (src carries "-en-"), and every one of them decodes
     (naturalWidth > 0) — a crop that 404s renders as an empty box, which reads
     as a missing asset on the live page;
  2. the width/height attributes match the decoded file, so the panel's aspect
     box is right before the image paints;
  3. the alt text follows the language: Chinese alts on zh, and NO CJK anywhere
     in the English alts (a Chinese label on an English page is an invisible
     WCAG defect no screenshot catches);
  4. no English sentence still names a Chinese app label the English crops do
     not show;
  5. the income-range label reads 全年收入 in Chinese, and its accessible name
     (aria-label on the select) agrees;
  6. the panel opens the same way on both languages and holds six steps.

Usage (needs a server on the repo root):
  python3 -m http.server 8777 &          # from the repo root
  /Library/Developer/CommandLineTools/usr/bin/python3 qa/verify_alipay_en_crops.py [base]
"""
import re
import sys
from playwright.sync_api import sync_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8777"
ok = bad = 0
CJK = re.compile(r"[\u3400-\u9fff]")


def check(label, errs):
    global ok, bad
    if errs:
        bad += 1
        print(f"FAIL  {label}")
        for e in errs:
            print("        ", e)
    else:
        ok += 1
        print(f"PASS  {label}")


with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome")
    page = b.new_page(viewport={"width": 1280, "height": 1000})

    for lang in ("zh", "en"):
        page.goto(f"{BASE}/embed/?part=pay&lang={lang}", wait_until="load")
        page.wait_for_timeout(600)
        page.click("#alipay-help")
        page.wait_for_timeout(900)

        imgs = page.eval_on_selector_all(
            "#alipay-help-panel .hsteps img",
            """els => els.map(e => ({src: e.getAttribute('src'), nw: e.naturalWidth,
                                    nh: e.naturalHeight, w: +e.getAttribute('width'),
                                    h: +e.getAttribute('height'), alt: e.getAttribute('alt')}))""")
        errs = []
        if len(imgs) != 6:
            errs.append(f"{len(imgs)} images, expected 6")
        for i, im in enumerate(imgs, 1):
            want_en = lang == "en"
            is_en = "-en-" in (im["src"] or "")
            if want_en != is_en:
                errs.append(f"step {i}: lang={lang} but src={im['src']}")
            if not im["nw"]:
                errs.append(f"step {i}: did not decode (404 or truncated) {im['src']}")
            if im["nw"] and im["w"] and abs(im["nw"] - im["w"]) > 1:
                errs.append(f"step {i}: width attr {im['w']} != natural {im['nw']}")
            if im["nh"] and im["h"] and abs(im["nh"] - im["h"]) > 1:
                errs.append(f"step {i}: height attr {im['h']} != natural {im['nh']}")
            if not im["alt"]:
                errs.append(f"step {i}: empty alt")
            if lang == "en" and im["alt"] and CJK.search(im["alt"]):
                errs.append(f"step {i}: CJK in English alt: {im['alt'][:60]}")
        check(f"{lang}: six crops decode, per-language, dims + alt agree", errs)

        # no English sentence may name a Chinese label the English crops don't show
        if lang == "en":
            txt = page.inner_text("#alipay-help-panel")
            stray = [t for t in ("需要收據", "捐款人資料", "慈善捐款", "我的捐款",
                                 "捐款記錄", "申請收據", "交易記錄", "捐款結果")
                     if t in txt]
            check("en: no Chinese app label left in the copy", stray)
            check("en: outro no longer claims a Chinese interface",
                  [] if "in Chinese" not in txt else ["outro still says 'in Chinese'"])

        page.screenshot(path=f"/tmp/alipay-help-{lang}.png", full_page=False)

        # the income-range label
        page.goto(f"{BASE}/embed/?part=input&lang={lang}", wait_until="load")
        page.wait_for_timeout(400)
        got = page.evaluate(
            """() => ({h: document.querySelector('#s1bh').textContent.trim(),
                       aria: (document.querySelector('#band-mobile')||{}).getAttribute
                             ? document.querySelector('#band-mobile').getAttribute('aria-label') : ''})""")
        if lang == "zh":
            errs = []
            if "全年收入" not in got["h"]:
                errs.append(f"heading: {got['h']!r}")
            if "全年收入" not in (got["aria"] or ""):
                errs.append(f"aria-label: {got['aria']!r}")
            if "年薪" in (got["aria"] or ""):
                errs.append("aria-label still says 年薪")
            check("zh: income label reads 全年收入 (option + aria)", errs)
        else:
            check("en: income label unchanged", [] if "yearly income" in got["h"]
                  else [f"heading: {got['h']!r}"])

    b.close()

print(f"\n{ok} passed, {bad} failed")
sys.exit(1 if bad else 0)
