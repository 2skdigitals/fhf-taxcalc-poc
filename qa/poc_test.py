#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QA harness for the FHF tax-calculator iframe POC.

The widget only talks to a *parent*, so everything runs inside qa/fixture.html
(the minimal host page), not on the widget directly.

  A. tax engine vs the verified examples (cap-free cases)
  B. iframe contract: ready, resize convergence, event payloads
  C. honesty invariant: no amount / income / rate in any payload
  D. fixed-height mode, no horizontal overflow at 390px and 1100px
  E. receipt validation + email_capture
  F. app-open attempt is observable from the host
  G. the harness page itself converges to the reported height

Exit 1 on any failure.  Requires: playwright + Google Chrome (channel="chrome").
"""
import json
import re
import sys
from playwright.sync_api import sync_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8765"
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


READ = """() => ({
  net: document.getElementById('net').textContent.trim(),
  gift: document.getElementById('gift-out').textContent.trim(),
  giftLabel: document.getElementById('gift-label').textContent.trim(),
  saved: document.getElementById('saved').textContent.trim(),
  savedLabel: document.getElementById('saved-label').textContent.trim(),
  rate: document.getElementById('rate').textContent.trim(),
  rateLabel: document.getElementById('rate-label').textContent.trim(),
  cap: document.getElementById('cap').textContent.trim(),
  caption: document.getElementById('net-caption').textContent.trim(),
})"""


def msgs(pg):
    return pg.evaluate("() => window.__msgs || []")


def names(pg):
    return [m.get("name") for m in msgs(pg) if m.get("type") == "event"]


def settle(pg, ms=180):
    pg.wait_for_timeout(ms)


with sync_playwright() as pw:
    browser = pw.chromium.launch(channel="chrome", headless=True)

    # ================================================== A · engine + B · contract
    pg = browser.new_page(viewport={"width": 1100, "height": 1200})
    pg.goto(f"{BASE}/qa/fixture.html", wait_until="load")
    pg.wait_for_timeout(600)
    f = pg.frames[1]

    ready = [m for m in msgs(pg) if m.get("type") == "ready"]
    check("widget posts ready on boot", [] if ready else [str(msgs(pg))[:200]])

    resizes = [m["height"] for m in msgs(pg) if m.get("type") == "resize"]
    check("widget posts at least one resize", [] if resizes else [str(msgs(pg))[:200]])

    cases = [
        ("500 @17% -> saved 85 / net 415", "once", 500, None, "r17",
         {"gift": "HK$500", "saved": "−HK$85", "net": "HK$415"}),
        ("1,800 @17% -> 306 / 1,494", "once", 1800, None, "r17",
         {"gift": "HK$1,800", "saved": "−HK$306", "net": "HK$1,494"}),
        ("500 @140k (below the allowance) -> 0 / 500", "once", 500, None, "r0",
         {"gift": "HK$500", "saved": "−HK$0", "net": "HK$500", "rate": "0%"}),
        ("10,000 @2.5M (standard 15%) -> 1,500 / 8,500", "once", 10000, None, "r15",
         {"gift": "HK$10,000", "saved": "−HK$1,500", "net": "HK$8,500",
          "rateLabel": "估算用嘅標準稅率"}),
        ("monthly 1,300 x 6 @17% -> 7,800 / 1,326", "monthly", 1300, 6, "r17",
         {"gift": "HK$7,800", "saved": "−HK$1,326", "net": "HK$6,474",
          "giftLabel": "全年捐款總額（6 個月）"}),
        ("monthly 1,300 x 4 @2% -> 5,200 / 104", "monthly", 1300, 4, "r2",
         {"gift": "HK$5,200", "saved": "−HK$104", "net": "HK$5,096", "rate": "2%"}),
    ]
    for label, mode, amt, months, band, exp in cases:
        f.click(f'input[name="mode"][value="{mode}"]')
        settle(pg, 90)
        f.fill("#gift", str(amt))
        settle(pg, 90)
        f.click(f'input[name="band"][value="{band}"]')
        settle(pg, 90)
        if months is not None:
            f.select_option("#months", str(months))
            settle(pg, 120)
        got = f.evaluate(READ)
        errs = [f"{k}: got {got.get(k)!r} want {v!r}" for k, v in exp.items() if got.get(k) != v]
        check(label, errs)

    f.click('input[name="mode"][value="once"]')
    f.fill("#gift", "1300")
    f.click('input[name="band"][value="unknown"]')
    settle(pg, 250)
    got = f.evaluate(READ)
    check("未知入息 shows a 2%–17% range, never a single invented rate",
          [] if (got["rate"] == "2% – 17%" and "至" in got["saved"]) else
          [f"rate={got['rate']!r} saved={got['saved']!r}"])

    f.click('input[name="band"][value="r17"]')
    f.fill("#gift", "175000")
    settle(pg, 250)
    got = f.evaluate(READ)
    check("the 35% ceiling is flagged, never silently computed",
          [] if ("上限" in got["cap"] and "最多" in got["savedLabel"]) else
          [f"cap={got['cap'][:40]!r} savedLabel={got['savedLabel']!r}"])

    f.click('input[name="mode"][value="monthly"]')
    f.fill("#gift", "1300")
    f.select_option("#months", "4")
    settle(pg, 300)
    got = f.evaluate(READ)
    check("monthly caption shows the arithmetic",
          [] if "每月 HK$1,300 × 4 個月 = 全年合計 HK$5,200" in got["caption"] else
          [repr(got["caption"])])

    # ---------------------------------------------------------------- C
    pg.wait_for_timeout(1200)
    got_names = names(pg)
    check("calc_started + calc_result_shown reach the host",
          [] if ("calc_started" in got_names and "calc_result_shown" in got_names) else [str(got_names[:10])])

    payloads = json.dumps([m.get("params") for m in msgs(pg) if m.get("type") == "event"], ensure_ascii=False)
    forbidden = [r'"amount"', r'"income"', r'"rate"', r'"marginal"', r'1,?300\b', r'"5200"', r'5,200']
    hits = [p for p in forbidden if re.search(p, payloads)]
    check("no amount / income / marginal-rate value in any payload", [] if not hits else [str(hits)])

    # ---------------------------------------------------------------- D · resize on change
    before = len(resizes)
    f.click('input[name="mode"][value="once"]')
    settle(pg, 350)
    after_h = [m["height"] for m in msgs(pg) if m.get("type") == "resize"]
    check("a height change pushes a new resize (dedupe, not silence)",
          [] if len(after_h) > before and after_h[-1] != resizes[-1] else
          [f"before={before} after={len(after_h)} last={after_h[-1] if after_h else None}"])

    box = pg.evaluate("() => Math.round(document.getElementById('f').getBoundingClientRect().height)")
    reported = after_h[-1]
    check("host-applied height converges to the reported height (±2px)",
          [] if abs(box - reported) <= 2 else [f"box={box} reported={reported}"])

    no_overflow = f.evaluate("() => document.documentElement.scrollWidth <= document.documentElement.clientWidth + 1")
    check("no horizontal overflow at 1100px", [] if no_overflow else ["scrollWidth > clientWidth"])

    # ---------------------------------------------------------------- E · receipt
    f.click('button[type="submit"]')
    settle(pg, 200)
    s = f.evaluate("() => ({n: document.getElementById('rname-msg').hidden, m: document.getElementById('rmail-msg').hidden})")
    check("empty receipt submit is blocked with field errors", [] if (s["n"] is False and s["m"] is False) else [str(s)])

    f.fill("#rname", "陳大文")
    f.fill("#rmail", "not-an-email")
    f.click('button[type="submit"]')
    settle(pg, 150)
    s = f.evaluate("() => document.getElementById('rmail-msg').hidden")
    check("invalid email is rejected", [] if s is False else [f"hidden={s}"])

    f.fill("#rmail", "donor@example.com")
    f.check("#consent")
    f.click('button[type="submit"]')
    settle(pg, 400)
    got_names = names(pg)
    check("valid capture fires email_capture + receipt_request",
          [] if ("email_capture" in got_names and "receipt_request" in got_names) else [str(got_names)])

    # ---------------------------------------------------------------- F · app-open (last: it may navigate)
    f.click('[data-deeplink="payme"]')
    settle(pg, 500)
    dl = [m for m in msgs(pg) if m.get("type") == "deeplink"]
    check("app-open attempt is observable from the host before any navigation",
          [] if dl and dl[0].get("phase") == "attempt" else [str(dl)])
    pg.close()   # the top frame may now be parked on an unhandled scheme

    # ---------------------------------------------------------------- D2 · narrow viewport
    pg2 = browser.new_page(viewport={"width": 390, "height": 800})
    pg2.goto(f"{BASE}/qa/fixture.html", wait_until="load")
    pg2.wait_for_timeout(600)
    f2 = pg2.frames[1]
    w = f2.evaluate("() => document.documentElement.scrollWidth <= document.documentElement.clientWidth + 1")
    check("no horizontal overflow at 390px", [] if w else ["scrollWidth > clientWidth"])

    pg3 = browser.new_page(viewport={"width": 390, "height": 800})
    pg3.goto(f"{BASE}/embed/?h=600", wait_until="load")
    pg3.wait_for_timeout(400)
    fit = pg3.evaluate("() => document.documentElement.getAttribute('data-fit')")
    taller = pg3.evaluate("() => document.documentElement.scrollHeight > 600")
    check("fixed-height mode is declared and the content is honestly taller than 600px",
          [] if (fit == "fixed" and taller) else [f"data-fit={fit!r} taller={taller}"])

    # ---------------------------------------------------------------- H · fixed-height parts
    # The real acceptance test: open each block at the height the client will set,
    # at the widths their page actually produces (iframe 328px → 1280px).
    BUDGET = {"input": 1000, "result": 750, "pay": 1100, "receipt": 650}
    for w in (328, 568, 944, 1280):
        for part, budget in BUDGET.items():
            pf = browser.new_page(viewport={"width": w, "height": budget}, is_mobile=(w < 600), has_touch=(w < 600))
            pf.goto(f"{BASE}/embed/?part={part}", wait_until="load")
            pf.wait_for_timeout(450)
            ov = pf.evaluate("()=>({sh:document.documentElement.scrollHeight, ch:document.documentElement.clientHeight})")
            vis = pf.evaluate("()=>[...document.querySelectorAll('section')].filter(s=>getComputedStyle(s).display!=='none').map(s=>s.id)")
            errs = []
            if ov["sh"] > budget + 1:
                errs.append(f"content overflows the {budget}px box by {ov['sh'] - budget}px")
            if len(vis) != 1:
                errs.append(f"expected one visible section, got {vis}")
            if pf.evaluate("()=>document.documentElement.scrollWidth > document.documentElement.clientWidth + 1"):
                errs.append("horizontal overflow")
            check(f"part '{part}' fits {budget}px at {w}px", errs)
            pf.close()

    # ---------------------------------------------------------------- I · the event verification page
    pe = browser.new_page(viewport={"width": 1280, "height": 900})
    pe.goto(f"{BASE}/events/", wait_until="load")
    pe.wait_for_timeout(1200)
    ef = pe.frames[1]
    ef.fill("#gift", "2500")
    pe.wait_for_timeout(1400)
    ev = pe.evaluate("""() => ({n: document.getElementById('n').textContent,
        hon: document.getElementById('hon').textContent,
        rows: document.querySelectorAll('#rows tr').length})""")
    check("the event page receives calc_started + calc_result_shown and stays clean",
          [] if (int(ev["n"]) >= 2 and ev["hon"].strip() == "clean" and ev["rows"] >= 2) else [str(ev)])
    pe.close()

    # ---------------------------------------------------------------- G · the bench
    pg4 = browser.new_page(viewport={"width": 1440, "height": 1000})
    pg4.goto(f"{BASE}/harness/", wait_until="load")
    pg4.wait_for_timeout(1200)
    h = pg4.evaluate("""() => ({
        applied: parseInt(document.getElementById('frame').style.height) || 0,
        reported: parseInt(document.getElementById('m-h').textContent) || 0,
        checks: document.getElementById('chk-n').textContent
      })""")
    check("the bench applies the widget's reported height",
          [] if (h["reported"] > 800 and abs(h["reported"] - h["applied"]) <= 2) else [str(h)])

    browser.close()

print(f"\n=== {ok} passed, {bad} failed ===")
sys.exit(1 if bad else 0)
