#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""23 Nov 2026 — the disclaimer becomes an always-visible numbered list.

The client asked for the five sentences as a numbered list, permanently visible,
with the IRD website linked inside item 4. It shipped as a collapsed
`<details>` accordion; this turns it into an `<h3>` + `<ol>` of five `<li>`.

Applied as a script, not by hand, for the reason the skill gives: every old
string is asserted to occur EXACTLY ONCE before it is replaced. A string that
appears twice means the edit lands in the wrong place; one that appears zero
times means the copy has already drifted.

Run: /Library/Developer/CommandLineTools/usr/bin/python3 qa/apply_disc_list_20261123.py
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "embed" / "index.html"

# ── the client's strings, character for character ───────────────────────────
# Chinese punctuation is as supplied: items 1, 2 and 4 end with an ASCII full
# stop, items 3 and 5 with 。. Do not normalise.
ZH_LINK = ('<a href="https://www.ird.gov.hk/chi/welcome.htm" target="_blank" '
           'rel="noopener noreferrer">香港稅務局網頁</a>')
EN_LINK = ('<a href="https://www.ird.gov.hk/eng/welcome.htm" target="_blank" '
           'rel="noopener noreferrer">Hong Kong Inland Revenue Department website</a>')

COPY = {
    "zh-HK": {
        "head": "免責聲明:",
        "1": "根據稅務局相關課稅年度資料估算，僅供一般參考.",
        "2": "不會收集、記錄或儲存任何輸入資料.",
        "3": "以累進稅率或標準稅率（以較低者為準）估算應繳稅款；最終以稅務局核定為準。",
        "4": "不構成專業意見，詳情請參閱" + ZH_LINK + "或諮詢顧問.",
        "5": "護瞳行動（香港）有限公司概不承擔相關法律責任。",
    },
    "en": {
        "head": "Disclaimer:",
        "1": "Based on IRD tax rates and info for the relevant assessment year; for general reference only.",
        "2": "Does not collect, record, or store entered data.",
        "3": "Estimates tax using progressive or standard rates (whichever is lower); actual results depend on the IRD.",
        "4": "Not formal financial/tax advice; refer to the " + EN_LINK + " or a professional.",
        "5": "The Fred Hollows Foundation (HK) Limited assumes no liability for use or reliance.",
    },
}

# ── 1 · the CSS ─────────────────────────────────────────────────────────────
CSS_OLD = """.disc-global{border-top:1px solid var(--line);margin-top:var(--s4);padding-top:var(--s3)}
/* 23 Nov: the disclaimer is the page's fine print, so it takes the fine-print
   size and the whole column. It was 15px inside a 510px measure \u2014 half the
   column empty, and it read larger than the 13px notes directly above it. */
details.q.disc-global p,details.q.disc-global ul{font-size:var(--t-cap);line-height:1.6;max-width:none}
"""

CSS_NEW = """/* 23 Nov: the disclaimer is the page's fine print and it is ALWAYS OPEN \u2014 the
   client wanted five numbered sentences, not an accordion. It keeps the 13px
   fine-print token and the whole column: at 15px inside a 510px measure it read
   larger than the 13px notes directly above it and left half the column empty.
   The heading is an h3 at the same fine-print size \u2014 a document heading, not a
   display heading, because this block sits under a 32px block heading. */
.disc-global{border-top:1px solid var(--line);margin-top:var(--s4);padding-top:var(--s3)}
/* #disc-link jumps here; the block takes focus so a keyboard or screen-reader
   user lands inside the text instead of at the top of the document. */
.disc-global:focus{outline:none}
.disc-global:focus-visible{outline:2px solid var(--navy);outline-offset:4px}
.disc-global .disc-h{margin:0 0 var(--s2);font-size:var(--t-cap);line-height:1.6;
                     font-weight:700;letter-spacing:.01em;color:var(--ink)}
/* a real <ol>, so the numbers are the list's, not typed digits \u2014 they follow the
   language and a screen reader announces "list of 5 items". */
.disc-global .disc-list{margin:0;padding-left:1.5em;font-size:var(--t-cap);
                        line-height:1.6;color:var(--ink-2);max-width:none}
.disc-global .disc-list li{margin:0 0 2px}
.disc-global .disc-list li:last-child{margin-bottom:0}
/* The IRD link sits inside a paragraph of small print, so it reads as a link
   (navy, underlined \u2014 the same treatment as the widget's other inline links),
   never as a button. #E97824 fails AA as text at any size (2.93:1 on white). */
.disc-global .disc-list a{color:var(--navy);text-decoration:underline;
                          text-underline-offset:2px;text-decoration-thickness:1px}
.disc-global .disc-list a:hover{text-decoration-thickness:2px}
.disc-global .disc-list a:focus-visible{outline:2px solid var(--navy);outline-offset:2px}
"""

