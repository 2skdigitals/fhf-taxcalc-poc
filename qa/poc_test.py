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
  nlabel: document.getElementById('net-label').textContent.trim(),
  saved: document.getElementById('saved').textContent.trim(),
  savedLabel: document.getElementById('saved-label').textContent.trim(),
  rate: document.getElementById('rate').textContent.trim(),
  rateLabel: document.getElementById('rate-label').textContent.trim(),
  cap: document.getElementById('cap').textContent.trim(),
  caption: document.getElementById('net-caption').textContent.trim(),
  benefit: document.getElementById('benefit').textContent.trim(),
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
    # 23 Nov: the hero figure is the DONATION, not a net cost — the client's own
    # label for it is 您的全額捐款 / Your donation, and the ledger row that used to
    # repeat the gift was removed. The net cost did not vanish: it is the 實際支持
    # figure inside the benefit sentence, which section K below checks against the
    # gift. So these cases pin the gift, the saving and the rate-label logic.
    cases = [
        ("500 in the 17% band -> saved 70 to 85, hero carries the gift", "once", 500, "r17",
         {"net": "HK$500", "saved": "HK$70 至 HK$85"}),
        ("1,800 in the 17% band -> saved 252 to 306", "once", 1800, "r17",
         {"net": "HK$1,800", "saved": "HK$252 至 HK$306"}),
        ("500 below the allowance -> saves nothing", "once", 500, "r0",
         {"net": "HK$500", "saved": "HK$0", "rate": "0%"}),
        ("10,000 in the 15% band -> saved 1,500 to 1,700", "once", 10000, "r15",
         {"net": "HK$10,000", "saved": "HK$1,500 至 HK$1,700",
          # a band, not a single rate: the crossing of the standard/progressive tie
          # at 2,132,500 means the band's ends save at 15% and 17%, so the row
          # may not be labelled 邊際 or 標準 any more.
          "rateLabel": "採用的稅率"}),
        # Monthly is amount x 12 since the client's slide-2 note removed the months
        # control. The hero carries the annual total under the client's label; the
        # arithmetic itself is still announced (checked below), because the caption
        # is now the client's brand line and no longer carries it.
        ("monthly 1,300 x 12 in the 17% band -> hero 15,600", "monthly", 1300, "r17",
         {"net": "HK$15,600", "saved": "HK$2,184 至 HK$2,652", "nlabel": "您的全額捐款"}),
        ("monthly 1,300 x 12 in the 2% band -> 0 to 312", "monthly", 1300, "r2",
         {"net": "HK$15,600", "saved": "HK$0 至 HK$312", "rate": "0% – 2%"}),
    ]
    for label, mode, amt, band, exp in cases:
        f.click(f'input[name="mode"][value="{mode}"]')
        settle(pg, 90)
        f.fill("#gift", str(amt))
        settle(pg, 90)
        f.click(f'input[name="band"][value="{band}"]')
        settle(pg, 90)
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
          [] if (got["saved"] == "HK$13,245 至 HK$29,750"
                 and got["savedLabel"] == "預計慈善捐款扣稅額"
                 and "35%" in got["cap"] and "未扣上限" not in got["savedLabel"]
                 and "42,500" not in got["saved"]) else
          [f"saved={got['saved']!r} label={got['savedLabel']!r} cap={got['cap'][:60]!r}"])

    f.click('input[name="mode"][value="monthly"]')
    f.fill("#gift", "1300")
    settle(pg, 300)
    got = f.evaluate(READ)
    check("monthly: the hero carries the annual total under the client's label, "
          "and the caption is the client's sentence",
          [] if (got["net"] == "HK$15,600" and got["nlabel"] == "您的全額捐款"
                 and got["caption"] == "帶來滿滿救盲力量，同時享扣稅回饋") else
          [f"net={got['net']!r} label={got['nlabel']!r} caption={got['caption']!r}"])
    # The arithmetic left the caption on 23 Nov (the client replaced that line), so
    # this asserts the assumption is still STATED — the aria-live region is the one
    # place that still says "13 x 12 months = 15,600", and it must keep saying it.
    settle(pg, 900)
    ann = f.evaluate("()=>document.getElementById('announce').textContent")
    check("the 12-month assumption is still stated in the live region, not silently assumed",
          [] if ("12 個月" in ann and "15,600" in ann) else [repr(ann)])

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
    # exact income is a swap inside the income card now, not a disclosure
    f.click("#exact-toggle")
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
    check("two payment rails present", [] if len(rails) == 2 else [str(rails)])
    bad_tag = [r for r in rails if r["tag"] != "A"]
    check("every rail is a link, not a dead button", [] if not bad_tag else [str(bad_tag)])
    # Two kinds of destination are legitimate now: the charity's own pages, and the
    # one live wallet endpoint decoded from the code they publish (19 Nov). PayMe was
    # dropped on 21 Nov, so its host is no longer an allow-listed destination — if it
    # ever comes back it comes back through this list, deliberately.
    ALLOWED = ("https://www.hollows.org/", "https://render.alipay.hk/")
    bad_href = [r for r in rails if not r["href"].startswith(ALLOWED)]
    check("every rail points at hollows.org or the decoded wallet endpoint",
          [] if not bad_href else [str(bad_href)])
    pays = {r["rail"]: r["href"] for r in rails}
    check("AlipayHK carries the endpoint decoded from the published QR code",
          [] if pays.get("alipay", "").startswith("https://render.alipay.hk/") else [str(pays)])
    # The desktop arrangement is the other half of the same block: one QR + one card
    # tile, equal weight. A stale third tile or a dead PayMe <img> would pass the
    # mobile-row checks above, so assert the grid itself.
    grid = f.evaluate("""() => {
        const g = document.querySelector('.paygrid');
        const tiles = [...g.children].filter(c => getComputedStyle(c).display !== 'none');
        return {n: tiles.length,
                imgs: tiles.filter(t => t.querySelector('img')).length,
                rails: tiles.map(t => t.dataset.rail || ''),
                w: tiles.map(t => Math.round(t.getBoundingClientRect().width)),
                h: tiles.map(t => Math.round(t.getBoundingClientRect().height)),
                srcs: [...g.querySelectorAll('img')].map(i => i.getAttribute('src'))};
    }""")
    check("the desktop grid is one QR and one card tile, the same size",
          [] if (grid["n"] == 2 and grid["imgs"] == 1 and grid["rails"] == ["", "card"]
                 and len(set(grid["w"])) == 1 and len(set(grid["h"])) == 1) else [str(grid)])
    # The whole point of this pass: the rail that was dropped leaves nothing behind.
    hard = f.evaluate("""() => {
        const t = document.getElementById('payment').textContent;
        const srcs = [...document.images].map(i => i.getAttribute('src') || '');
        return {text: /payme/i.test(t.replace(/payment/gi, '')),
                imgs: srcs.filter(s => /payme/i.test(s.replace(/payment/gi, ''))),
                rail: [...document.querySelectorAll('[data-rail]')].map(e => e.dataset.rail)};
    }""")
    check("no PayMe copy, image or rail value survives in the payment block",
          [] if (not hard["text"] and not hard["imgs"]
                 and not [r for r in hard["rail"] if r.startswith("payme")]) else [str(hard)])
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
    # 320 to 1440, plus 45–70px of slack. `calc` is in here because the client
    # embedded it: at 1,020px its content (1,499px at 320px) produced the second,
    # inner scrollbar they reported on mobile.
    # Reissued 23 Nov 2026 (client call): 18px body at 1.56, 32px block heading,
    # 1280px column: 1610 / 950 / 800 / 545 / 820 / 2665.
    # Reissued AGAIN 23 Nov 2026 (qa/apply_disc_list_20261123.py): the disclaimer
    # became an always-visible five-item list, +110..260px on every block.
    # zh-HK: 1720 / 1050 / 980 / 640 / 990 / 2790.
    BUDGET = {"calc": 1720, "input": 1050, "result": 980, "pay": 640, "receipt": 990, "all": 2790}
    SECTIONS = {"calc": ["calculator", "result"], "input": ["calculator"],
                "result": ["result"], "pay": ["payment"], "receipt": ["receipt"],
                "all": ["calculator", "result", "payment", "receipt"]}
    for w in (328, 568, 944, 1280):
        for part, budget in BUDGET.items():
            pf = browser.new_page(viewport={"width": w, "height": budget}, is_mobile=(w < 600), has_touch=(w < 600))
            pf.goto(f"{BASE}/embed/?part={part}", wait_until="load")
            pf.wait_for_timeout(450)
            ov = pf.evaluate("()=>({sh:document.documentElement.scrollHeight, ch:document.documentElement.clientHeight})")
            # section.panel: the part-switched blocks. #disclaimer is a <section>
            # too and is deliberately visible in every part, so a bare 'section'
            # selector would report it as an unexpected panel.
            vis = pf.evaluate("()=>[...document.querySelectorAll('section.panel')].filter(s=>getComputedStyle(s).display!=='none').map(s=>s.id)")
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
    # 23 Nov: the sentence is the client's, and EVERY figure in it computes from
    # the donor's own gift. Three falsifiable properties, checked per band:
    #   · the relief pair in the sentence is the pair in the ledger,
    #   · the 實際支持 pair is the gift minus those two, and
    #   · no relief figure may exceed 17% of the gift (the cap is never cash back).
    # (saved low, saved high) for a HK$1,300 one-off gift, per band's two ends.
    BAND_EXPECT = {
        "r2":  (0, 26), "r6": (26, 78), "r10": (78, 130), "r14": (130, 182),
        "r17": (182, 221), "r15": (195, 221), "r16": (195, 208),
    }

    def hk(n):
        return "HK$" + format(n, ",")

    bench = browser.new_page(viewport={"width": 390, "height": 900}, is_mobile=True, has_touch=True)
    for band, (lo_s, hi_s) in BAND_EXPECT.items():
        # ?part=calc, not ?part=result: the income picker lives in the calculator
        # block, so it is only reachable in a page where that block is visible.
        bench.goto(f"{BASE}/embed/?part=calc")
        bench.wait_for_timeout(350)
        bench.fill("#gift", "1300")
        bench.select_option("#band-mobile", band)
        bench.wait_for_timeout(260)
        line = bench.evaluate("()=>document.getElementById('benefit').textContent")
        shown = bench.evaluate("()=>document.getElementById('saved').textContent")
        want_relief = hk(lo_s) + " – " + format(hi_s, ",")
        want_net = hk(1300 - hi_s) + " – " + format(1300 - lo_s, ",")
        errs = []
        if hk(1300) not in line:
            errs.append("does not name the gift figure")
        if "可全數扣稅" not in line:
            errs.append("uncapped band must say 可全數扣稅")
        if want_relief not in line:
            errs.append(f"want relief {want_relief!r} in {line!r}")
        if want_net not in line:
            errs.append(f"want net support {want_net!r} in {line!r}")
        if format(hi_s, ",") not in shown:
            errs.append(f"figures strip {shown!r} disagrees with {hi_s}")
        check(f"benefit sentence in band {band} computes both of its figures", errs)

    # the cap: a gift that DOES reach the 35% ceiling may not claim full deductibility
    bench.goto(f"{BASE}/embed/?part=calc")
    bench.wait_for_timeout(320)
    bench.select_option("#band-mobile", "r17")
    bench.fill("#gift", "175,000")
    bench.wait_for_timeout(280)
    line = bench.evaluate("()=>document.getElementById('benefit').textContent")
    strip = bench.evaluate("()=>document.getElementById('saved').textContent")
    cap2 = bench.evaluate("()=>document.getElementById('cap').textContent")
    errs = []
    if "35% 上限" not in line:
        errs.append("the capped sentence does not state the cap")
    if "可全數扣稅" in line:
        errs.append("the capped sentence still claims full deductibility")
    if "HK$29,750" not in strip:
        errs.append(f"figures strip {strip!r} lost the ceiling figure")
    if "42,500" in line or "42,500" in strip:
        errs.append("the old flat-multiplier overstatement is back")
    if "可全數扣除" in cap2:
        errs.append(f"capline claims full deductibility at the cap: {cap2!r}")
    check("benefit sentence and cap line follow the arithmetic when the 35% ceiling bites", errs)

    # ---------------------------------------------------------------- N · the HK$100 floor
    # The client's slide-1 note: the donation field has a minimum of HK$100.
    # Below it NO estimate is shown and her own line takes its place — and the
    # figure the donor typed is never silently clamped, because a clamp both hides
    # the problem and mis-states the gift.
    bench.goto(f"{BASE}/embed/?part=calc")
    bench.wait_for_timeout(350)
    bench.fill("#gift", "50")
    bench.wait_for_timeout(320)
    fl = bench.evaluate("""()=>({
        shown: !document.getElementById('min-note').hidden,
        line: document.getElementById('min-note').textContent,
        estimate: getComputedStyle(document.querySelector('#result .result')).display,
        benefit: getComputedStyle(document.getElementById('benefit')).display,
        typed: document.getElementById('gift').value
    })""")
    check("below HK$100 no estimate is shown and the client's own line replaces it",
          [] if (fl["shown"] and "捐款金額達到或超過 HK$100" in fl["line"]
                 and fl["estimate"] == "none" and fl["benefit"] == "none") else [str(fl)])
    check("below HK$100 the amount is not clamped — the donor keeps the figure they typed",
          [] if fl["typed"] == "50" else [f"field={fl['typed']!r}"])
    bench.fill("#gift", "100")
    bench.wait_for_timeout(320)
    fl2 = bench.evaluate("""()=>({
        minHidden: document.getElementById('min-note').hidden,
        estimate: getComputedStyle(document.querySelector('#result .result')).display,
        saved: document.getElementById('saved').textContent})""")
    check("HK$100 itself is inside the floor — the estimate comes back",
          [] if (fl2["minHidden"] and fl2["estimate"] != "none"
                 and fl2["saved"] == "HK$14 至 HK$17") else [str(fl2)])

    # ---------------------------------------------------------------- L · C2 declarations
    d = bench.evaluate("""()=>{
        const el=document.getElementById('disclaimer');
        const h=document.querySelector('#disclaimer h3');
        const li=document.querySelectorAll('#disclaimer .disc-list > li');
        const a=document.querySelector('#disclaimer .disc-list a');
        const out={scope:(document.querySelector('.scope')||{}).textContent||'',
                   spouse:(document.getElementById('spouse')||{}).textContent||'',
                   link:(document.querySelector('#receipt a[href="#disclaimer"]')||{}).textContent||'',
                   foot:(document.querySelector('.wrap > p.fine')||{}).textContent||'',
                   floorline:(document.getElementById('gift-min')||{}).textContent||'',
                   disc: el?el.textContent:'', visible:false, head:'', size:0,
                   ratio:0, items:0, listLink:''};
        if(!el || !h) return out;
        const rgb = s => (s.match(/[\\d.]+/g)||[]).slice(0,3).map(Number);
        const lum = c => { const f = v => { v/=255;
            return v<=.03928 ? v/12.92 : Math.pow((v+.055)/1.055,2.4); };
            return .2126*f(c[0])+.7152*f(c[1])+.0722*f(c[2]); };
        // the widget is transparent on purpose, so white is the honest ground
        let bg=[255,255,255], n=h;
        while(n){ const b=getComputedStyle(n).backgroundColor;
                  if(b && !/rgba\\(0, 0, 0, 0\\)|transparent/.test(b)){ bg=rgb(b); break; }
                  n=n.parentElement; }
        const cs=getComputedStyle(h), L1=lum(rgb(cs.color)), L2=lum(bg);
        out.head=h.textContent; out.size=parseFloat(cs.fontSize);
        out.ratio=Math.round((Math.max(L1,L2)+.05)/(Math.min(L1,L2)+.05)*100)/100;
        out.items=li.length; out.listLink=a?a.textContent:'';
        out.visible=el.getBoundingClientRect().height>0 && cs.display!=='none';
        return out;
    }""")
    # The client's slide-7 note removes the scope reminder beside the figures: the
    # single-person allowance is already stated once, where the income is chosen.
    # The check therefore asserts the REMOVAL and that the client's own disclaimer —
    # not our draft — is what now stands behind the numbers. Note for the record:
    # their approved text does not itself say "salaries tax only", so the widget no
    # longer states that scope anywhere; that is the client's call, flagged in
    # docs/CLIENT-COMMENTS-2-2026120.md rather than silently re-added.
    check("the result block no longer repeats the allowance/scope reminder (client instruction)",
          [] if not d["scope"] else [d["scope"][:80]])
    # 23 Nov: the client removed the spouse FAQ from the result block. The check is
    # inverted rather than deleted — a removed block that silently returns is exactly
    # the regression this line exists to catch.
    check("the spouse FAQ is absent from the result block (client instruction, 23 Nov)",
          [] if not d["spouse"].strip() else [d["spouse"][:80]])
    # 23 Nov: the disclaimer is no longer an accordion. The check moved from "is the
    # <summary> collapsed" to "is the title present, visible without a click, and
    # legible": the same intent (the legal block is there, readable, and names itself)
    # against the structure that now ships. Collapsed was the old contract; removing
    # the assertion instead would have left the heading and the fine print unmeasured.
    check("the disclaimer's title is present, visible and meets AA contrast", []
          if (d["visible"] and d["head"].strip() == "免責聲明:"
              and d["ratio"] >= 4.5 and d["size"] >= 12)
          else [f"visible={d['visible']} head={d['head']!r} "
                f"ratio={d['ratio']} size={d['size']}"])
    check("the disclaimer is a five-item list, and the consent line reaches it", []
          if (d["items"] == 5 and "免責聲明" in d["link"]
              and "最終以稅務局核定為準" in d["disc"]
              and "不會收集、記錄或儲存任何輸入資料" in d["disc"]
              and "不能取代專業意見" not in d["disc"])
          else [f"items={d['items']} link={d['link']!r} text={d['disc'][:120]!r}"])
    check("the HK$100 floor line is on the donation field, in the client's words",
          [] if "捐款金額達到或超過 HK$100 可獲得稅收減免。" in d["floorline"] else [d["floorline"][:80]])

    # ---------------------------------------------------------------- M · C4 tap targets
    # Measured per block, because the controls live in different blocks and a
    # hidden element cannot be measured (offsetParent === null is skipped).
    tap = []
    for bench_part in ("calc", "pay", "receipt"):
        bench.goto(f"{BASE}/embed/?part={bench_part}")
        bench.wait_for_timeout(320)
        tap += bench.evaluate("""()=>{
            const sels = ['#ref-help', '.seg label', '#band-mobile',
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

    # ---------------------------------------------------------------- O · the transaction-ID popover
    # The popover is the only overlay in the widget and the only place a real
    # transaction ID is pictured, so it carries four things worth failing on: the
    # disclosure contract (aria-expanded, real button), the overlay contract (inside
    # the frame, never full-screen), the assets (three captioned screenshots that
    # actually load — a lazy image in a hidden panel would otherwise never be
    # requested and a dead path would ship silently), and no keyboard trap.
    # Measured at the height the client actually declares for this block (990px zh,
    # 1185px en after the disclaimer became a list) — a generous 900px viewport
    # would have hidden the one failure mode that matters here, an overlay that
    # scrolls the host's fixed frame.
    for lang_q, frame_h in (("", 990), ("&lang=en", 1185)):
        pop = browser.new_page(viewport={"width": 390, "height": frame_h},
                               is_mobile=True, has_touch=True)
        pop.goto(f"{BASE}/embed/?part=receipt{lang_q}", wait_until="load")
        pop.wait_for_timeout(420)
        before = pop.evaluate("""()=>({
            hidden: document.getElementById('ref-help-panel').hidden,
            exp: document.getElementById('ref-help').getAttribute('aria-expanded'),
            tag: document.getElementById('ref-help').tagName,
            role: document.getElementById('ref-help-panel').getAttribute('role'),
            label: document.getElementById('ref-help').getAttribute('aria-label') || ''})""")
        pop.click("#ref-help")
        pop.wait_for_timeout(500)
        after = pop.evaluate("""()=>{
            const pop = document.getElementById('ref-help-panel');
            const r = pop.getBoundingClientRect(), d = document.documentElement;
            return {hidden: pop.hidden,
                    role: pop.getAttribute('role'),
                    exp: document.getElementById('ref-help').getAttribute('aria-expanded'),
                    w: Math.round(r.width), right: Math.round(r.right),
                    vw: d.clientWidth, vh: d.clientHeight, h: Math.round(r.height),
                    frame: Math.round(d.getBoundingClientRect().width),
                    scrolls: pop.scrollHeight > pop.clientHeight + 1,
                    overX: d.scrollWidth > d.clientWidth + 1,
                    steps: [...pop.querySelectorAll('.n')].map(n => n.textContent),
                    imgs: [...pop.querySelectorAll('img')].map(i => ({
                        src: i.getAttribute('src'), ok: i.complete && i.naturalWidth > 0,
                        alt: i.getAttribute('alt') || ''}))};
        }""")
        errs = []
        if before["tag"] != "BUTTON" or before["exp"] != "false" or not before["hidden"]:
            errs.append(f"closed state {before}")
        if not before["label"]:
            errs.append("the disclosure button has no accessible name")
        if after["role"] != "dialog":
            errs.append(f"panel role {after['role']!r}")
        if after["hidden"] or after["exp"] != "true":
            errs.append(f"open state {after}")
        if after["right"] > after["frame"] + 1 or after["overX"]:
            errs.append(f"panel escapes the frame: right {after['right']} of {after['frame']}")
        if after["h"] > after["vh"] * 0.75:
            errs.append(f"panel is {after['h']}px of a {after['vh']}px frame — a full-screen modal")
        # Two steps since the confirmation-screen capture was withdrawn: it carried
        # the donor's own avatar and a HK$1.00 test gift under an HK$100 minimum.
        if len(after["steps"]) != 2 or len(after["imgs"]) != 2:
            errs.append(f"steps {after['steps']} imgs {len(after['imgs'])}")
        if [t.strip() for t in after["steps"]] not in (["Step 1", "Step 2"], ["\u7b2c 1 \u6b65", "\u7b2c 2 \u6b65"]):
            errs.append(f"step labels {after['steps']}")
        bad_img = [i for i in after["imgs"] if not i["ok"] or not i["alt"]]
        if bad_img:
            errs.append(f"image not loaded or missing alt: {bad_img}")
        if not after["scrolls"]:
            errs.append("panel neither fits nor scrolls — it must do one")
        check(f"the reference popover opens as a dialog inside the frame{lang_q or ' (zh)'}", errs)
        # The panel is absolutely positioned, so opening it must not grow the
        # document — that is what keeps the client's fixed frame honest in the
        # open state, where a modal would have blown the declared height apart.
        pop.click("#ref-help")
        pop.wait_for_timeout(350)
        grown = pop.evaluate("""()=>{
            const pop = document.getElementById('ref-help-panel');
            const open = document.documentElement.scrollHeight;
            pop.hidden = true;
            const closed = document.documentElement.scrollHeight;
            pop.hidden = false;
            return {open: open, closed: closed};
        }""")
        check(f"opening the popover does not change the block height{lang_q or ' (zh)'}",
              [] if grown["open"] == grown["closed"] else [str(grown)])
        # Escape closes it and hands focus back to the button; Tab is NOT trapped.
        pop.keyboard.press("Escape")
        pop.wait_for_timeout(200)
        esc = pop.evaluate("()=>({hidden:document.getElementById('ref-help-panel').hidden,"
                           "focus:document.activeElement.id||document.activeElement.tagName})")
        check(f"Escape closes the popover and returns focus to its button{lang_q or ' (zh)'}",
              [] if (esc["hidden"] and esc["focus"] == "ref-help") else [str(esc)])
        pop.click("#ref-help")
        pop.wait_for_timeout(150)
        for _ in range(5):
            pop.keyboard.press("Tab")
        out = pop.evaluate("()=>document.activeElement.id||document.activeElement.tagName")
        check(f"the popover is not a keyboard trap (5 Tabs leave it){lang_q or ' (zh)'}",
              [] if out not in ("ref-help-panel", "") and out != "BODY" else [out])
        # and it must never scroll the host's fixed frame in the open state
        pop.click("#ref-help")
        pop.wait_for_timeout(300)
        openh = pop.evaluate("()=>document.documentElement.scrollHeight")
        check(f"the open popover stays inside the declared {frame_h}px frame{lang_q or ' (zh)'}",
              [] if openh <= frame_h else [f"document {openh}px > frame {frame_h}px"])
        pop.close()

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

    # ---------------------------------------------------------------- J · no third-party script, ever
    # The ?gtm= parameter used to load any GTM-XXXX id inside this origin; a GTM
    # container can run Custom HTML, so a crafted link became a PII harvester with
    # access to the donor's fields and the engine state. It is gone, and this test
    # fails the build if it comes back.
    pc = browser.new_page(viewport={"width": 390, "height": 900})
    pc.goto(f"{BASE}/embed/?part=input&gtm=GTM-ATTACK1", wait_until="load")
    pc.wait_for_timeout(900)
    g = pc.evaluate("""() => ({
        gtm: performance.getEntriesByType('resource')
               .map(r => r.name).filter(u => /googletagmanager|google-analytics/.test(u)),
        external: performance.getEntriesByType('resource')
               .map(r => r.name).filter(u => !u.startsWith(location.origin)),
        dbg: typeof window.__fhfPoc
      })""")
    errs = []
    if g["gtm"]:
        errs.append(f"third-party script loaded: {g['gtm']}")
    if g["external"]:
        errs.append(f"external requests: {g['external']}")
    if g["dbg"] != "undefined":
        errs.append(f"window.__fhfPoc is still exposed ({g['dbg']})")
    check("no ?gtm= escape hatch: no third-party script, no external request, no debug global", errs)
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
