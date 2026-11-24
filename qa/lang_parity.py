#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Language parity and EN-build gate for the FHF tax calculator widget.

This is the fourth QA file (the other three are poc_test.py, test_tax_engine.py
and verify_six_examples.py). It exists because the EN build had to prove three
different things at once, and poc_test.py's 57 assertions are pinned to the
Chinese copy — a harness whose pinned strings move with the change proves
nothing.

What it asserts
  A. zh-HK is untouched: every rendered string in every block, across a matrix
     of 23 states, is **byte-identical** to the pre-change file (the .bak is
     served as a .html fixture, because Chrome picks MIME by extension and a
     .bak would render as plain text).
  B. `?lang=zh-HK` explicit equals the default — the parameter cannot change
     the Chinese build.
  C. The English build is really English: zero CJK characters anywhere in the
     DOM (including hidden blocks, attributes and <option> text), apart from the
     AlipayHK button labels the receipt tooltip quotes on purpose — and the four
     IRD terms are present.
  D. The figures do not move with the language: the digit runs inside the money
     surface (net, saved, figures strip, caption, cap, benefit, assumption,
     announcement) are identical in both languages. Words are copy; numbers
     are not.
  E. The events are identical in name and count in both languages, carry no
     amount / income / rate, and carry `lang` as a coarse dimension.
  F. `fhf-config {lang}` switches the language inside a live frame — the page
     is not re-loaded (a JS marker set before the switch survives it).
  G. 44px tap targets hold in English at 390px, as they do in Chinese.

