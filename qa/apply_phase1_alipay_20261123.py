#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Phase 1 + the AlipayHK receipt tooltip — applied as a re-runnable script.

Two changes, one file:
  A · section 5 (the receipt module) is gated behind `PHASE1` and renders
      nothing; the disclaimer stays, as the page-level footer it already is.
  B · the AlipayHK rail gains one line of copy + the same disclosure pattern
      the payment-reference field uses, carrying five cropped screencaps that
      walk a donor to 申請收據 inside the AlipayHK app.

Why a script and not hand edits: every replacement asserts its old string
occurs EXACTLY ONCE. A string that appears twice means the change lands in the
wrong place; a string that appears zero times means the copy has already
drifted. The script also runs `node --check` on the extracted <script>, because
a missing comma in a string table is a syntax error that silently kills the
whole IIFE and presents as "the language didn't switch" (skill §10o).

Run from the repo root:  python3 qa/apply_phase1_alipay_20261123.py
"""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILE = ROOT / "embed" / "index.html"
BAK = ROOT / "embed" / "index.html.bak-pre-phase1-20261123"

if not BAK.exists():
    BAK.write_bytes(FILE.read_bytes())
    print(f"backup → {BAK.name}")

src = FILE.read_text(encoding="utf-8")
applied = []


def sub(old, new, label):
    global src
    n = src.count(old)
    if n != 1:
        print(f"FAIL  {label}: old string occurs {n} times (need exactly 1)")
        sys.exit(1)
    src = src.replace(old, new)
    applied.append(label)


# ─────────────────────────────────────────────────────────────── A1 · version
sub('  var V = "1.2.0";',
    '  var V = "1.3.0";',
    "version 1.2.0 → 1.3.0")

# ───────────────────────────────────────────────────── A2 · the phase switch
sub('''  var V = "1.3.0";
''',
    '''  var V = "1.3.0";
  /* ── CAMPAIGN PHASE ────────────────────────────────────────────────────
     Phase 1 ships AlipayHK and the credit card, nothing else. PayMe is not in
     phase 1, and section 5 (the receipt module) exists ONLY to claim a PayMe
     receipt — the AlipayHK route is inside the AlipayHK app itself, and the
     card route is handled on the Foundation's own donation page. So section 5
     is switched OFF here rather than deleted: flip PHASE1 to false when PayMe
     ships and the section, its form, its popover and ?part=receipt all come
     back with no other edit. The constant is the whole switch — the CSS that
     consumes it reads html[data-phase="1"], which is set immediately below,
     and nothing else in this file knows the phase. */
  var PHASE1 = true;
  if (PHASE1) document.documentElement.setAttribute("data-phase", "1");
''',
    "PHASE1 constant + data-phase attribute")

# ────────────────────────────────────────── A3 · phase 1 CSS (part-mode block)
sub('''body[data-part="all"] #receipt{display:block}
''',
    '''body[data-part="all"] #receipt{display:block}
/* ── phase 1: section 5 is hidden, never deleted ──────────────────────────
   Section 5 renders nothing while PHASE1 is true, and a frame still pointed
   at ?part=receipt must return an EMPTY frame that reports ~60px rather than a
   half-drawn block — so the disclaimer goes quiet there too, and only there:
   every part that carries real content still closes with it. #receipt keeps
   its markup, its form, its popover and its analytics wiring, which is what
   makes PHASE1 a one-line return for PayMe. */
html[data-phase="1"] #receipt{display:none!important}
html[data-phase="1"] body[data-part="receipt"] #disclaimer{display:none!important}
''',
    "phase-1 CSS: hide #receipt, quiet the receipt frame")

# ───────────────────────────────────────────────── B1 · the payhelp CSS block
sub('''.hsteps p{font-size:var(--t-cap);line-height:1.55;color:var(--ink-2);margin:0}
''',
    '''.hsteps p{font-size:var(--t-cap);line-height:1.55;color:var(--ink-2);margin:0}

/* ── the AlipayHK receipt line ───────────────────────────────────────────
   Phase 1 has no in-widget receipt form (that is section 5, which returns
   with PayMe), but a wallet gift still needs a receipt and AlipayHK issues it
   from inside its own app. So the rail carries the route: one line of copy and
   the SAME disclosure the payment-reference field uses — .helpbtn + .helppop,
   aria-expanded, role="dialog", Escape closes, focus returns. One pattern in
   this widget, never two.

   It sits with the AlipayHK rail in both arrangements: between the two rows on
   a phone (blue 3px rule and the rail's own 14px inset, so the copy starts on the
   same left edge as the rail above it), and under
   the QR tile on a desktop, where only the <a> rows go and this line stays.
   Fine print only — the 13px token, the muted ink, no new size, colour, face
   or shadow. */
.payhelp{position:relative;padding:11px 0 12px 14px}
.rails .payhelp{border-left:3px solid #1677FF}
.payhelp-line{display:flex;align-items:center;gap:0;margin:0;
              font-size:var(--t-cap);line-height:1.55;color:var(--muted)}
.payhelp .helpbtn{margin:-13px -12px -13px -3px}
/* The panel is the reference popover's, re-anchored for a SHORT block: the
   payment block is declared at 640px (750px in English) and this trigger is the
   last thing in it, so a panel growing downward from a top:-10px anchor ends
   past the declared height every time — the one failure a fixed-height frame
   cannot absorb. So: full width below the trigger on a phone, beside it at
   ≥641px, and opening UPWARD from ≥720px where the trigger sits low and the
   space above it is the space that exists. Its bottom is pinned to the trigger,
   so it can never leave the frame at the bottom; the height cap keeps its top
   inside the frame too, and the steps scroll inside the panel. */
#payhelp .helppop{max-height:clamp(200px,calc(100vh - 300px),340px)}
@media(min-width:641px){
  /* left-anchored, not right: this trigger lives at the left edge of the
     payment block, so a right-anchored panel would open away from it */
  #payhelp .helppop{left:0;right:auto}
}
@media(min-width:720px){
  .rails{display:block;border-top:0;margin-top:0}
  .rails > a{display:none}
  .rails .payhelp{border-left:0}
  .payhelp{padding:15px 0 0}
  .payhelp-line{max-width:340px}
  #payhelp .helppop{top:auto;bottom:calc(100% + 8px);
                    max-height:clamp(240px,calc(100vh - 340px),380px)}
}
''',
    "payhelp CSS (+ the desktop arrangement that keeps the line)")

# ──────────────────────────────────── A4 · the disclaimer is the page footer
sub('''  <p class="fine" data-i18n="foot.legal">Based on IRD tax rates and info for the relevant assessment year; for general reference only.</p>''',
    '''  <!-- The page-level footer. The disclaimer sits here — OUTSIDE every panel —
       so it is the one block every part carries, and it survives phase 1 with
       section 5 switched off (PHASE1). Legally reviewed client copy: never let
       it move inside a panel or behind a disclosure again. -->
  <p class="fine" data-i18n="foot.legal">Based on IRD tax rates and info for the relevant assessment year; for general reference only.</p>''',
    "disclaimer documented as the page-level footer")

# ───────────────────────────────────────────── B2 · the payhelp markup
sub('''        <span class="go" aria-hidden="true">↗</span>
      </a>
      <a href="https://www.hollows.org/zh-Hant-HK/donate/" target="_top" rel="noopener" data-rail="card" class="r-card">''',
    '''        <span class="go" aria-hidden="true">↗</span>
      </a>

      <!-- Phase 1: the receipt route for an AlipayHK gift. AlipayHK issues the
           receipt inside its own app, so the rail carries the instruction plus
           five crops that walk a donor to 申請收據. The copy deliberately stops
           short of promising an issued receipt: it names where to apply.

           The crops are the client's own donor-side screens, resized to 400px
           and compressed (27 KB for all five). Two things were cropped OUT: the
           transaction reference on step 4 and the whole reference/amount block
           on step 5 (only the button and its link remain). No names, emails or
           phone numbers were in the source; nothing was added. AlipayHK's UI is
           Chinese, which is why the outro says so for an English reader. -->
      <div class="payhelp" id="payhelp">
        <p class="payhelp-line">
          <span data-i18n="s3.receipt.line">Need a receipt? Apply inside AlipayHK.</span>
          <button type="button" class="helpbtn" id="alipay-help" aria-expanded="false"
                  aria-controls="alipay-help-panel" data-help="alipay-help-panel"
                  data-i18n-aria="s3.receipt.btn">
            <span class="i" aria-hidden="true">?</span>
          </button>
        </p>

        <div class="helppop" id="alipay-help-panel" role="dialog"
             aria-labelledby="alipay-help-title" hidden>
          <button type="button" class="hclose" data-help-close
                  aria-label="Close" data-i18n-aria="s3.rcpt.close">&#10005;</button>
          <h3 id="alipay-help-title" data-i18n="s3.rcpt.title">Applying for a receipt in AlipayHK</h3>
          <p data-i18n="s3.rcpt.intro">A gift made in AlipayHK is receipted inside the same app. Five steps:</p>
          <ol class="hsteps">
            <li>
              <span class="n" data-i18n="s3.rcpt.s1t">Step 1</span>
              <img loading="eager" src="../assets/help/alipay-receipt-step-1.webp" width="400" height="189"
                   alt="AlipayHK home screen with the Charity donation icon ringed" data-i18n-alt="s3.rcpt.alt1">
              <p data-i18n="s3.rcpt.s1">Open AlipayHK and tap Charity donation.</p>
            </li>
            <li>
              <span class="n" data-i18n="s3.rcpt.s2t">Step 2</span>
              <img loading="eager" src="../assets/help/alipay-receipt-step-2.webp" width="400" height="107"
                   alt="The My donations tab at the foot of the charity page, ringed" data-i18n-alt="s3.rcpt.alt2">
              <p data-i18n="s3.rcpt.s2">Tap My donations at the bottom of the charity page.</p>
            </li>
            <li>
              <span class="n" data-i18n="s3.rcpt.s3t">Step 3</span>
              <img loading="eager" src="../assets/help/alipay-receipt-step-3.webp" width="400" height="344"
                   alt="The charity menu with Donation records ringed" data-i18n-alt="s3.rcpt.alt3">
              <p data-i18n="s3.rcpt.s3">Tap Donation records.</p>
            </li>
            <li>
              <span class="n" data-i18n="s3.rcpt.s4t">Step 4</span>
              <img loading="eager" src="../assets/help/alipay-receipt-step-4.webp" width="400" height="63"
                   alt="One HK$100 gift to the Foundation in the transaction list" data-i18n-alt="s3.rcpt.alt4">
              <p data-i18n="s3.rcpt.s4">Find the gift: the charity, the date and the amount identify it.</p>
            </li>
            <li>
              <span class="n" data-i18n="s3.rcpt.s5t">Step 5</span>
              <img loading="eager" src="../assets/help/alipay-receipt-step-5.webp" width="360" height="93"
                   alt="The blue Apply for receipt button at the foot of the donation result" data-i18n-alt="s3.rcpt.alt5">
              <p data-i18n="s3.rcpt.s5">Tap the blue Apply for receipt button at the foot of the donation result.</p>
            </li>
          </ol>
          <p data-i18n="s3.rcpt.outro">The AlipayHK app is shown in Chinese; the buttons sit in the same place on your screen.</p>
        </div>
      </div>

      <a href="https://www.hollows.org/zh-Hant-HK/donate/" target="_top" rel="noopener" data-rail="card" class="r-card">''',
    "payhelp markup (line + five-step dialog) between the two rails")

# ─────────────────────────────────────────── B3 · the second trigger is wired
sub('''          <button type="button" class="helpbtn" id="ref-help" aria-expanded="false"
                  aria-controls="ref-help-panel" data-i18n-aria="rc.ref.help.btn">''',
    '''          <button type="button" class="helpbtn" id="ref-help" aria-expanded="false"
                  aria-controls="ref-help-panel" data-help="ref-help-panel"
                  data-i18n-aria="rc.ref.help.btn">''',
    "#ref-help joins the shared disclosure pattern (data-help)")

# ──────────────────────────────────────────── B4 · string table, Chinese
sub('''      "rc.h": "索取扣稅收據",''',
    '''      "s3.receipt.line": "需要收據？可於 AlipayHK 內申請。",
      "s3.receipt.btn": "如何在 AlipayHK 內申請收據",
      "s3.rcpt.title": "在 AlipayHK 內申請收據",
      "s3.rcpt.intro": "在 AlipayHK 完成的捐款，收據同樣在 App 內申請。共五步：",
      "s3.rcpt.s1t": "第 1 步",
      "s3.rcpt.s1": "開啟 AlipayHK，點按「慈善捐款」。",
      "s3.rcpt.s2t": "第 2 步",
      "s3.rcpt.s2": "在慈善捐款頁底部點按「我的捐款」。",
      "s3.rcpt.s3t": "第 3 步",
      "s3.rcpt.s3": "點按「捐款記錄」。",
      "s3.rcpt.s4t": "第 4 步",
      "s3.rcpt.s4": "找到該筆捐款：受惠機構、日期與金額足以辨認。",
      "s3.rcpt.s5t": "第 5 步",
      "s3.rcpt.s5": "在捐款結果頁底部點按藍色的「申請收據」。",
      "s3.rcpt.outro": "截圖為 AlipayHK 的中文介面；您手機上的按鈕位置相同。",
      "s3.rcpt.close": "關閉",
      "s3.rcpt.alt1": "AlipayHK 首頁，已圈出「慈善捐款」圖示",
      "s3.rcpt.alt2": "慈善捐款頁底部，已圈出「我的捐款」",
      "s3.rcpt.alt3": "慈善捐款選單，已圈出「捐款記錄」",
      "s3.rcpt.alt4": "交易紀錄中一筆 HK$100 護瞳行動捐款",
      "s3.rcpt.alt5": "捐款結果頁底部的藍色「申請收據」按鈕",
      "rc.h": "索取扣稅收據",''',
    "zh-HK strings for the AlipayHK receipt route")

# ──────────────────────────────────────────── B5 · string table, English
sub('''      "rc.h": "Claim your receipt",''',
    '''      "s3.receipt.line": "Need a receipt? Apply inside AlipayHK.",
      "s3.receipt.btn": "How to apply for a receipt in AlipayHK",
      "s3.rcpt.title": "Applying for a receipt in AlipayHK",
      "s3.rcpt.intro": "A gift made in AlipayHK is receipted inside the same app. Five steps:",
      "s3.rcpt.s1t": "Step 1",
      "s3.rcpt.s1": "Open AlipayHK and tap Charity donation.",
      "s3.rcpt.s2t": "Step 2",
      "s3.rcpt.s2": "Tap My donations at the bottom of the charity page.",
      "s3.rcpt.s3t": "Step 3",
      "s3.rcpt.s3": "Tap Donation records.",
      "s3.rcpt.s4t": "Step 4",
      "s3.rcpt.s4": "Find the gift: the charity, the date and the amount identify it.",
      "s3.rcpt.s5t": "Step 5",
      "s3.rcpt.s5": "Tap the blue Apply for receipt button at the foot of the donation result.",
      "s3.rcpt.outro": "The AlipayHK app is shown in Chinese; the buttons sit in the same place on your screen.",
      "s3.rcpt.close": "Close",
      "s3.rcpt.alt1": "AlipayHK home screen with the Charity donation icon ringed",
      "s3.rcpt.alt2": "The My donations tab at the foot of the charity page, ringed",
      "s3.rcpt.alt3": "The charity menu with Donation records ringed",
      "s3.rcpt.alt4": "One HK$100 gift to the Foundation in the transaction list",
      "s3.rcpt.alt5": "The blue Apply for receipt button at the foot of the donation result",
      "rc.h": "Claim your receipt",''',
    "en strings for the AlipayHK receipt route")

# ───────────── C · the IRD link stays PER LANGUAGE (client decision, 23 Nov)
# English item 4 → /eng/welcome.htm, Chinese item 4 → /chi/welcome.htm. The client
# briefly asked for one shared /chi/ URL and then supplied the English page, so the
# pairing is language-appropriate again: an English reader is never sent to a
# Chinese-language page, and a Chinese reader is never sent to an English one.
# Nothing is rewritten here — the assertion is the point, because this is a line
# that gets "tidied" into a single constant the moment someone simplifies the table.
n_eng = src.count("https://www.ird.gov.hk/eng/welcome.htm")
n_chi = src.count("https://www.ird.gov.hk/chi/welcome.htm")
# 2 English (markup default + en string table) and 1 Chinese (zh string table).
if (n_eng, n_chi) != (2, 1):
    print(f"FAIL  IRD links: expected 2 English (markup default + en table) and 1 Chinese, "
          f"found {n_eng} / {n_chi}")
    sys.exit(1)
applied.append("disclaimer item 4 hrefs verified per language: en /eng/ · zh /chi/")

# ──────────────────────────── B6 · one disclosure pattern, two triggers
start = '  var $helpBtn = $("#ref-help"), $helpPop = $("#ref-help-panel");'
end = '\n  /* ---------- boot ---------- */'
i = src.find(start)
j = src.find(end, i)
if i < 0 or j < 0:
    print("FAIL  popover wiring block not found")
    sys.exit(1)
old_block = src[i:j]
if "$helpBtn" not in old_block or "helpOpen" not in old_block:
    print("FAIL  popover wiring block looks wrong")
    sys.exit(1)
new_block = '''  /* ---------- the help popovers (ONE pattern, two triggers) ----------
     A disclosure that happens to be an overlay: a real <button> with
     aria-expanded, a panel with role="dialog" and aria-labelledby, Escape to
     close, focus returned to the button, and NO focus trap — the panel is not
     modal, so Tab must still be able to leave it.

     Two triggers share it, which is why this is a loop rather than a one-off:
       #ref-help     the payment-reference field (section 5, back with PayMe)
       #alipay-help  the receipt route inside the AlipayHK app (phase 1)
     `data-help` names the panel, so a third one is an attribute, not code. The
     loop is the same contract the single-instance version had — same events,
     same order, same focus behaviour — so neither trigger can drift. */
  $$("[data-help]").forEach(function (btn) {
    var pop = document.getElementById(btn.getAttribute("data-help"));
    if (!pop) return;
    function helpOpen(on){
      pop.hidden = !on;
      btn.setAttribute("aria-expanded", on ? "true" : "false");
      scheduleHeight();
    }
    btn.addEventListener("click", function () { helpOpen(pop.hidden); });
    pop.addEventListener("click", function (e) {
      var el = e.target;
      while (el && el !== pop) {
        if (el.hasAttribute && el.hasAttribute("data-help-close")) {
          helpOpen(false); btn.focus(); return;
        }
        el = el.parentNode;
      }
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && !pop.hidden) { helpOpen(false); btn.focus(); }
    });
    document.addEventListener("click", function (e) {
      if (pop.hidden) return;
      if (pop.contains(e.target) || btn.contains(e.target)) return;
      helpOpen(false);
    });
  });
'''
src = src[:i] + new_block + src[j:]
applied.append("popover wiring generalised to [data-help] (both triggers)")

# ────────────────────────────────────────────────────────── write + node check
FILE.write_text(src, encoding="utf-8")

m = re.search(r"<script>(.*)</script>", src, re.S)
if not m:
    print("FAIL  no <script> block found")
    sys.exit(1)
with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as fh:
    fh.write(m.group(1))
    tmp = fh.name
r = subprocess.run(["node", "--check", tmp], capture_output=True, text=True)
if r.returncode:
    print("FAIL  node --check:\n" + (r.stderr or "")[:1500])
    sys.exit(1)
print("node --check: the script parses")

# residue: the phase attribute must be the only phase gate, and the old
# single-instance popover variables must be gone
for bad in ("$helpBtn", "$helpPop", "PHASE1 = false"):
    if bad in src:
        print(f"FAIL  residue: {bad!r} still in the file")
        sys.exit(1)

print(f"\n=== {len(applied)} changes applied ===")
for a in applied:
    print("  •", a)
hide_sel = 'html[data-phase="1"] #receipt'
print(f"\nphase gate: {src.count('data-phase')} uses · "
      f"receipt-section hide: {src.count(hide_sel)}")
