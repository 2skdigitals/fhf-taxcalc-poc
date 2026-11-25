#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""25 Nov 2026 — remove the disclaimer from the widget; the host page carries it.

The client has added a Rich Text Editor block on their own Optimize page to carry
the legal disclaimer, so the widget must stop carrying it. Three things leave, in
both languages, together (a one-sided edit fails lang_parity on a key mismatch):

  1. `<section class="disc-global" id="disclaimer">` — the five numbered
     sentences, with `#disc-h`;
  2. `<p class="fine" data-i18n="foot.legal">` — the one-line "Based on IRD tax
     rates…" note above it, which duplicates the block's first sentence;
  3. their i18n keys — `rc.disc.head`, `rc.disc.1`…`rc.disc.5`, `foot.legal` —
     from the zh-HK and en tables.

`rc.disclink` stays but becomes plain text: it pointed at `#disclaimer`, and that
anchor is dead now. "Read the disclaimer before you send anything." /
「提交前請先閱讀免責聲明。」 — client-reviewed copy, not rewritten further.

What deliberately STAYS (so a later pass does not re-add the block):
  · the section's CSS (`.disc-global`, `.disc-list`, `.disc-h`, the focus rules);
  · `html[data-phase="1"] body[data-part="receipt"] #disclaimer{display:none!important}`;
  · `p.fine[data-i18n="foot.legal"]{max-width:none}`;
  · `.fine` itself — the consent line still uses that class.

Also removes the JS that gave `#disc-link` its jump-and-focus behaviour: there is
no link and no target any more.

Run from the repo root:
    /Library/Developer/CommandLineTools/usr/bin/python3 qa/apply_remove_disclaimer_20261125.py
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HTML = ROOT / "embed" / "index.html"

src = HTML.read_bytes().decode("utf-8")
orig = src


def must(hay, needle, what):
    n = hay.count(needle)
    if n != 1:
        raise SystemExit(f"anchor {what!r}: found {n} times, expected 1 — file already changed?")
    return hay.index(needle)


# ───────────────────────────────────────────── 1 · the Chinese string table
ZH_OLD = '''      "rc.disclink": "提交前請先閱讀<a href=\\"#disclaimer\\" id=\\"disc-link\\">免責聲明</a>。",
      "rc.submit": "提交收據申請",
      "rc.keep": "請保留收據六年；稅務局可能要求查閱。",
      "rc.disc.head": "免責聲明:",
      "rc.disc.1": "根據稅務局相關課稅年度資料估算，僅供一般參考.",
      "rc.disc.2": "不會收集、記錄或儲存任何輸入資料.",
      "rc.disc.3": "以累進稅率或標準稅率（以較低者為準）估算應繳稅款；最終以稅務局核定為準。",
      "rc.disc.4": "不構成專業意見，詳情請參閱<a href=\\"https://www.ird.gov.hk/chi/welcome.htm\\" target=\\"_blank\\" rel=\\"noopener noreferrer\\">香港稅務局網頁</a>或諮詢顧問.",
      "rc.disc.5": "護瞳行動（香港）有限公司概不承擔相關法律責任。",
      "foot.legal": "根據稅務局相關課稅年度資料估算，僅供一般參考。",
'''
ZH_NEW = '''      "rc.disclink": "提交前請先閱讀免責聲明。",
      "rc.submit": "提交收據申請",
      "rc.keep": "請保留收據六年；稅務局可能要求查閱。",
'''
src = src.replace(ZH_OLD, ZH_NEW, 1)
if ZH_NEW not in src:
    raise SystemExit("the zh-HK string block moved — read the table before editing")

# ───────────────────────────────────────────── 2 · the English string table
EN_OLD = '''      "rc.disclink": "Read the <a href=\\"#disclaimer\\" id=\\"disc-link\\">disclaimer</a> before you send anything.",
      "rc.submit": "Request my receipt",
      "rc.keep": "Keep the receipt for six years — the IRD may ask to see it.",
      "rc.disc.head": "Disclaimer:",
      "rc.disc.1": "Based on IRD tax rates and info for the relevant assessment year; for general reference only.",
      "rc.disc.2": "Does not collect, record, or store entered data.",
      "rc.disc.3": "Estimates tax using progressive or standard rates (whichever is lower); actual results depend on the IRD.",
      "rc.disc.4": "Not formal financial/tax advice; refer to the <a href=\\"https://www.ird.gov.hk/eng/welcome.htm\\" target=\\"_blank\\" rel=\\"noopener noreferrer\\">Hong Kong Inland Revenue Department website</a> or a professional.",
      "rc.disc.5": "The Fred Hollows Foundation (HK) Limited assumes no liability for use or reliance.",
      "foot.legal": "Based on IRD tax rates and info for the relevant assessment year; for general reference only.",
'''
EN_NEW = '''      "rc.disclink": "Read the disclaimer before you send anything.",
      "rc.submit": "Request my receipt",
      "rc.keep": "Keep the receipt for six years — the IRD may ask to see it.",
'''
src = src.replace(EN_OLD, EN_NEW, 1)
if EN_NEW not in src:
    raise SystemExit("the en string block moved — read the table before editing")

# ───────────────────────────────────────────── 3 · the consent line's markup
LINK_OLD = ('      <p class="fine" data-i18n-html="rc.disclink">'
            'Read the <a href="#disclaimer" id="disc-link">disclaimer</a> '
            'before you send anything.</p>')