# ── 2 · the markup ──────────────────────────────────────────────────────────
HTML_OLD = """      <details class="q disc-global" id="disclaimer">
      <summary data-i18n="rc.disc.summary">Disclaimer</summary>
      <p data-i18n-html="rc.disc.body">Based on IRD tax rates and info for the relevant assessment year; for general reference only.<br>Does not collect, record, or store entered data.<br>Estimates tax using progressive or standard rates (whichever is lower); actual results depend on the IRD.<br>Not formal financial/tax advice; refer to the Hong Kong Inland Revenue Department website or a professional.<br>The Fred Hollows Foundation (HK) Limited assumes no liability for use or reliance.</p>
    </details>
"""


def html_new():
    rows = "\n".join(
        f'        <li data-i18n-html="rc.disc.{i}">{COPY["en"][str(i)]}</li>'
        for i in range(1, 6))
    return f"""      <!-- The legal block: always visible, five numbered sentences (23 Nov).
           It is NOT a disclosure any more \u2014 #disc-link still points at this id,
           so the consent line keeps working; the block takes focus on arrival. -->
      <section class="disc-global" id="disclaimer" tabindex="-1" aria-labelledby="disc-h">
        <h3 class="disc-h" id="disc-h" data-i18n="rc.disc.head">{COPY["en"]["head"]}</h3>
        <ol class="disc-list">
{rows}
        </ol>
      </section>
"""


# ── 3 · the two string tables ───────────────────────────────────────────────
ZH_OLD = ('      "rc.disc.summary": "\u514d\u8cac\u8072\u660e",\n'
          '      "rc.disc.body": "\u6839\u64da\u7a05\u52d9\u5c40\u76f8\u95dc\u8ab2\u7a05\u5e74\u5ea6\u8cc7\u6599\u4f30\u7b97\uff0c\u50c5\u4f9b\u4e00\u822c\u53c3\u8003\u3002<br>\u4e0d\u6703\u6536\u96c6\u3001\u8a18\u9304\u6216\u5132\u5b58\u4efb\u4f55\u8f38\u5165\u8cc7\u6599\u3002<br>\u4ee5\u7d2f\u9032\u7a05\u7387\u6216\u6a19\u6e96\u7a05\u7387\uff08\u4ee5\u8f03\u4f4e\u8005\u70ba\u6e96\uff09\u4f30\u7b97\u61c9\u7e73\u7a05\u6b3e\uff1b\u6700\u7d42\u4ee5\u7a05\u52d9\u5c40\u6838\u5b9a\u70ba\u6e96\u3002<br>\u4e0d\u69cb\u6210\u5c08\u696d\u610f\u898b\uff0c\u8a73\u60c5\u8acb\u53c3\u95b1\u9999\u6e2f\u7a05\u52d9\u5c40\u7db2\u9801\u6216\u8aee\u8a62\u9867\u554f.<br>\u8b77\u77b3\u884c\u52d5\uff08\u9999\u6e2f\uff09\u6709\u9650\u516c\u53f8\u6982\u4e0d\u627f\u64d4\u76f8\u95dc\u6cd5\u5f8b\u8cac\u4efb"')

EN_BODY = ("Based on IRD tax rates and info for the relevant assessment year; for general reference only."
           "<br>Does not collect, record, or store entered data."
           "<br>Estimates tax using progressive or standard rates (whichever is lower); actual results depend on the IRD."
           "<br>Not formal financial/tax advice; refer to the Hong Kong Inland Revenue Department website or a professional."
           "<br>The Fred Hollows Foundation (HK) Limited assumes no liability for use or reliance.")
EN_OLD = ('      "rc.disc.summary": "Disclaimer",\n'
          '      "rc.disc.body": ' + json.dumps(EN_BODY))


def table_new(lang):
    c = COPY[lang]
    # No trailing comma on the last line: the retired block ended with one, and
    # the key after it still carries its own — two commas is a syntax error.
    lines = ['      "rc.disc.head": ' + json.dumps(c["head"], ensure_ascii=False)]
    for i in range(1, 6):
        lines.append(f'      "rc.disc.{i}": ' + json.dumps(c[str(i)], ensure_ascii=False))
    return ",\n".join(lines)


