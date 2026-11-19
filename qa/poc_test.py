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

    # Band mode now brackets the selected band's floor and ceiling, so a band
    # wide enough to cross a slice renders a RANGE. These are the exact pairs
    # the engine produces at each band's ends (qa/test_tax_engine.py proves the
    # engine; this proves the render). The old flat multiplier printed one
    # number here and overstated every gift large enough to cross a band.
    cases = [
        ("500 in the 17% band -> 70 to 85 / net 415-430", "once", 500, None, "r17",
         {"gift": "HK$500", "saved": "−HK$70 至 −HK$85", "net": "HK$415 – 430"}),
        ("1,800 in the 17% band -> 252 to 306 / net 1,494-1,548", "once", 1800, None, "r17",
         {"gift": "HK$1,800", "saved": "−HK$252 至 −HK$306", "net": "HK$1,494 – 1,548"}),
        ("500 below the allowance -> 0 / 500", "once", 500, None, "r0",
         {"gift": "HK$500", "saved": "−HK$0", "net": "HK$500", "rate": "0%"}),
        ("10,000 in the 15% band -> 1,500 to 1,700 / net 8,300-8,500", "once", 10000, None, "r15",
         {"gift": "HK$10,000", "saved": "−HK$1,500 至 −HK$1,700", "net": "HK$8,300 – 8,500",
          # a band, not a single rate: the crossing of the standard/progressive tie
          # at 2,132,500 means the band's ends save at 15% and 17%, so the row
          # may not be labelled 邊際 or 標準 any more.
          "rateLabel": "採用的稅率"}),
        ("monthly 1,300 x 6 in the 17% band -> 7,800 / 1,092-1,326", "monthly", 1300, 6, "r17",
         {"gift": "HK$7,800", "saved": "−HK$1,092 至 −HK$1,326", "net": "HK$6,474 – 6,708",
          "giftLabel": "全年總額（6 個月）"}),
        ("monthly 1,300 x 4 in the 2% band -> 5,200 / 0-104", "monthly", 1300, 4, "r2",
         {"gift": "HK$5,200", "saved": "−HK$0 至 −HK$104", "net": "HK$5,096 – 5,200",
          "rate": "0% – 2%"}),
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
    check("未知入息 shows a 0%–17% range, never a single invented rate",
          [] if (got["rate"] == "0% – 17%" and "至" in got["saved"]) else
          [f"rate={got['rate']!r} saved={got['saved']!r}"])

    f.click('input[name="band"][value="r17"]')
    f.fill("#gift", "175000")
    settle(pg, 250)
    got = f.evaluate(READ)
    # The 35% ceiling must be COMPUTED, not flagged and left out of the maths.
    # At the band's floor the cap limits the deduction to 120,750 (saving
    # 13,245); at its ceiling the gift is under the cap and saves 29,750. The
    # old engine printed the flat 17% figure, 29,750 as a single number at both
    # ends — and 42,500 for a 250,000 gift. Neither may come back.
    check("the 35% ceiling is computed, and a band renders both of its ends",
          [] if (got["saved"] == "−HK$13,245 至 −HK$29,750"
                 and got["savedLabel"] == "節省稅款"
                 and "35%" in got["cap"] and "未扣上限" not in got["savedLabel"]
                 and "42,500" not in got["saved"]) else
          [f"saved={got['saved']!r} label={got['savedLabel']!r} cap={got['cap'][:60]!r}"])

    f.click('input[name="mode"][value="monthly"]')
    f.fill("#gift", "1300")
    f.select_option("#months", "4")
    settle(pg, 300)
    got = f.evaluate(READ)
    check("monthly caption shows the arithmetic",
          [] if "每月 HK$1,300 × 4 個月 = 全年 HK$5,200" in got["caption"] else
          [repr(got["caption"])])

    # ---------------------------------------------------------------- C
    pg.wait_for_timeout(1200)
    got_names = names(pg)
    check("calc_started + calc_result_shown reach the host",
          [] if ("calc_started" in got_names and "calc_result_shown" in got_names) else [str(got_names[:10])])

    payloads = json.dumps([m.get("params") for m in msgs(pg) if m.get("type") == "event"], ensure_ascii=False)
    forbidden = [r'"amount"', r'"income"', r'"rate"', r'"marginal"', r'1,?300\b', r'"5200"', r'5,200']
    hits = [p for p in forbidden if re.search(p, payloads)]

    # ...and the optional exact-income field must not leak either. Type a
    # distinctive value, wait past the 800ms event debounce, and re-scan
    # everything the frame has ever posted: the value and its formatted form
    # must be absent, and the only permitted trace is exact:"yes"|"no".
    f.evaluate("()=>{document.getElementById('exact-row').open = true;}")
    f.fill("#exact", "654321")
    settle(pg, 1100)
    payloads = json.dumps([m.get("params") for m in msgs(pg) if m.get("type") == "event"], ensure_ascii=False)
    hits += [p for p in [r'654,?321', r'"exact"\s*:\s*"(?!yes"|no")'] if re.search(p, payloads)]
    if '"exact": "yes"' not in payloads:
        hits.append('exact dimension missing from calc_result_shown')
    check("no amount / income / marginal-rate value in any payload (exact income included)",
          [] if not hits else [str(hits)])
    f.fill("#exact", "")
    settle(pg, 120)

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
    s = f.evaluate("() => ({n: document.getElementById('rname-msg').hidden, m: document.getElementById('rmail-msg').hidden, r: document.getElementById('rref-msg').hidden})")
    check("empty receipt submit is blocked with field errors (name, email, reference)",
          [] if (s["n"] is False and s["m"] is False and s["r"] is False) else [str(s)])

    f.fill("#rname", "陳大文")
    f.fill("#rmail", "not-an-email")
    f.click('button[type="submit"]')
    settle(pg, 150)
    s = f.evaluate("() => document.getElementById('rmail-msg').hidden")
    check("invalid email is rejected", [] if s is False else [f"hidden={s}"])

    f.fill("#rmail", "donor@example.com")
    f.check("#consent")
    f.click('button[type="submit"]')
    settle(pg, 300)
    got_names = names(pg)
    check("a receipt request without the payment reference is refused",
          [] if ("receipt_request" not in got_names) else ["receipt_request fired with no reference"])

    # a QR gift happens in the donor's own app, so the reference is the ONLY thing that
    # ties a claim to money that arrived. It must travel to the receipt system — and it
    # must never appear in a measurement payload.
    REF = "PM-20261118-77XK2"
    f.fill("#rref", REF)
    f.click('button[type="submit"]')
    settle(pg, 400)
    got_names = names(pg)
    check("valid capture fires email_capture + receipt_request",
          [] if ("email_capture" in got_names and "receipt_request" in got_names) else [str(got_names)])

    rr = [m for m in msgs(pg) if m.get("type") == "event" and m.get("name") == "receipt_request"]
    check("receipt_request reports that a reference was given",
          [] if rr and rr[-1].get("params", {}).get("has_reference") == "yes" else [str(rr[-1] if rr else None)])
    leaked = [m for m in msgs(pg) if REF in json.dumps(m, ensure_ascii=False)]
    check("the payment reference never appears in any payload", [] if not leaked else [str(leaked)[:200]])

    # ---------------------------------------------------------------- F · payment rails are live links
    # The POC deep-link bench is gone: the wallet rails are now ordinary links to the
    # charity's own giving page, so the assertion is that they navigate and that no
    # dead control or placeholder text is left on the block.
    rails = f.evaluate("""() => [...document.querySelectorAll('.rails [data-rail]')].map(el => ({
        tag: el.tagName, rail: el.dataset.rail, href: el.getAttribute('href') || '',
        target: el.getAttribute('target') || '', rel: el.getAttribute('rel') || '',
        text: el.textContent.replace(/\\s+/g, ' ').trim()}))""")
    check("three payment rails present", [] if len(rails) == 3 else [str(rails)])
    bad_tag = [r for r in rails if r["tag"] != "A"]
    check("every rail is a link, not a dead button", [] if not bad_tag else [str(bad_tag)])
    # Two kinds of destination are legitimate now: the charity's own pages, and the
    # live wallet endpoints decoded from the codes they publish (19 Nov). Anything else
    # is a rail that goes somewhere nobody agreed to.
    ALLOWED = ("https://www.hollows.org/", "https://qr.payme.hsbc.com.hk/",
               "https://render.alipay.hk/")
    bad_href = [r for r in rails if not r["href"].startswith(ALLOWED)]
    check("every rail points at hollows.org or a decoded wallet endpoint",
          [] if not bad_href else [str(bad_href)])
    pays = {r["rail"]: r["href"] for r in rails}
    check("the two wallets carry the endpoints decoded from the published QR codes",
          [] if (pays.get("payme", "").startswith("https://qr.payme.hsbc.com.hk/")
                 and pays.get("alipay", "").startswith("https://render.alipay.hk/"))
          else [str(pays)])
    bad_top = [r for r in rails if r["target"] != "_top"]
    check("every rail escapes the frame (target=_top)", [] if not bad_top else [str(bad_top)])
    body = f.evaluate("() => document.body.innerText")
    banned = [w for w in ("POC", "test mode", "test code", "示意", "placeholder", "Placeholder") if w in body]
    check("no POC or placeholder text remains in the payment block", [] if not banned else [str(banned)])
    pg.close()

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
    # These numbers come from qa/sweep_heights.py — the peak of 22 widths from
    # 320 to 1440, plus 50–73px of slack. `calc` is in here because the client
    # embedded it: at 1,020px its content (1,499px at 320px) produced the second,
    # inner scrollbar they reported on mobile.
    BUDGET = {"calc": 1950, "input": 1190, "result": 860, "pay": 600, "receipt": 780}
    SECTIONS = {"calc": ["calculator", "result"], "input": ["calculator"],
                "result": ["result"], "pay": ["payment"], "receipt": ["receipt"]}
    for w in (328, 568, 944, 1280):
        for part, budget in BUDGET.items():
            pf = browser.new_page(viewport={"width": w, "height": budget}, is_mobile=(w < 600), has_touch=(w < 600))
            pf.goto(f"{BASE}/embed/?part={part}", wait_until="load")
            pf.wait_for_timeout(450)
            ov = pf.evaluate("()=>({sh:document.documentElement.scrollHeight, ch:document.documentElement.clientHeight})")
            vis = pf.evaluate("()=>[...document.querySelectorAll('section')].filter(s=>getComputedStyle(s).display!=='none').map(s=>s.id)")
            want = SECTIONS[part]
            errs = []
            if ov["sh"] > budget + 1:
                errs.append(f"content overflows the {budget}px box by {ov['sh'] - budget}px")
            if vis != want:
                errs.append(f"expected {want}, got {vis}")
            if pf.evaluate("()=>document.documentElement.scrollWidth > document.documentElement.clientWidth + 1"):
                errs.append("horizontal overflow")
            check(f"part '{part}' fits {budget}px at {w}px", errs)
            pf.close()

    # ---------------------------------------------------------------- K · C6 benefit line
    # The client's "selling point" sentence must follow the same numbers as the
    # figures strip, and it must never overclaim the benefit. Two falsifiable
    # forms: the sentence's per-100 range must be the exact complement of the
    # saving range it quotes, and "每捐 HK$100 實際付出約 HK$N" can never fall
    # below 83, because 17% is the top marginal rate and the 35% cap is never a
    # cash return. Both are pinned per band, so a drift in either fails.
    BAND_EXPECT = {
        # band: (saved range as rendered, per-100 range as rendered)
        "r2":  ("−HK$0 至 −HK$26",   "HK$98 至 HK$100"),
        "r6":  ("−HK$26 至 −HK$78",  "HK$94 至 HK$98"),
        "r10": ("−HK$78 至 −HK$130", "HK$90 至 HK$94"),
        "r14": ("−HK$130 至 −HK$182","HK$86 至 HK$90"),
        "r17": ("−HK$182 至 −HK$221","HK$83 至 HK$86"),
        "r15": ("−HK$195 至 −HK$221","HK$83 至 HK$85"),
        "r16": ("−HK$195 至 −HK$208","HK$84 至 HK$85"),
    }
    bench = browser.new_page(viewport={"width": 390, "height": 900}, is_mobile=True, has_touch=True)
    for band, (want_saved, want_100) in BAND_EXPECT.items():
        # ?part=calc, not ?part=result: the income picker lives in the calculator
        # block, so it is only reachable in a page where that block is visible.
        bench.goto(f"{BASE}/embed/?part=calc")
        bench.wait_for_timeout(350)
        bench.select_option("#band-mobile", band)
        bench.wait_for_timeout(220)
        line = bench.evaluate("()=>document.getElementById('benefit').textContent")
        shown = bench.evaluate("()=>document.getElementById('saved').textContent")
        errs = []
        if "認可慈善捐款扣除" not in line:
            errs.append("does not name 認可慈善捐款")
        if want_saved not in shown:
            errs.append(f"figures strip {shown!r} does not match {want_saved!r}")
        if f"實際付出約 {want_100}" not in line:
            errs.append(f"want 實際付出約 HK${want_100} in {line!r}")
        check(f"benefit line in band {band} matches the figures strip ({want_100} per HK$100)", errs)

    bench.select_option("#band-mobile", "r17")
    bench.fill("#gift", "175,000")
    bench.wait_for_timeout(250)
    line = bench.evaluate("()=>document.getElementById('benefit').textContent")
    strip = bench.evaluate("()=>document.getElementById('saved').textContent")
    # The line may not promise more than the cap allows, and it may not say
    # "lower than X" either — with the cap computed, X IS the achievable figure.
    # The figure itself lives in the figures strip (the sentence states the cap,
    # it does not repeat the number), so assert it there and keep the ban here.
    check("benefit line computes the 35% ceiling instead of promising a lower figure",
          [] if ("35% 上限" in line and "HK$29,750" in strip
                 and "會低於" not in line and "42,500" not in line
                 and "42,500" not in strip) else [f"line={line!r} strip={strip!r}"])

    # ---------------------------------------------------------------- L · C2 declarations
    d = bench.evaluate("""()=>({
        scope: (document.querySelector('.scope')||{}).textContent || '',
        spouse: (document.getElementById('spouse')||{}).textContent || '',
        disc: (document.getElementById('disclaimer')||{}).textContent || '',
        closed: !(document.getElementById('disclaimer')||{hasAttribute:()=>false}).hasAttribute('open'),
        link: (document.querySelector('#receipt a[href="#disclaimer"]')||{}).textContent || ''
    })""")
    check("scope line states salaries-tax-only and 並非稅務建議",
          [] if ("薪俸稅" in d["scope"] and "並非稅務建議" in d["scope"]) else [d["scope"][:80]])
    check("spouse note does not promise the excess is freely transferable",
          [] if ("BIR60" in d["spouse"] and "35%" in d["spouse"] and "不能全數轉移" in d["spouse"])
          else [d["spouse"][:120]])
    check("disclaimer exists, is collapsed by default, and is reachable from the consent line",
          [] if (d["closed"] and "免責聲明" in d["link"] and "稅務局評定為準" in d["disc"]
                 and "不收集、不儲存" in d["disc"]) else [str(d)[:200]])

    # ---------------------------------------------------------------- M · C4 tap targets
    # Measured per block, because the controls live in different blocks and a
    # hidden element cannot be measured (offsetParent === null is skipped).
    tap = []
    for bench_part in ("calc", "pay", "receipt"):
        bench.goto(f"{BASE}/embed/?part={bench_part}")
        bench.wait_for_timeout(320)
        tap += bench.evaluate("""()=>{
            const sels = ['#calculator .chips button', '.seg label', '#band-mobile',
                          '.rform .consent', '#rsubmit', '.rails button', '.rails a',
                          'details.q summary', '.amt'];
            const out = [];
            for (const s of sels) {
              for (const e of document.querySelectorAll(s)) {
                if (e.offsetParent === null) continue;
                const h = Math.round(e.getBoundingClientRect().height);
                if (h < 44) out.push(`${s} ${h}px`);
              }
            }
            return out;
          }""")
    check("every thumb target on the phone surface is at least 44px tall", tap)
    bench.close()

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

    # ---------------------------------------------------------------- J · container inside the frame
    pc = browser.new_page(viewport={"width": 390, "height": 900})
    pc.goto(f"{BASE}/embed/?part=input&gtm=GTM-XXXXXXX", wait_until="load")
    pc.wait_for_timeout(900)
    g = pc.evaluate("""() => ({
        init: (window.dataLayer || []).find(x => x && x.event === 'fhf_init') || null,
        script: !!document.querySelector('script[src*="googletagmanager.com/gtm.js"]')
      })""")
    check("a container ID loads GTM inside the frame and seeds dataLayer with the host page",
          [] if (g["script"] and g["init"] and "host_page" in g["init"]) else [str(g)])
    pc.close()

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
