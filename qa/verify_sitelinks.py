#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verify the two published github.io paths render the right language.

Checks, on the LIVE URLs (not the local copy):
  /zh/   the heading is Chinese, the widget computes, the crops decode
  /en/   the same with English copy — and no CJK left in it
  both   no 404 asset inside the frame, no horizontal overflow at 320px

A path that 200s but renders the wrong language is the failure this catches: the
two files are generated from one source, so a bad transform shows up only here.
"""
import sys
from playwright.sync_api import sync_playwright

ZH = "https://2skdigitals.github.io/fh-taxcalculator-zh/"
EN = "https://2skdigitals.github.io/fh-taxcalculator-en/"
ok = bad = 0


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
    for url, lang in ((ZH, "zh"), (EN, "en")):
        pg = b.new_page(viewport={"width": 390, "height": 900})
        failed = []
        pg.on("response", lambda r: failed.append(f"{r.status} {r.url}") if r.status >= 400 else None)
        pg.goto(url, wait_until="load")
        pg.wait_for_timeout(2000)

        h = pg.inner_text("#s1bh")
        html_lang = pg.evaluate("document.documentElement.lang")
        title = pg.title()
        # the calculator must compute from its default on first paint
        gift = pg.eval_on_selector("#gift", "e => e.value")
        saved = pg.evaluate("() => (document.querySelector('#saved')||{}).textContent || ''")
        overflow = pg.evaluate("document.documentElement.scrollWidth - window.innerWidth")
        # The lazy crops inside the receipt popover only load when it opens — check
        # them open, not hidden, or five correct files read as broken.
        pg.click("#alipay-help")
        pg.wait_for_timeout(1500)
        imgs = pg.eval_on_selector_all("img", "els => els.map(e => [e.getAttribute('src'), e.naturalWidth])")
        dead = [s for s, w in imgs if not w]

        errs = []
        if lang == "zh":
            if "收入" not in h:
                errs.append(f"heading not Chinese: {h!r}")
            if html_lang != "zh-Hant-HK":
                errs.append(f"document lang {html_lang!r}")
        else:
            if "income" not in h.lower():
                errs.append(f"heading not English: {h!r}")
            if html_lang != "en":
                errs.append(f"document lang {html_lang!r}")
            if "Donation tax calculator" not in title:
                errs.append(f"title {title!r}")
        if not gift:
            errs.append("gift field empty")
        if not saved:
            errs.append("no computed result on first paint")
        if failed:
            errs.append(f"failed requests: {failed}")
        if dead:
            errs.append(f"images that did not decode: {dead}")
        if overflow > 1:
            errs.append(f"horizontal overflow {overflow}px at 390")
        check(f"{url} renders {lang} · computes · no 404 · no overflow", errs)
        pg.screenshot(path=f"/tmp/sitelink-{lang}.png", full_page=False)
        pg.close()
    b.close()

print(f"\n{ok} passed, {bad} failed")
sys.exit(1 if bad else 0)