# ── 4 · the click handler ───────────────────────────────────────────────────
JS_OLD = """  /* The consent-line link must OPEN the collapsed text, not just jump to it.
     Bound on the document because applyLang() re-creates that paragraph when
     the language changes \u2014 a listener on the old node would be orphaned. */
  document.addEventListener("click", function (e) {
    var el = e.target;
    while (el && el !== document) {
      if (el.id === "disc-link") {
        var d = $("#disclaimer"); if (d) { d.open = true; scheduleHeight(); }
        return;
      }
      el = el.parentNode;
    }
  });"""

JS_NEW = """  /* The consent-line link used to OPEN a collapsed accordion. The block is
     always visible now, so the link's job is the jump plus focus: without it a
     keyboard or screen-reader user is moved on screen but left at the top of the
     document. preventScroll keeps the browser's own anchor jump. Bound on the
     document because applyLang() re-creates that paragraph when the language
     changes \u2014 a listener on the old node would be orphaned. */
  document.addEventListener("click", function (e) {
    var el = e.target;
    while (el && el !== document) {
      if (el.id === "disc-link") {
        var d = $("#disclaimer"); if (d) { d.focus({preventScroll: true}); }
        return;
      }
      el = el.parentNode;
    }
  });"""

EDITS = [
    ("css: the accordion-only fine-print rule becomes the list block", CSS_OLD, CSS_NEW),
    ("markup: <details>/<summary> -> <h3> + <ol> of five <li>", HTML_OLD, html_new()),
    ("i18n zh-HK: rc.disc.summary/body -> rc.disc.head + .1-.5", ZH_OLD, table_new("zh-HK")),
    ("i18n en: rc.disc.summary/body -> rc.disc.head + .1-.5", EN_OLD, table_new("en")),
    ("js: the link opens nothing now, so it focuses the block", JS_OLD, JS_NEW),
]


def main():
    src = SRC.read_text(encoding="utf-8")
    originals = {}
    for label, old, new in EDITS:
        n = src.count(old)
        if n != 1:
            print(f"ABORT — {label}: old string occurs {n}\u00d7, needs exactly 1")
            return 1
        originals[label] = old
        src = src.replace(old, new)
        print(f"  ok  {label}")

    SRC.write_text(src, encoding="utf-8")

    # the edit list cannot disagree with the file: re-read and assert
    after = SRC.read_text(encoding="utf-8")
    problems = []
    for label, old, _ in EDITS:
        if old in after:
            problems.append(f"{label}: old text still present")
    for must in ('id="disclaimer" tabindex="-1"', '<ol class="disc-list">',
                 'aria-labelledby="disc-h"',
                 'https://www.ird.gov.hk/eng/welcome.htm',
                 'https://www.ird.gov.hk/chi/welcome.htm',
                 'rel="noopener noreferrer"'):
        if must not in after:
            problems.append(f"missing after the edit: {must}")
    if after.count('<li data-i18n-html="rc.disc.') != 5:
        problems.append("the <ol> does not carry exactly five translated <li>")
    if "rc.disc.summary" in after or "rc.disc.body" in after:
        problems.append("a retired rc.disc key survives")
    if after.count("d.open = true") != 0:
        problems.append("the accordion handler survives")
    if problems:
        print("VERIFY FAIL:")
        for p in problems:
            print("  -", p)
        return 1

    # A string-table edit is a JavaScript edit: a missing comma between two keys
    # is a syntax error that silently kills the whole IIFE, so every page falls
    # back to the English markup and only the language looks wrong. The browser
    # reports it as "Unexpected string" and nothing else. Parse it here instead.
    scripts = re.findall(r"<script>(.*?)</script>", after, re.S)
    ok = True
    for n, body in enumerate(scripts):
        tmp = Path("/tmp") / f"fhf-script-{n}.js"
        tmp.write_text(body, encoding="utf-8")
        rc = __import__("subprocess").run(["node", "--check", str(tmp)],
                                          capture_output=True, text=True)
        if rc.returncode != 0:
            ok = False
            problems.append(f"script #{n} does not parse: {rc.stderr.strip().splitlines()[:3]}")
    if not ok:
        print("VERIFY FAIL:")
        for p in problems:
            print("  -", p)
        return 1

    print("\nAll edits applied and verified in embed/index.html.")
    print("\nCopy now shipping (both tables):")
    for lang in ("zh-HK", "en"):
        c = COPY[lang]
        print(f"  [{lang}] {c['head']}")
        for i in range(1, 6):
            plain = re.sub(r"<[^>]+>", "", c[str(i)])
            print(f"    {i}. {plain}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
