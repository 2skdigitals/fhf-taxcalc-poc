#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hard-rule QA for the calm redesign.

Checks, in order:
  1  tax engine is byte-identical to embed/index.html
  2  the English build renders zero CJK characters
  3  every key used in the DOM exists in both tables, and both tables hold the
     same key set (parity)
  4  the Chinese table uses no spoken particles
  5  every required fact is still present, in both languages
  6  every interactive control is >= 44px tall
  7  no horizontal overflow at 320 / 390 / 568 / 768 / 1280
  8  no new external requests: no <img>, no webfonts, no CDN; outbound links
     point at hollows.org only
  9  the receipt form still has name + email + payment reference + consent
 10  the height sweep: 22 widths, both languages, every part
"""
import hashlib, json, re, sys
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8766/index.html"
ORIG = "../../embed/index.html"
SRC = "index.html"
I18N = json.load(open("_new_i18n.json", encoding="utf-8"))
ENGINE_RE = re.compile(r"(/\* FHF_TAX_ENGINE_START \*/.*?/\* FHF_TAX_ENGINE_END \*/)", re.S)

fails, warns = [], []


def ok(cond, label, detail=""):
    print(("  ok   " if cond else "  FAIL ") + label + (("  — " + detail) if detail and not cond else ""))
    if not cond:
        fails.append(label + (" — " + detail if detail else ""))


print("\n1 · tax engine untouched")
a = hashlib.sha256(ENGINE_RE.search(open(SRC, encoding="utf-8").read()).group(1).encode()).hexdigest()
b = hashlib.sha256(ENGINE_RE.search(open(ORIG, encoding="utf-8").read()).group(1).encode()).hexdigest()
ok(a == b, "engine sha256 matches embed/index.html", a + " vs " + b)

print("\n2–5 · copy tables")
ok(set(I18N["zh-HK"]) == set(I18N["en"]),
   "both tables hold the same keys", str(set(I18N["zh-HK"]) ^ set(I18N["en"])))
parts = open(SRC, encoding="utf-8").read()
used = set(re.findall(r'data-i18n(?:-html|-ph|-aria|-alt)?="([^"]+)"', parts))
missing = sorted(k for k in used if k not in I18N["en"] or k not in I18N["zh-HK"])
ok(not missing, "every data-i18n key exists in both tables", ", ".join(missing))
ok(not re.search(r"[\u3400-\u9fff\uf900-\ufaff]", json.dumps(I18N["en"], ensure_ascii=False)),
   "English table holds no CJK")
bad = [k for k, v in I18N["zh-HK"].items() if re.search(r"[嘅咗喺冇唔慳嘢啲喎咁]", v)]
ok(not bad, "Chinese table holds no spoken particles", ", ".join(bad))

print("\n6–9 · rendered checks")
FACTS = {
    "35% cap":            ("35%", "35%"),
    "HK$100 receipt":     ("HK$100", "HK$100"),
    "six-year retention": ("six years", "六年"),
    "s.88 approved charity": ("section 88", "第 88 條"),
    "non-deductible list": ("raffle", "獎券"),
    "spouse 35% own income": ("35% of their own income or profits", "按其本人的入息或利潤計算"),
    "not tax advice":     ("not tax advice", "並非稅務建議"),
    "standard rate 15/16": ("15% on the first HK$5 million, 16% above", "首 HK$500 萬 15%"),
    "top rungs fall":     ("last two rungs fall", "最頂兩級"),
    "31 March YA end":    ("31 March", "3 月 31 日"),
    "IRD determines":     ("rest with the Inland Revenue Department", "以稅務局評定為準"),
    "recognised donation": ("recognised charitable donation", "認可慈善捐款"),
    "2,132,500 threshold": ("2,132,500", "2,132,500"),
    "annual total rule":  ("total for that year", "全年捐款總額"),
}

heights = {}
with sync_playwright() as pw:
    br = pw.chromium.launch(channel="chrome", headless=True)

    # ---- rendered text per language, both parts, facts + CJK + targets + overflow
    for lang in ("en", "zh-HK"):
        text = {}
        for part in ("calc", "pay", "receipt"):
            p = br.new_page(viewport={"width": 1280, "height": 300}, device_scale_factor=1)
            p.goto(f"{BASE}?part={part}&lang={lang}", wait_until="load")
            p.wait_for_timeout(350)
            text[part] = p.evaluate("""()=>{
              const grab = [];
              document.querySelectorAll('[data-i18n],[data-i18n-ph],[data-i18n-aria],input,option,button,a,h2,p,dt,dd,label,summary,legend')
                .forEach(el=>{
                  grab.push(el.textContent||'');
                  if(el.placeholder) grab.push(el.placeholder);
                  if(el.getAttribute('aria-label')) grab.push(el.getAttribute('aria-label'));
                });
              return grab.join(' \\u0001 ');
            }""")
            if lang == "en":
                cjk = re.findall(r"[\u3400-\u9fff\uf900-\ufaff]", p.evaluate("document.body.innerText"))
                ok(not cjk, f"en build (?part={part}) renders no CJK",
                   repr("".join(cjk[:12])))
                small = p.evaluate("""()=>{
                  const bad=[];
                  document.querySelectorAll('a,button,summary,select,input[type=checkbox],[data-amt],[data-mo]').forEach(el=>{
                    const r=el.getBoundingClientRect();
                    if(r.width===0&&r.height===0) return;
                    const inProse = el.closest('p.lede,p.benefit,p.hint,p.note,p.scope,p.assump,p.fine,details p,dl');
                    if(inProse && el.tagName==='A' && !el.classList.contains('btn')) return;  // links inside running text
                    // effective target: a checkbox wrapped in its label is hit via the label
                    let t = r;
                    if (el.type === 'checkbox') {
                      const lab = el.closest('label');
                      if (lab) t = lab.getBoundingClientRect();
                    }
                    if(t.height < 43.5) bad.push(el.tagName+'.'+(el.className||'')+' h='+Math.round(t.height));
                  });
                  return bad;
                }""")
                ok(not small, f"touch targets >= 44px (?part={part})", "; ".join(small[:4]))
            p.close()
        joined = " ".join(text.values())
        for label, (en_s, zh_s) in FACTS.items():
            needle = en_s if lang == "en" else zh_s
            ok(needle in joined, f"[{lang}] fact present: {label}", needle)

    # ---- the income ladder must never clip its own label
    LADDER_JS = ("()=>{const bad=[];document.querySelectorAll('.bands label').forEach(l=>{"
                 "const sp=l.querySelector('span:not(.r)'); if(!sp) return;"
                 "if(sp.scrollWidth>sp.clientWidth+1||l.scrollWidth>l.clientWidth+1)"
                 " bad.push(sp.textContent.trim());});return bad;}")
    for lang in ("en", "zh-HK"):
        for w in (721, 768, 900, 1280):
            p = br.new_page(viewport={"width": w, "height": 400})
            p.goto(f"{BASE}?part=calc&lang={lang}", wait_until="load")
            p.wait_for_timeout(200)
            bad = p.evaluate(LADDER_JS)
            ok(not bad, f"income ladder fits {lang} @{w}px", ", ".join(bad))
            p.close()

    # ---- overflow at five widths
    for lang in ("en", "zh-HK"):
        for part in ("calc", "pay", "receipt"):
            for w in (320, 390, 568, 768, 1280):
                p = br.new_page(viewport={"width": w, "height": 300}, is_mobile=(w < 600),
                                has_touch=(w < 600))
                p.goto(f"{BASE}?part={part}&lang={lang}", wait_until="load")
                p.wait_for_timeout(250)
                ov = p.evaluate("()=>{const d=document.documentElement;"
                                "return Math.ceil(Math.max(d.scrollWidth,document.body.scrollWidth))-d.clientWidth;}")
                ok(ov <= 0, f"no h-overflow {part}/{lang} @{w}px", f"+{ov}px")
                p.close()

    # ---- external surface
    p = br.new_page()
    p.goto(f"{BASE}?part=calc&lang=en", wait_until="load")
    reqs = []
    p.on("request", lambda r: reqs.append(r.url))
    p.reload(wait_until="load")
    p.wait_for_timeout(400)
    ext = [u for u in reqs if not u.startswith("http://127.0.0.1:8766")]
    ok(not ext, "no external requests", "; ".join(ext[:3]))
    hrefs = p.evaluate("()=>Array.from(document.querySelectorAll('a[href]')).map(a=>a.href)")
    ok(all(h.startswith("https://www.hollows.org/") or h.endswith(("#result", "#disclaimer")) for h in hrefs),
       "outbound links only to hollows.org", str(hrefs))
    ok(p.evaluate("()=>document.querySelectorAll('img,link[rel=stylesheet],script[src]').length") == 0,
       "no images, no external stylesheet, no script src")
    ok(p.evaluate("()=>document.querySelectorAll('input#rname,input#rmail,input#rref,input#consent').length") == 4,
       "receipt form keeps name, email, reference, consent")
    p.close()

    # ---- height sweep
    WIDTHS = [320, 328, 360, 390, 414, 430, 480, 540, 568, 600, 640, 700, 721, 768,
              820, 900, 944, 1024, 1100, 1200, 1280, 1440]
    for lang in ("zh-HK", "en"):
        for part in ("calc", "pay", "receipt"):
            rows = []
            for w in WIDTHS:
                p = br.new_page(viewport={"width": w, "height": 240}, is_mobile=(w < 600),
                                has_touch=(w < 600))
                p.goto(f"{BASE}?part={part}&lang={lang}", wait_until="load")
                p.wait_for_timeout(220)
                rows.append((w, p.evaluate("()=>document.documentElement.scrollHeight")))
                p.close()
            peak_w, peak = max(rows, key=lambda r: r[1])
            heights[f"{part}/{lang}"] = {"peak": peak, "at": peak_w,
                                         "min": min(r[1] for r in rows),
                                         "curve": rows}
    br.close()

print("\n10 · height sweep (22 widths)")
print(f"{'block':16}{'peak':>7}{'at':>7}{'min':>7}   {'+55 suggested':>14}")
for k, v in heights.items():
    print(f"{k:16}{v['peak']:>7}{v['at']:>7}{v['min']:>7}   {v['peak']+55:>14}")

json.dump(heights, open("heights-sweep.json", "w"), indent=1)
print("\n" + ("ALL CHECKS PASSED" if not fails else f"{len(fails)} FAILURES:\n  - " + "\n  - ".join(fails)))
sys.exit(1 if fails else 0)