LINK_NEW = ('      <!-- The sentence used to link to #disclaimer. The disclaimer now lives on\n'
            '           the host page, so the anchor is gone and this is plain text. -->\n'
            '      <p class="fine" data-i18n="rc.disclink">'
            'Read the disclaimer before you send anything.</p>')
src = src.replace(LINK_OLD, LINK_NEW, 1)
if LINK_NEW not in src:
    raise SystemExit("the consent line moved — read the receipt form before editing")

# ───────────────────────────────────────────── 4 · the footer block itself
FOOT_OLD = '''  <!-- The page-level footer. The disclaimer sits here — OUTSIDE every panel —
       so it is the one block every part carries, and it survives phase 1 with
       section 5 switched off (PHASE1). Legally reviewed client copy: never let
       it move inside a panel or behind a disclosure again. -->
  <p class="fine" data-i18n="foot.legal">Based on IRD tax rates and info for the relevant assessment year; for general reference only.</p>

      <!-- The legal block: always visible, five numbered sentences (23 Nov).
           It is NOT a disclosure any more — #disc-link still points at this id,
           so the consent line keeps working; the block takes focus on arrival. -->
      <section class="disc-global" id="disclaimer" tabindex="-1" aria-labelledby="disc-h">
        <h3 class="disc-h" id="disc-h" data-i18n="rc.disc.head">Disclaimer:</h3>
        <ol class="disc-list">
          <li data-i18n-html="rc.disc.1">Based on IRD tax rates and info for the relevant assessment year; for general reference only.</li>
          <li data-i18n-html="rc.disc.2">Does not collect, record, or store entered data.</li>
          <li data-i18n-html="rc.disc.3">Estimates tax using progressive or standard rates (whichever is lower); actual results depend on the IRD.</li>
          <li data-i18n-html="rc.disc.4">Not formal financial/tax advice; refer to the <a href="https://www.ird.gov.hk/eng/welcome.htm" target="_blank" rel="noopener noreferrer">Hong Kong Inland Revenue Department website</a> or a professional.</li>
          <li data-i18n-html="rc.disc.5">The Fred Hollows Foundation (HK) Limited assumes no liability for use or reliance.</li>
        </ol>
      </section>

'''
FOOT_NEW = '''  <!-- The legal fine print used to close this document: a one-line "Based on IRD
       tax rates…" note plus a five-sentence numbered disclaimer, outside every
       panel so that every part carried it. It now belongs to the client's own
       page (their Rich Text Editor block), so the widget does not carry it in
       any part and no part's height includes it. The CSS for the block is left
       in place on purpose — it is the record of what shipped, and the phase-1
       rule for the empty `?part=receipt` frame still names it. Do not rebuild
       the block here: two copies of a legal notice is the defect this pass fixes. -->

'''
src = src.replace(FOOT_OLD, FOOT_NEW, 1)
if FOOT_NEW not in src:
    raise SystemExit("the footer block moved — read it before editing")

# ───────────────────────────────────────────── 5 · the jump-and-focus handler
JS_OLD = '''  /* The consent-line link used to OPEN a collapsed accordion. The block is
     always visible now, so the link's job is the jump plus focus: without it a
     keyboard or screen-reader user is moved on screen but left at the top of the
     document. preventScroll keeps the browser's own anchor jump. Bound on the
     document because applyLang() re-creates that paragraph when the language
     changes — a listener on the old node would be orphaned. */
  document.addEventListener("click", function (e) {
    var el = e.target;
    while (el && el !== document) {
      if (el.id === "disc-link") {
        var d = $("#disclaimer"); if (d) { d.focus({preventScroll: true}); }
        return;
      }
      el = el.parentNode;
    }
  });

'''
if src.count(JS_OLD) != 1:
    raise SystemExit("the disclaimer click handler moved — read the JS before editing")
src = src.replace(JS_OLD, "", 1)

if src == orig:
    raise SystemExit("nothing changed")

HTML.write_bytes(src.encode("utf-8"))

# ───────────────────────────────────────────── 6 · checks that can actually fail
# A string-table edit is a JavaScript edit: one stray or missing comma kills the
# whole IIFE and every page silently falls back to the markup defaults.
script = re.search(r"<script>(.*)</script>", src, re.S).group(1)
tmp = ROOT / "qa" / "_remove_disc_check.js"
tmp.write_text(script, encoding="utf-8")
r = subprocess.run(["node", "--check", str(tmp)], capture_output=True, text=True)
tmp.unlink()
if r.returncode:
    raise SystemExit("node --check failed — the string table is broken:\n" + r.stderr)

bad = [k for k in ("rc.disc.head", "rc.disc.1", "rc.disc.2", "rc.disc.3", "rc.disc.4",
                   "rc.disc.5", '"foot.legal":', 'id="disc-link"', 'id="disc-h"',
                   'id="disclaimer"', 'href="#disclaimer"') if k in src]
if bad:
    raise SystemExit(f"still in the document: {bad}")
# the CSS is deliberately kept — prove it, so this pass cannot be "tidied" later
for keep in (".disc-global{border-top:1px solid var(--line)",
             ".disc-global .disc-list{",
             'html[data-phase="1"] body[data-part="receipt"] #disclaimer{display:none!important}',
             'p.fine[data-i18n="foot.legal"]{max-width:none}',
             ".fine{font-size:var(--t-cap)"):
    if keep not in src:
        raise SystemExit(f"a rule this pass must KEEP is missing: {keep}")

print("embed/index.html: disclaimer block and its i18n keys removed, both languages")
print(f"  bytes {len(orig)} -> {len(src)}  ({len(orig) - len(src)} fewer)")