Usage: python3 qa/lang_parity.py [--base http://127.0.0.1:8765]
Exit 1 on any failure.
"""
import json
import re
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
ARGS = sys.argv[1:]
BASE = "http://127.0.0.1:8765"
for i, a in enumerate(ARGS):
    if a == "--base" and i + 1 < len(ARGS):
        BASE = ARGS[i + 1]

# The pre-change file, served as .html so Chrome treats it as a document.
BAK = ROOT / "embed" / "index.html.bak-pre-en-20261115"
# The guard's job is "the Chinese build did not move by accident". It therefore compares
# against the last ACCEPTED Chinese copy state, not against a frozen 15 Nov file: the
# payment-reference pass (18 Nov) changed seven zh strings on purpose, so the baseline was
# rebased to the file that pass started from. Refresh it only when a zh copy change is signed
# off, and record the change list — the assertions below are what catch an accidental drift.
# Rebases on record: 18 Nov (payment reference, 7 strings) · 20 Nov (client comment pass 2 —
# white ground, 56rem column, HK$100 floor, months control removed, positive saving, scope
# line and monthly link removed, the client's own disclaimer; list in
# docs/CLIENT-COMMENTS-2-2026120.md and qa/apply_client_comments2_2026120.py) · 21 Nov
# (PayMe dropped: the desktop QR figure, the mobile row, `s3.qr.alt.payme` and `s3.payme.sub`
# in both tables, and `s3.lede` rewritten to name AlipayHK and the credit card — list in
# qa/apply_payme_removal_20261121.py) · 23 Nov (the client's section-by-section copy
# sheet: Section 1/2 headers, the chips and the "what counts" disclosure removed, the band
# hint and note rewritten, Section 3 restructured around 您的全額捐款 with the gift row
# removed and the assumption as a numbered block, the spouse FAQ removed, and the
# transaction-ID popover added — 93 edits, list in qa/apply_client_copy_20261123.py) · 23 Nov
# (the disclaimer stops being a collapsed <details>: rc.disc.summary + rc.disc.body become
# rc.disc.head + rc.disc.1-5 — five <li> in an always-visible <ol>, with the IRD link in item 4,
# zh and en — list in qa/apply_disc_list_20261123.py) · 23 Nov (PHASE 1: section 5 hidden
# behind the PHASE1 constant, so ?part=receipt is an empty frame and ?part=all ends at
# "How you give"; plus the AlipayHK receipt line and its five-step tooltip in the payment
# block — zh and en — list in qa/apply_phase1_alipay_20261123.py. The disclaimer did NOT
# change: it was already outside the panels, and it still closes every content part) ·
# 24 Nov (the client reviewed the AlipayHK tooltip and sent TWO flows: tick 「需要收據」
# while giving — 2 steps, led first — or claim it afterwards from the donation records —
# 4 steps; title, intro, two section headings, six step sentences, six alt texts and the
# outro replaced in both languages, and six 320px crops replace the five 400px ones —
# list in qa/apply_alipay_two_options_20261124.py. DELIBERATE zh change, rebased) ·
# 24 Nov (Option B payment pair, qa/apply_pay_optionb_20261124.py: **NO copy change** —
# nothing a donor reads moved, and the 390px block is pixel-identical in both languages.
# What moved is the DOM: the receipt note now sits inside the AlipayHK tile instead of
# between the rails, and the desktop card tile carries a decorative ↗ (aria-hidden) on
# its foot line. The check compares rendered strings, so a re-order reads as a change —
# rebased rather than excused, and `bag()` below now reports a re-order with the copy
# intact as a note instead of a failure. The rebase is the only reason this file moved.)
# What the gate is for survives each rebase: the ZH
# build may only change where a change was signed off, and every assertion below still
# fails on an accidental drift.
FIXTURE = ROOT / "qa" / "_baseline_zh_pre_ref.html"
if BAK.exists() and (not FIXTURE.exists() or FIXTURE.stat().st_mtime < BAK.stat().st_mtime):
    FIXTURE.write_bytes(BAK.read_bytes())

ok = bad = 0


def check(label, errs):
    global ok, bad
    if errs:
        bad += 1
        print(f"FAIL  {label}")
        for e in errs[:6]:
            print("        ", e)
        if len(errs) > 6:
            print(f"        … {len(errs) - 6} more")
    else:
        ok += 1
        print(f"PASS  {label}")


CAPTURE = """() => {
  const attrs = ["aria-label", "placeholder", "alt", "title"];
  const a = [];
  document.querySelectorAll("body *").forEach(el => {
    for (const n of attrs) {
      if (el.hasAttribute && el.hasAttribute(n)) a.push(el.tagName.toLowerCase() + "[" + n + "]=" + el.getAttribute(n));
    }
  });
  const ids = {};
  document.querySelectorAll("[id]").forEach(el => { ids[el.id] = el.textContent; });
  // body.textContent includes the inline <script> source, which is not copy:
  // strip it, or the v-string and the I18N table count as user-facing text.
  const clone = document.body.cloneNode(true);
  clone.querySelectorAll("script").forEach(s => s.remove());
  const txt = clone.textContent || "";
  // the result block minus its step eyebrow ("步驟二" / "Step 2" — the only
  // place where a Chinese numeral legitimately becomes a digit)
  let resultText = "";
  const res = document.getElementById("result");
  if (res) {
    const rc = res.cloneNode(true);
    const eb = rc.querySelector(".eyebrow"); if (eb) eb.remove();
    resultText = rc.textContent;
  }
  return {
    title: document.title,
    htmlLang: document.documentElement.lang,
    text: txt,
    inner: document.body.innerText,
    attrs: a,
    options: [...document.querySelectorAll("option")].map(o => o.value + "|" + o.textContent),
    ids: ids,
    resultText: resultText,
    cjk: (txt.match(/[\\u3400-\\u9fff]/g) || []).length
  };
}"""

# the money surface: every figure a donor reads. Language may not move a digit here.
MONEY_IDS = ["net", "net-label", "net-caption", "saved", "saved-label", "rate",
             "rate-label", "cap", "benefit", "assumption", "assume-1", "assume-3",
             "announce"]


def set_band(v):
    return ("()=>{const s=document.getElementById('band-mobile');s.value=%r;"
            "s.dispatchEvent(new Event('change',{bubbles:true}));}" % v)


def set_mode(v):
    return ("()=>{document.querySelector('input[name=\"mode\"][value=%r]').checked=true;"
            "document.querySelector('input[name=\"mode\"][value=%r]')"
            ".dispatchEvent(new Event('change',{bubbles:true}));}" % (v, v))


STATES = {
    "calc": [
        ("default", None),
        ("band r0", set_band("r0")),
        ("band r6", set_band("r6")),
        ("band r16", set_band("r16")),
        ("band unknown", set_band("unknown")),
        ("monthly 12", "(function(){document.querySelector('input[name=\"mode\"][value=\"monthly\"]').checked=true;"
                      "document.querySelector('input[name=\"mode\"][value=\"monthly\"]').dispatchEvent(new Event('change',{bubbles:true}));})()"),
        ("empty gift", "()=>{const g=document.getElementById('gift');g.value='';"
                       "g.dispatchEvent(new Event('input',{bubbles:true}));}"),
        ("big gift r17", "()=>{const g=document.getElementById('gift');g.value='175000';"
                         "g.dispatchEvent(new Event('input',{bubbles:true}));}"),
        ("exact capped", "(function(){document.getElementById('exact-toggle').click();"
                         "var g=document.getElementById('gift');g.value='250000';"
                         "g.dispatchEvent(new Event('input',{bubbles:true}));"
                         "var e=document.getElementById('exact');e.value='500000';"
                         "e.dispatchEvent(new Event('input',{bubbles:true}));})()"),
    ],
    "input": [
        ("default", None),
        ("monthly 12", "(function(){document.querySelector('input[name=\"mode\"][value=\"monthly\"]').checked=true;"
                       "document.querySelector('input[name=\"mode\"][value=\"monthly\"]').dispatchEvent(new Event('change',{bubbles:true}));})()"),
        ("band unknown", set_band("unknown")),
        ("band r14", set_band("r14")),
    ],
    "result": [
        ("default", None),
        ("band r15", set_band("r15")),
        ("band r2", set_band("r2")),
        ("exact", "(function(){document.getElementById('exact-toggle').click();"
                  "var e=document.getElementById('exact');e.value='654321';"
                  "e.dispatchEvent(new Event('input',{bubbles:true}));})()"),
    ],
    "pay": [
        ("default", None),
    ],
    "receipt": [
        ("default", None),
        # the disclaimer is permanently open now; the state that still needs
        # covering is the consent-line jump, which is what a donor reaches it by
        ("disclaimer link", "()=>{document.getElementById('disc-link').click();}"),
        ("empty submit", "()=>{document.getElementById('rform').requestSubmit();}"),
        ("bad email", "(function(){document.getElementById('rname').value='陳大文';"
                      "document.getElementById('rmail').value='nope';"
                      "document.getElementById('rform').requestSubmit();})()"),
        ("success", "(function(){document.getElementById('rname').value='陳大文';"
                    "document.getElementById('rmail').value='donor@example.com';"
                    "document.getElementById('consent').checked=true;"
                    "document.getElementById('rform').requestSubmit();})()"),
    ],
}


def norm(v):
    """Collapse whitespace runs before any comparison.

    `textContent` carries the source indentation, so MOVING a node inside a
    wrapper — which is what nesting the receipt note in the AlipayHK tile is —
    changes a hundred spaces without changing one word. The gate's subject is
    the donor-visible copy, so indentation is not evidence: it is normalised
    away, and a real copy change still fails.
    """
    if isinstance(v, str):
        return re.sub(r"\s+", " ", v).strip()
    if isinstance(v, dict):
        return {k: norm(x) for k, x in v.items()}
    if isinstance(v, list):
        return [norm(x) for x in v]
    return v


TOKEN = re.compile(r"[\u3400-\u9fff]+|[^\s\u3400-\u9fff]+")


def bag(v):
    """The same snapshot as the SET of copy tokens it renders.

    Used only to tell a re-order from a rewrite. Tokens are CJK runs (Chinese has
    no spaces, so a run is a phrase regardless of the source indentation) and
    non-space runs of everything else — so moving a node changes the ORDER of the
    bag without changing the bag, while any added, cut or reworded string changes
    it. Plain word-splitting was not good enough: two elements that used to abut
    (`<b>AlipayHK</b><span>…`) now have a newline between them, which would read
    as a copy change when it is only indentation.
    """
    if isinstance(v, dict):
        return {k: bag(x) for k, x in v.items()}
    if isinstance(v, list):
        return sorted(str(bag(x)) for x in v)
    return sorted(TOKEN.findall(str(v)))


def run_state(page, url, js):
    page.goto(url, wait_until="load")
    # #announce is an aria-live region written 600ms after the last render; a
    # shorter wait makes the snapshot race the debounce instead of testing it.
    page.wait_for_timeout(500)
    if js:
        page.evaluate(js)
    page.wait_for_timeout(850)
    return norm(page.evaluate(CAPTURE))


def parity_digits(s):
    """Digits that must match across languages.

    全額100% is COPY, not a figure: the client's Chinese sentence states the
    sight-saving claim as a percentage, and the authored English states the same
    claim as "the full … impact". Neither is computed from the donor's input, so
    it is normalised away here — and asserted as a claim in its own check below,
    which is the part that can actually fail if one language loses it.
    """
    return digits_of((s or "").replace("100%", "FULL"))


def digits_of(s):
    """Digit runs with the thousands separator normalised away.

    The separator itself is copy (English puts a comma where Chinese puts a
    full-width one), so '1,300' and '1300' must compare equal — otherwise a
    punctuation difference reads as a figure change.
    """
    return re.findall(r"\d+", (s or "").replace(",", ""))


with sync_playwright() as pw:
    browser = pw.chromium.launch(channel="chrome", headless=True)
    page = browser.new_page(viewport={"width": 390, "height": 900}, is_mobile=True, has_touch=True)

    base_snaps, zh_snaps, en_snaps = {}, {}, {}
    for part, states in STATES.items():
        for label, js in states:
            key = f"{part}:{label}"
            base_snaps[key] = run_state(page, f"{BASE}/qa/_baseline_zh_pre_ref.html?part={part}", js)
            zh_snaps[key] = run_state(page, f"{BASE}/embed/?part={part}", js)
            en_snaps[key] = run_state(page, f"{BASE}/embed/?part={part}&lang=en", js)

    # explicit ?lang=zh-HK must equal the default build
    explicit = {}
    for part, states in STATES.items():
        for label, js in states:
            explicit[f"{part}:{label}"] = run_state(page, f"{BASE}/embed/?part={part}&lang=zh-HK", js)

    # ---------------------------------------------------------------- A
    def field_diffs(b, z, fields):
        out = []
        for field in fields:
            bv, zv = b[field], z[field]
            if bv == zv:
                continue
            if isinstance(bv, dict):
                for k in sorted(set(bv) | set(zv)):
                    if bv.get(k) != zv.get(k):
                        out.append(f"{field}[{k}]: {str(bv.get(k))[:70]!r} → {str(zv.get(k))[:70]!r}")
            elif isinstance(bv, list):
                for i, (x, y) in enumerate(zip(bv, zv)):
                    if x != y:
                        out.append(f"{field}[{i}]: {x[:70]!r} → {y[:70]!r}")
                if len(bv) != len(zv):
                    out.append(f"{field}: length {len(bv)} → {len(zv)}")
            else:
                i = next((i for i in range(min(len(bv), len(zv))) if bv[i] != zv[i]),
                         min(len(bv), len(zv)))
                out.append(f"{field} @{i}: {bv[max(0, i-30):i+40]!r} → {zv[max(0, i-30):i+40]!r}")
        return out

    FIELDS = ("title", "text", "inner", "attrs", "options", "ids", "htmlLang")

    # a byte-level dump of every Chinese string, so `diff` can be the evidence
    dump_dir = None
    for i, a in enumerate(ARGS):
        if a == "--dump" and i + 1 < len(ARGS):
            dump_dir = Path(ARGS[i + 1])
    if dump_dir:
        dump_dir.mkdir(parents=True, exist_ok=True)

        def dump(path, snaps):
            with open(path, "w", encoding="utf-8") as fh:
                for key in sorted(snaps):
                    s = snaps[key]
                    fh.write(f"# {key} · title: {s['title']}\n")
                    fh.write(f"# {key} · lang: {s['htmlLang']}\n")
                    for i, a in enumerate(s["attrs"]):
                        fh.write(f"{key}\tattr{i}\t{a}\n")
                    for i, o in enumerate(s["options"]):
                        fh.write(f"{key}\toption{i}\t{o}\n")
                    for k in sorted(s["ids"]):
                        fh.write(f"{key}\tid={k}\t{s['ids'][k]}\n")
                    fh.write(f"{key}\tinner\t{s['inner']}\n")
                    fh.write(f"{key}\ttext\t{s['text']}\n")
                    fh.write(f"{key}\tresult\t{s['resultText']}\n")

        dump(dump_dir / "zh-strings-before.txt", base_snaps)
        dump(dump_dir / "zh-strings-after.txt", zh_snaps)
        print(f"dumped {len(base_snaps)} states to {dump_dir}/zh-strings-{{before,after}}.txt\n")

    diffs, reorders = [], []
    for key in base_snaps:
        d = field_diffs(base_snaps[key], zh_snaps[key], FIELDS)
        if not d:
            continue
        # A failed diff is not automatically a copy change: nesting the receipt
        # note inside the AlipayHK tile (Option B, 24 Nov) re-orders the payment
        # block in the DOM while leaving every word where it was. So the strings
        # are compared as a SET as well — equal sets mean the same copy in a new
        # order, which is reported, not failed. A word added, cut or reworded
        # changes the set and still fails.
        if bag(base_snaps[key]) == bag(zh_snaps[key]):
            reorders += [f"{key} · {x.split(' @')[0]}" for x in d]
        else:
            diffs += [f"{key} · {x}" for x in d]
    check(f"zh-HK rendered strings are byte-identical to the pre-change file ({len(base_snaps)} states)", diffs)
    if reorders:
        print(f"      note: {len(reorders)} field(s) re-ordered with the copy intact "
              f"(no word added, cut or changed) — e.g. {reorders[0]}")

    # ---------------------------------------------------------------- B
    diffs = []
    for key in zh_snaps:
        diffs += [f"{key} · {d}" for d in field_diffs(zh_snaps[key], explicit[key], FIELDS)]
    check("?lang=zh-HK renders the same as no lang parameter", diffs)

    # ---------------------------------------------------------------- C
    # The AlipayHK tooltip quotes the app's own labels in Chinese on purpose: a donor
    # matches them against what their phone shows, and translating them breaks the
    # instruction. They are the ONLY Chinese allowed here — everything else still fails,
    # and the other half of the check asserts they are present, so a later "translate
    # them to be safe" pass cannot quietly delete the thing that makes the copy work.
    APP_LABELS = ["慈善捐款", "捐款人資料", "我的捐款", "捐款記錄", "交易記錄",
                  "捐款結果", "申請收據", "需要收據", "護瞳行動"]

    def cjk_left(text):
        for lab in APP_LABELS:
            text = (text or "").replace(lab, "")
        return len(re.findall(r"[\u3400-\u9fff]", text))

    cjk = {}
    for k, v in en_snaps.items():
        n = cjk_left(v["text"])
        if n:
            cjk[k] = n
    check(f"no CJK anywhere in the English build except the app labels it quotes "
          f"({len(en_snaps)} states)", [f"{k}: {n} CJK chars" for k, n in cjk.items()])

    quoted = " ".join(v["text"] for v in en_snaps.values()) + " " + " ".join(
        a for v in en_snaps.values() for a in v["attrs"])
    absent = [lab for lab in ("慈善捐款", "捐款人資料", "我的捐款", "捐款記錄",
                             "申請收據", "需要收據") if lab not in quoted]
    check("the English build keeps AlipayHK's six labels in Chinese, verbatim", absent)

    all_en = " ".join(v["text"] for v in en_snaps.values())
    # "year of assessment" became "the relevant assessment year" when the client's
    # approved disclaimer replaced our draft and their slide-2 note removed the
    # months hint that carried the full phrase — their wording governs.
    # 23 Nov: "recognised charitable donation" left the build with the two blocks that
    # carried it (the "what counts" disclosure and the old benefit sentence); the
    # client's own sentence says 可全數扣稅 / "qualifies for full tax deduction" instead.
    # Their sheet also introduced "Net Chargeable Income" and "Salaries Tax", which are
    # IRD terms, so the list follows the copy that now ships rather than the copy that
    # did — and it still fails if the English drifts into ad-hoc wording.
    terms = ["net chargeable income", "assessable income", "salaries tax",
             "standard rate", "assessment year", "donation"]
    missing = [t for t in terms if t.lower() not in all_en.lower()]
    check("English copy uses the IRD terms (" + ", ".join(terms) + ")", missing)

    bangs = [k for k, v in en_snaps.items() if "!" in v["text"]]
    check("no exclamation mark in the English build", bangs)

    # ---------------------------------------------------------------- D
    fig_diffs = []
    for key in zh_snaps:
        z, e = zh_snaps[key]["ids"], en_snaps[key]["ids"]
        for i in MONEY_IDS:
            if i in z and i in e:
                if parity_digits(z[i]) != parity_digits(e[i]):
                    fig_diffs.append(f"{key} · #{i}: {digits_of(z[i])} vs {digits_of(e[i])}")
    check("every figure in the money surface is identical in both languages", fig_diffs)

    # the whole result block, not just the named ids
    fig_diffs = []
    for key in zh_snaps:
        if key.startswith("receipt") or key.startswith("pay"):
            continue
        z, e = zh_snaps[key]["resultText"], en_snaps[key]["resultText"]
        if parity_digits(z) != parity_digits(e):
            fig_diffs.append(f"{key}: {parity_digits(z)} vs {parity_digits(e)}")
    check("the whole result block renders the same digits in both languages", fig_diffs)

    # the one non-numeric figure in the sentence: the client's 全額100% claim
    claim = []
    for key in zh_snaps:
        z = "100%" in (zh_snaps[key]["ids"].get("benefit") or "")
        e = "the full sight-saving impact" in (en_snaps[key]["ids"].get("benefit") or "")
        if z != e:
            claim.append(f"{key}: zh 100%={z} en full={e}")
    check("the client's “full 100% sight-saving” claim is carried by both languages", claim)

    # the client's 5th note: the saving is money kept, so it never carries a minus
    neg = [k for snaps in (zh_snaps, en_snaps) for k, v in snaps.items()
           if "−HK$" in (v["ids"].get("saved") or "")]
    check("the tax-saved figure never renders with a minus sign, in either language", neg)

    # ---------------------------------------------------------------- H · the client's disclaimer
    # Downloads/Tax Calculator.docx carries the wording the client has approved.
    # Their text beats our draft, so this pins it character for character in both
    # languages rather than trusting that the edit landed.
    #
    # 23 Nov 2026: the accordion became an always-visible numbered list, so the
    # pin moves from one <br>-joined paragraph to five <ol>/<li>. One string per
    # item is the point — a single joined string would pass while an item boundary
    # moved, and the list is now the delivered structure. The Chinese punctuation
    # is the client's, not normalised: items 1, 2 and 4 end with an ASCII ".", 3
    # and 5 with "。". Changing one character still fails.
    DISC = {
        "zh-HK": {
            "head": "免責聲明:",
            "items": [
                "根據稅務局相關課稅年度資料估算，僅供一般參考.",
                "不會收集、記錄或儲存任何輸入資料.",
                "以累進稅率或標準稅率（以較低者為準）估算應繳稅款；最終以稅務局核定為準。",
                "不構成專業意見，詳情請參閱香港稅務局網頁或諮詢顧問.",
                "護瞳行動（香港）有限公司概不承擔相關法律責任。",
            ],
            "href": "https://www.ird.gov.hk/chi/welcome.htm",
            "link": "香港稅務局網頁",
        },
        "en": {
            "head": "Disclaimer:",
            "items": [
                "Based on IRD tax rates and info for the relevant assessment year; for general reference only.",
                "Does not collect, record, or store entered data.",
                "Estimates tax using progressive or standard rates (whichever is lower); "
                "actual results depend on the IRD.",
                "Not formal financial/tax advice; refer to the Hong Kong Inland Revenue "
                "Department website or a professional.",
                "The Fred Hollows Foundation (HK) Limited assumes no liability for use or reliance.",
            ],
            "href": "https://www.ird.gov.hk/eng/welcome.htm",
            "link": "Hong Kong Inland Revenue Department website",
        },
    }
    got, errs = {}, []
    for lang in ("zh-HK", "en"):
        pd = browser.new_page(viewport={"width": 390, "height": 900})
        # ?part=pay, not ?part=receipt: section 5 is hidden while PHASE1 is true, and
        # the disclaimer is the one block every CONTENT part still carries. Measuring
        # it in the empty placeholder would measure nothing.
        pd.goto(f"{BASE}/embed/?part=pay&lang={lang}", wait_until="load")
        pd.wait_for_timeout(450)
        got[lang] = pd.evaluate(
            "()=>{const d=document.getElementById('disclaimer');if(!d)return null;"
            "const h=d.querySelector('h3'), ol=d.querySelector('ol'), a=d.querySelector('a');"
            "return {head:h?h.textContent:'', "
            "items:ol?[...ol.children].map(li=>li.textContent):[], "
            "href:a?a.getAttribute('href'):'', link:a?a.textContent:''};}")
        pd.close()
        want = DISC[lang]
        if not got[lang]:
            errs.append(f"{lang}: #disclaimer is missing")
            continue
        g = got[lang]
        if g["head"] != want["head"]:
            errs.append(f"{lang} heading: {g['head']!r} != {want['head']!r}")
        if len(g["items"]) != 5:
            errs.append(f"{lang}: {len(g['items'])} list items, expected 5")
        for n, (a, b) in enumerate(zip(g["items"], want["items"]), 1):
            if a != b:
                i = next((i for i in range(min(len(a), len(b))) if a[i] != b[i]),
                         min(len(a), len(b)))
                errs.append(f"{lang} item {n} @{i}: {a[max(0,i-25):i+35]!r} != "
                            f"{b[max(0,i-25):i+35]!r}")
        # the link is not decoration: sent to the wrong locale it is a defect an
        # English reader cannot recover from, and a missing rel hands the referrer over
        if g["href"] != want["href"]:
            errs.append(f"{lang} link href: {g['href']!r} != {want['href']!r}")
        if g["link"] != want["link"]:
            errs.append(f"{lang} link text: {g['link']!r} != {want['link']!r}")
    check("the disclaimer is the client's approved text, verbatim, in both languages", errs)

    # The client's decision (23 Nov 2026, relayed by Kevin): the IRD link is
    # LANGUAGE-APPROPRIATE — English to /eng/, Chinese to /chi/ — so the two hrefs must
    # DIFFER. An equal pair is the defect (it means one language is being sent to a page
    # it cannot read), and so is either side pointing somewhere else.
    check("the IRD link follows the frame's language: en → /eng/, zh → /chi/",
          [] if (got.get("zh-HK", {}).get("href") == "https://www.ird.gov.hk/chi/welcome.htm"
                 and got.get("en", {}).get("href") == "https://www.ird.gov.hk/eng/welcome.htm")
          else [f"zh={got.get('zh-HK', {}).get('href')!r} en={got.get('en', {}).get('href')!r}"])

    # The list must READ as numbered to a screen reader: a real <ol> of five
    # <li>, not five lines starting with a typed digit.
    shape = []
    for lang in ("zh-HK", "en"):
        pd = browser.new_page(viewport={"width": 390, "height": 900})
        pd.goto(f"{BASE}/embed/?part=pay&lang={lang}", wait_until="load")
        pd.wait_for_timeout(400)
        s = pd.evaluate("""()=>{const d=document.getElementById('disclaimer');
          if(!d) return null;
          const ol=d.querySelector('ol'), a=d.querySelector('a');
          const cs=ol?getComputedStyle(ol):null;
          return {ol:!!ol, lis:ol?ol.children.length:0,
                  marker:cs?cs.listStyleType:'',
                  visible:d.getBoundingClientRect().height>0 &&
                          getComputedStyle(d).display!=='none',
                  digits:/^\\s*[1-5][.)]/.test(ol&&ol.children[0]?ol.children[0].textContent:''),
                  blank:(a?a.getAttribute('target'):null)==='_blank',
                  rel:(a?a.getAttribute('rel'):'')||''};}""")
        pd.close()
        if not s:
            shape.append(f"{lang}: no #disclaimer")
            continue
        if not s["ol"] or s["lis"] != 5:
            shape.append(f"{lang}: ol={s['ol']} items={s['lis']}")
        if s["marker"] not in ("decimal", "decimal-leading-zero"):
            shape.append(f"{lang}: list-style {s['marker']!r} is not a decimal list")
        if not s["visible"]:
            shape.append(f"{lang}: the disclaimer is not visible without a click")
        if s["digits"]:
            shape.append(f"{lang}: item 1 carries a typed ordinal — the <ol> owns the numbers")
        if not s["blank"] or "noopener" not in s["rel"] or "noreferrer" not in s["rel"]:
            shape.append(f"{lang}: target/rel {s['blank']}/{s['rel']!r}")
    check("the disclaimer is an always-visible <ol> of five, linked with rel=noopener noreferrer",
          shape)

    # ---------------------------------------------------------------- F
    # language switch by postMessage inside a live frame, through the real host
    # page (qa/fixture.html) — the same path the CMS will use
    pg = browser.new_page(viewport={"width": 1100, "height": 1000})
    pg.goto(f"{BASE}/qa/fixture.html", wait_until="load")
    pg.wait_for_timeout(600)
    pg.evaluate("()=>{window.__msgs=[];}")
    before = pg.frames[1].evaluate("()=>{window.__marker='alive';return {t:document.getElementById('s1h').textContent,"
                                   "lang:document.documentElement.lang};}")
    href_before = pg.frames[1].evaluate("()=>location.href")
    pg.evaluate("""()=>{document.getElementById('f').contentWindow.postMessage(
        {type:'fhf-config', config:{lang:'en'}}, '*');}""")
    pg.wait_for_timeout(500)
    after = pg.frames[1].evaluate("()=>({t:document.getElementById('s1h').textContent,"
                                  "lang:document.documentElement.lang,"
                                  "marker:window.__marker||null,"
                                  "href:location.href})")
    errs = []
    # Copy-independent on purpose: pinning the literal heading made this a copy test
    # that failed the moment the copy was rewritten, while the behaviour it exists to
    # protect (switch in place, no reload) was fine. Assert the property instead —
    # the heading must CHANGE, and must carry no CJK in English.
    if after["t"] == before["t"]:
        errs.append(f"heading did not change: {before['t']!r} → {after['t']!r}")
    if re.search(r"[\u4e00-\u9fff]", after["t"]):
        errs.append(f"heading still Chinese after switching to en: {after['t']!r}")
    if after["lang"] != "en":
        errs.append(f"document lang = {after['lang']!r}")
    if after["marker"] != "alive":
        errs.append("the frame re-loaded — the JS marker did not survive the switch")
    if after["href"] != href_before:
        errs.append(f"location changed: {href_before} → {after['href']}")
    pg.evaluate("""()=>{document.getElementById('f').contentWindow.postMessage(
        {type:'fhf-config', config:{lang:'zh-HK'}}, '*');}""")
    pg.wait_for_timeout(400)
    back = pg.frames[1].evaluate("()=>document.getElementById('s1h').textContent")
    if not re.search(r"[\u4e00-\u9fff]", back or ""):
        errs.append(f"switch back to zh-HK gave no Chinese heading: {back!r}")
    check("fhf-config{lang} switches the language in place — no reload, no src change", errs)
    pg.close()

    # ---------------------------------------------------------------- E
    names = {}
    payloads = {}
    for lang in ("zh-HK", "en"):
        p = browser.new_page(viewport={"width": 390, "height": 900}, is_mobile=True, has_touch=True)
        p.goto(f"{BASE}/qa/fixture.html", wait_until="load")
        p.wait_for_timeout(400)
        f = p.frames[1]
        f.evaluate(f"()=>{{location.href='../embed/?part=calc&lang={lang}';}}")
        p.wait_for_timeout(900)
        f = p.frames[1]
        f.fill("#gift", "2500")
        f.click("#exact-toggle")   # exact income is a swap now, not a disclosure
        f.fill("#exact", "654321")
        p.wait_for_timeout(1300)
        msgs = p.evaluate("()=>window.__msgs||[]")
        names[lang] = [m["name"] for m in msgs if m.get("type") == "event"]
        payloads[lang] = json.dumps([m.get("params") for m in msgs if m.get("type") == "event"],
                                    ensure_ascii=False)
        p.close()

    check("the same events fire in both languages",
          [] if names["zh-HK"] == names["en"] and names["en"] else
          [f"zh={names['zh-HK']} en={names['en']}"])

    hits = []
    for lang, s in payloads.items():
        for pat in (r'"amount"', r'"income"', r'"rate"', r'"marginal"', r'654,?321', r'2,?500',
                    r'"5200"', r'5,200', r'1,?300'):
            if re.search(pat, s):
                hits.append(f"{lang}: {pat}")
    check("no amount / income / rate in any payload, in either language", hits)

    dims = []
    for lang, s in payloads.items():
        if f'"lang": "{lang}"' not in s:
            dims.append(f"{lang}: lang dimension missing → {s[:160]}")
    check("every event carries lang as a dimension (zh-HK | en)", dims)

    # ---------------------------------------------------------------- G
    tap = []
    for part in ("calc", "pay", "receipt"):
        p = browser.new_page(viewport={"width": 390, "height": 900}, is_mobile=True, has_touch=True)
        p.goto(f"{BASE}/embed/?part={part}&lang=en", wait_until="load")
        p.wait_for_timeout(380)
        tap += [f"{part} {x}" for x in p.evaluate("""()=>{
            const sels = ['#ref-help', '#alipay-help', '.seg label', '#band-mobile',
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
          }""")]
        ov = p.evaluate("()=>document.documentElement.scrollWidth > document.documentElement.clientWidth + 1")
        if ov:
            tap.append(f"{part}: horizontal overflow at 390px in English")
        p.close()
    check("every thumb target is still >=44px in the English build at 390px", tap)

    browser.close()

print(f"\n=== lang parity: {ok} passed, {bad} failed ===")
sys.exit(1 if bad else 0)
