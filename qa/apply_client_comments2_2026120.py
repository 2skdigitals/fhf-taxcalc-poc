#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Apply Denise's second round of annotated comments (20 Nov 2026) to embed/index.html.

Every edit is an exact string that must occur EXACTLY ONCE. A string appearing
twice means the change would land in the wrong place; zero means the copy has
already drifted. The script is re-runnable from the .bak it writes.

  C1  white ground              --ground #F3F3F0 -> #fff   (1px lines keep the structure)
  C2  desktop width             .wrap max-width 44rem -> 56rem
  C3  donation floor HK$100     her own line, estimate suppressed below it, never clamped
  C4  months control removed    monthly = 12 months (an assumption made on her behalf)
  C5  no minus sign             tax saved renders HK$182, never −HK$182
  C6  scope line removed        the result block stops repeating the allowance basis
  C7  monthly link removed      "Give monthly instead" (a redirect to another page)
  C8  client disclaimer         their approved wording, verbatim, both languages
  plus ?part=all                one document: calculator -> result -> payment -> receipt

Usage: /usr/bin/python3 qa/apply_client_comments2_2026120.py
"""
import io
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "embed", "index.html")
BAK = os.path.join(ROOT, "embed", "index.html.bak-pre-client2-2026120")

if not os.path.exists(BAK):
    shutil.copy2(SRC, BAK)
    print(f"backup → {os.path.relpath(BAK, ROOT)}")

with io.open(BAK, encoding="utf-8") as fh:
    doc = fh.read()

rows = []


def edit(label, old, new, count=1):
    global doc
    n = doc.count(old)
    if n != count:
        print(f"FAIL  {label}: expected {count} occurrence(s), found {n}")
        print("      " + repr(old[:120]))
        sys.exit(1)
    doc = doc.replace(old, new)
    rows.append((label, old.splitlines()[0][:58], (new.splitlines()[0][:58] if new else "(removed)")))


def cut(label, start, end, keep=None):
    """Remove the slice from `start` up to and including `end`, replacing it with `keep`."""
    if keep is None:
        keep = end
    global doc
    if doc.count(start) != 1 or doc.count(end) != 1:
        print(f"FAIL  {label}: markers not unique ({doc.count(start)} / {doc.count(end)})")
        sys.exit(1)
    i = doc.index(start)
    j = doc.index(end, i) + len(end)
    removed = doc[i:j]
    doc = doc[:i] + keep + doc[j:]
    rows.append((label, removed.splitlines()[0][:58], "(block removed)"))


# ── C1 · white ground ────────────────────────────────────────────────────────
edit("C1 ground token", "  --ground:#F3F3F0;", "  --ground:#fff;")

# ── C2 · desktop width ───────────────────────────────────────────────────────
edit("C2 column width",
     ".wrap{max-width:44rem;margin:0 auto;",
     ".wrap{max-width:56rem;margin:0 auto;")

# ── C8/C3 · the HK$100 floor, styling ────────────────────────────────────────
edit("C3 floor styles",
     ".note{font-size:var(--t-cap);line-height:1.6;color:var(--muted);margin:12px 0 0;max-width:var(--measure)}",
     ".note{font-size:var(--t-cap);line-height:1.6;color:var(--muted);margin:12px 0 0;max-width:var(--measure)}\n"
     "\n"
     "/* below the HK$100 floor no estimate is shown — the client's own sentence takes\n"
     "   its place. Nothing is clamped: the donor's figure stays what they typed. */\n"
     "#result.is-below-min .result,\n"
     "#result.is-below-min .benefit,\n"
     "#result.is-below-min .assump{display:none}\n"
     ".min-note{\n"
     "  margin:16px 0 0;padding:14px 16px;border:1px solid var(--line-2);\n"
     "  border-radius:var(--radius);background:var(--white);color:var(--ink);\n"
     "  font-size:var(--t-body);line-height:1.5;max-width:var(--measure);\n"
     "}")

# ── C4 · the months control goes ─────────────────────────────────────────────
cut("C4 months control",
    '      <div class="field" id="months-field" hidden>',
    '      </div>\n\n      <details class="q inset" id="what-counts">',
    keep='      <details class="q inset" id="what-counts">')

# ── C3 · her floor line under the amount ─────────────────────────────────────
edit("C3 floor line under the amount",
     '          <button type="button" data-amt="3000">3,000</button>\n'
     "        </div>\n"
     "      </div>",
     '          <button type="button" data-amt="3000">3,000</button>\n'
     "        </div>\n"
     '        <p class="hint" id="gift-min" data-i18n="s1.min">捐款金額達到或超過 HK$100 可獲得稅收減免。</p>\n'
     "      </div>")

# ── C3 · the result block's replacement note ─────────────────────────────────
edit("C3 floor note in the result block",
     '      </dl>\n'
     "    </div>\n"
     "\n"
     '    <p class="benefit"',
     '      </dl>\n'
     "    </div>\n"
     "\n"
     '    <p class="min-note" id="min-note" data-i18n="s2.min" hidden>捐款金額達到或超過 HK$100 可獲得稅收減免。</p>\n'
     "\n"
     '    <p class="benefit"')

# ── C6 · the scope line goes ─────────────────────────────────────────────────
edit("C6 scope line removed",
     '    <p class="scope" data-i18n="s2.scope">One person, salaries tax only. An estimate, not tax advice.</p>\n',
     "")

# ── C7 · the monthly link goes ───────────────────────────────────────────────
edit("C7 monthly link removed",
     '    <p class="alt"><a href="https://www.hollows.org/zh-Hant-HK/donate/monthly-donation/" '
     'target="_top" rel="noopener" data-i18n="s3.monthly">Give monthly instead</a></p>\n',
     "")

# ── C8 · the client's disclaimer, verbatim ───────────────────────────────────
DISC_ZH = ("根據稅務局相關課稅年度資料估算，僅供一般參考.<br>"
           "不會收集、記錄或儲存任何輸入資料.<br>"
           "以累進稅率或標準稅率（以較低者為準）估算應繳稅款；最終以稅務局核定為準。<br>"
           "不構成專業意見，詳情請參閱香港稅務局網頁或諮詢顧問.<br>"
           "護瞳行動（香港）有限公司概不承擔相關法律責任。")
DISC_EN = ("Based on IRD tax rates and info for the relevant assessment year; for general reference only.<br>"
           "Does not collect, record, or store entered data.<br>"
           "Estimates tax using progressive or standard rates (whichever is lower); actual results depend on the IRD.<br>"
           "Not formal financial/tax advice; refer to the Hong Kong Inland Revenue Department website or a professional.<br>"
           "The Fred Hollows Foundation (HK) Limited assumes no liability for use or reliance.")
FOOT_ZH = "根據稅務局相關課稅年度資料估算，僅供一般參考."
FOOT_EN = "Based on IRD tax rates and info for the relevant assessment year; for general reference only."

edit("C8 disclaimer element → html-capable",
     '      <p data-i18n="rc.disc.body">An estimate only. Not tax advice, and no substitute for professional advice. '
     'It follows Inland Revenue Department rules for the year of assessment ending 31 March, covers the deduction '
     'for recognised charitable donations only, and allows nothing for other deductions, allowances or tax '
     'reductions. It does not cover profits tax, personal assessment or joint assessment. What you may deduct, and '
     'what you pay, rest with the Inland Revenue Department. The calculator collects and stores nothing; the name, '
     'email and reference you give here are used only to match your donation and issue your receipt.</p>',
     '      <p data-i18n-html="rc.disc.body">' + DISC_EN + "</p>")

edit("C8 footnote → their line 1",
     '  <p class="fine" data-i18n="foot.legal">* What you may deduct rests with the Inland Revenue Department. '
     'The cap is 35% of assessable income or profits; the tax saved is roughly the deductible amount × your rate, '
     'up to 17%.</p>',
     '  <p class="fine" data-i18n="foot.legal">' + FOOT_EN + "</p>")

# ── i18n tables ──────────────────────────────────────────────────────────────
# zh
edit("i18n zh · months label/hint → floor line",
     '      "s1.months.label": "本課稅年度的捐款月數",\n'
     '      "s1.months.hint": "課稅年度至 3 月 31 日止；扣稅按全年捐款總額計算。",\n',
     '      "s1.min": "捐款金額達到或超過 HK$100 可獲得稅收減免。",\n')
edit("i18n zh · scope line → floor line (result)",
     '      "s2.scope": "只估算個人在薪俸稅下的捐款扣稅，並非稅務建議。",\n',
     '      "s2.min": "捐款金額達到或超過 HK$100 可獲得稅收減免。",\n')
edit("i18n zh · monthly link removed",
     '      "s3.monthly": "改為每月捐款",\n', "")
edit("i18n zh · disclaimer",
     '      "rc.disc.body": "僅為估算，並非稅務建議，亦不能取代專業意見。估算依稅務局截至 3 月 31 日止課稅年度的規定，'
     '只計入認可慈善捐款的扣稅，並無計及其他扣除、免稅額或稅務寬減；亦不涵蓋利潤稅、個人入息課稅或夫婦合併評稅。'
     '實際可扣除金額及應繳稅款以稅務局評定為準。本計算機不收集、不儲存任何資料；您在此提供的姓名、電郵及付款參考編號，'
     '只用於核對捐款及發出收據。",',
     '      "rc.disc.body": "' + DISC_ZH + '",')
edit("i18n zh · footnote",
     '      "foot.legal": "* 以稅務局評定為準。上限為應評稅入息或利潤的 35%；節省稅款約為可扣除金額 × 適用稅率（最高 17%）。",',
     '      "foot.legal": "' + FOOT_ZH + '",')
# en
edit("i18n en · months label/hint → floor line",
     '      "s1.months.label": "Months given this year of assessment",\n'
     '      "s1.months.hint": "The year of assessment ends 31 March. The deduction uses your total for that year.",\n',
     '      "s1.min": "Donation amount at HK$100 or above will receive tax deduction receipt",\n')
edit("i18n en · scope line → floor line (result)",
     '      "s2.scope": "One person, salaries tax only. An estimate, not tax advice.",\n',
     '      "s2.min": "Donation amount at HK$100 or above will receive tax deduction receipt",\n')
edit("i18n en · monthly link removed",
     '      "s3.monthly": "Give monthly instead",\n', "")
edit("i18n en · disclaimer",
     '      "rc.disc.body": "An estimate only. Not tax advice, and no substitute for professional advice. It follows '
     'Inland Revenue Department rules for the year of assessment ending 31 March, covers the deduction for recognised '
     'charitable donations only, and allows nothing for other deductions, allowances or tax reductions. It does not '
     'cover profits tax, personal assessment or joint assessment. What you may deduct, and what you pay, rest with the '
     'Inland Revenue Department. The calculator collects and stores nothing; the name, email and reference you give '
     'here are used only to match your donation and issue your receipt.",',
     '      "rc.disc.body": "' + DISC_EN + '",')
edit("i18n en · footnote",
     '      "foot.legal": "* The IRD decides what you may deduct. Cap 35% of assessable income or profits; '
     'tax saved ≈ deductible × your rate, up to 17%.",',
     '      "foot.legal": "' + FOOT_EN + '",')

# ── C4 · monthly is a full year, in the engine's terms ───────────────────────
edit("C4 state loses months",
     'var st = {amount:1300, band:"r17", mode:"once", months:12, exact:0};',
     'var st = {amount:1300, band:"r17", mode:"once", exact:0};\n'
     '  /* Monthly is a full year of gifts. The client slide-2 note removes the\n'
     '     months control, so the annual deduction is amount x 12 — stated in the\n'
     '     caption, never silently assumed. */\n'
     '  var MONTHS = 12;')
edit("C4 clampMonths → constant",
     '  function clampMonths(v){ var n = parseInt(v,10); if (isNaN(n)) return 12; return Math.min(Math.max(n,1),12); }\n',
     "")
edit("C4 render reads the constant",
     '    var months = clampMonths(st.months);',
     '    var months = MONTHS;')
edit("C4 wiring: months field hidden toggle",
     '      $("#months-field").hidden = st.mode !== "monthly";\n',
     "")
edit("C4 months change handler",
     '  $("#months").addEventListener("change", function (e) {\n'
     '    touched = true; st.months = clampMonths(e.target.value);\n'
     '    e.target.value = String(st.months);\n'
     '    render(); resultShown();\n'
     '  });\n'
     '  $$("[data-mo]").forEach(function (b) {\n'
     '    b.addEventListener("click", function () {\n'
     '      st.months = clampMonths(b.dataset.mo);\n'
     '      $("#months").value = String(st.months);\n'
     '      touched = true; render(); resultShown();\n'
     '    });\n'
     '  });\n',
     "")
edit("C4 chips sync",
     '    $$("[data-mo]").forEach(function(b){\n'
     '      b.classList.toggle("is-on", String(clampMonths(st.months)) === String(b.getAttribute("data-mo")));\n'
     '    });\n',
     "")
edit("C4 month words in applyLang",
     '    /* a month count is a value, not copy: one template, singular kept */\n'
     '    $$("#months option").forEach(function(o){ o.textContent = monthWord(o.value); });\n'
     '    $$("[data-mo]").forEach(function(b){ b.textContent = monthWord(b.getAttribute("data-mo")); });\n',
     "")
edit("C4 monthWord helper",
     '  function monthWord(n){\n'
     '    n = String(n);\n'
     '    return t(n === "1" ? "d.months.one" : "d.months.n", {n: n});\n'
     '  }\n',
     "")
edit("C4 analytics annual",
     '      var annual = digits(st.amount) * (st.mode === "monthly" ? clampMonths(st.months) : 1);',
     '      var annual = digits(st.amount) * (st.mode === "monthly" ? MONTHS : 1);')

# ── C5 · no minus sign ───────────────────────────────────────────────────────
edit("C5 default markup renders positive",
     '<dd id="saved">−HK$221</dd>',
     '<dd id="saved">HK$221</dd>')
edit("C5 stale comment",
     '       range ("−X to −Y") and the caption names its source, so the plain label',
     '       range ("X to Y") and the caption names its source, so the plain label')
edit("C5 positive saving",
     '    $("#saved").textContent = annual <= 0 ? "−HK$0"\n'
     '      : isRange ? "−" + money(savedLow) + t("d.range.sep") + "−" + money(savedHigh)\n'
     '      : "−" + money(savedHigh);',
     '    /* the client\'s fifth note: the saving is money you keep, so it reads\n'
     '       positive — HK$182, never −HK$182. */\n'
     '    $("#saved").textContent = annual <= 0 ? money(0)\n'
     '      : isRange ? money(savedLow) + t("d.range.sep") + money(savedHigh)\n'
     '      : money(savedHigh);')

# ── C3 · below the floor there is no estimate ────────────────────────────────
edit("C3 render: floor state",
     '    var netLow = annual - savedHigh, netHigh = annual - savedLow;',
     '    /* Below HK$100 there is no deduction to estimate. The figure is NOT\n'
     '       clamped: the donor keeps what they typed and reads the client\'s own\n'
     '       sentence instead of a number. */\n'
     '    var belowMin = once > 0 && once < 100;\n'
     '    $("#result").classList.toggle("is-below-min", belowMin);\n'
     '    var mn = $("#min-note"); if (mn) mn.hidden = !belowMin;\n'
     '\n'
     '    var netLow = annual - savedHigh, netHigh = annual - savedLow;')
edit("C3 announce: floor line instead of figures",
     '      $("#announce").textContent =\n'
     '        (st.mode === "monthly"',
     '      $("#announce").textContent = belowMin ? t("s2.min") :\n'
     '        (st.mode === "monthly"')
edit("C3 analytics: no result event below the floor",
     '  function resultShown(){\n'
     '    clearTimeout(resultT);',
     '  function resultShown(){\n'
     '    /* below the floor no result is shown, so no result event is claimed */\n'
     '    if (digits(st.amount) > 0 && digits(st.amount) < 100) return;\n'
     '    clearTimeout(resultT);')

# ── ?part=all ────────────────────────────────────────────────────────────────
edit("all · CSS shows every section",
     'body[data-part="pay"] #payment,\n'
     'body[data-part="receipt"] #receipt{display:block}',
     'body[data-part="pay"] #payment,\n'
     'body[data-part="receipt"] #receipt,\n'
     'body[data-part="all"] #calculator,\n'
     'body[data-part="all"] #result,\n'
     'body[data-part="all"] #payment,\n'
     'body[data-part="all"] #receipt{display:block}')
edit("all · the footnote stays in the combined document",
     'body[data-part="calc"] .wrap > p.fine{display:block}',
     'body[data-part="calc"] .wrap > p.fine,\n'
     'body[data-part="all"] .wrap > p.fine{display:block}')
edit("all · part map",
     '  var part = qs.get("part");\n'
     '  var PART_SECTIONS = {\n'
     '    input:   ["calculator"],\n'
     '    result:  ["result"],\n'
     '    calc:    ["calculator","result"],\n'
     '    pay:     ["payment"],\n'
     '    receipt: ["receipt"]\n'
     '  };',
     '  /* `all` is the one-link arrangement: calculator -> result -> payment ->\n'
     '     receipt in one document, separated exactly as the design already\n'
     '     separates them. It is also the DEFAULT, so the link Kevin sends needs no\n'
     '     parameter at all. The four single-part embeds still work unchanged and\n'
     '     remain the recommended production arrangement (docs/INTERFACE.md §2). */\n'
     '  var part = qs.get("part") || "all";\n'
     '  var PART_SECTIONS = {\n'
     '    input:   ["calculator"],\n'
     '    result:  ["result"],\n'
     '    calc:    ["calculator","result"],\n'
     '    pay:     ["payment"],\n'
     '    receipt: ["receipt"],\n'
     '    all:     ["calculator","result","payment","receipt"]\n'
     '  };')
edit("all · analytics default",
     '      part: part || "full",',
     '      part: part,')

# ── write + report ───────────────────────────────────────────────────────────
with io.open(SRC, "w", encoding="utf-8") as fh:
    fh.write(doc)

print(f"\napplied {len(rows)} edits to embed/index.html\n")
print(f"{'change':44}  {'before':58}")
print("-" * 106)
for label, before, after in rows:
    print(f"{label:44}  {before}")
print("\nresidues (all must be 0):")
checks = {
    "--ground:#F3F3F0": doc.count("--ground:#F3F3F0"),
    "max-width:44rem": doc.count("max-width:44rem"),
    "id=\"months-field\"": doc.count('id="months-field"'),
    "id=\"months\"": doc.count('id="months"'),
    "clampMonths": doc.count("clampMonths"),
    '"−" + money (render)': doc.count('"−" + money'),
    "−HK$0 default": doc.count("−HK$0"),
    'data-i18n="s2.scope"': doc.count('data-i18n="s2.scope"'),
    'data-i18n="s3.monthly"': doc.count('data-i18n="s3.monthly"'),
    "old draft disclaimer phrase": doc.count("不能取代專業意見"),
}
for k, v in checks.items():
    print(f"  {k:28} {v}   {'OK' if v == 0 else 'FAIL'}")
if any(checks.values()):
    sys.exit(1)
print("\nmarkers present:", all(x in doc for x in ('data-part="all"', 'id="min-note"', 'var MONTHS = 12;')))
