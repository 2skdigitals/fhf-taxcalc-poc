#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Apply the client's section-by-section copy sheet (23 Nov 2026) to embed/index.html.

Kevin supplied every string; they are applied character-for-character in both
languages. Nothing here re-derives the tax engine, the eight analytics events or
the ?part= routing — the only JS touched is the render of the strings the sheet
renamed, plus the transaction-ID help popover (Section 5).

Re-runnable: `python3 qa/apply_client_copy_20261123.py --restore` copies
embed/index.html.bak-pre-copy-20261123 back first (that file is git-ignored; a
fresh clone restores it from git history). Every edit asserts that its old text
occurs EXACTLY ONCE — twice means the change would land in the wrong place, zero
means the copy has already drifted.

    python3 qa/apply_client_copy_20261123.py
    python3 qa/apply_client_copy_20261123.py --restore
"""
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "embed" / "index.html"
BAK = ROOT / "embed" / "index.html.bak-pre-copy-20261123"

if "--restore" in sys.argv and BAK.exists():
    shutil.copyfile(BAK, TARGET)
    print(f"restored {TARGET.name} from {BAK.name}")

if not BAK.exists():
    shutil.copyfile(TARGET, BAK)
    print(f"baseline saved → {BAK.name}")

src = TARGET.read_text(encoding="utf-8")
edits = []


def once(old, new, label):
    """Replace `old` with `new`; fail unless `old` occurs exactly once."""
    global src
    n = src.count(old)
    if n != 1:
        raise SystemExit(f"ERROR [{label}]: old text occurs {n}x (need exactly 1)\n"
                         f"---\n{old[:240]}\n---")
    src = src.replace(old, new, 1)
    edits.append(label)


def span(start, end, new, label):
    """Replace the text from `start` to `end` (both must occur exactly once)."""
    global src
    i, j = src.find(start), src.find(end)
    if i < 0 or j < 0 or src.count(start) != 1 or src.count(end) != 1 or j <= i:
        raise SystemExit(f"ERROR [{label}]: anchors not unique/ordered "
                         f"({src.count(start)}x / {src.count(end)}x)")
    src = src[:i] + new + src[j:]
    edits.append(label)


# ═══════════════════════════════════════════════════════════════════ CSS
once("""/* quick amounts read as outlined pills that fill when they are the current value */
.quick{display:flex;flex-wrap:wrap;align-items:center;gap:8px;margin:var(--s3) 0 0}
.quick .qlab{font-size:var(--t-cap);color:var(--muted);padding-right:2px}
.quick button{
  min-height:44px;padding:0 15px;border:1px solid var(--line-2);border-radius:999px;
  background:var(--white);color:var(--ink-2);cursor:pointer;
  font-size:var(--t-sm);font-weight:500;font-variant-numeric:tabular-nums;
  transition:background-color 160ms var(--ease),border-color 160ms var(--ease),color 160ms var(--ease),transform 120ms var(--ease);
}
.quick button.is-on{background:var(--navy);border-color:var(--navy);color:#fff;font-weight:600}
.quick button:active{transform:scale(.97)}
@media (hover:hover) and (pointer:fine){
  .quick button:hover:not(.is-on){border-color:var(--navy);color:var(--navy)}
}

""",
     """/* The four quick-amount chips were removed on 23 Nov at the client's
   instruction, so the field is the only control for the gift — one question,
   one control, and ~106px of the block's height handed back. */

""", "css: remove the quick-amount chips")

once("""@media (max-width:420px){
  .result{padding:20px 18px}
  .figs > div{gap:12px}
  .figs dd{font-size:1.1875rem}
  .figs dd.is-range{font-size:.875rem}
  .quick{gap:6px}
  .quick button{padding:0 12px}
  .quick .qlab{padding-right:0}
}
/* four month chips never sit evenly on a phone: two rows of two */
@media (max-width:520px){
  .quick-mo{display:grid;grid-template-columns:1fr 1fr;gap:6px}
}
/* below this the four amounts cannot hold one line: an even row of four
   cells keeps them on one rank instead of breaking 3,000 onto its own line */
@media (max-width:380px){
  .quick-amt{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:6px}
  .quick-amt .qlab{grid-column:1 / -1;min-height:0;padding:0;line-height:1.3}
  .quick-amt button{padding:0 4px}
  select.band-select{font-size:.8125rem;padding-right:26px}
}""",
     """@media (max-width:420px){
  .result{padding:20px 18px}
  .figs > div{gap:12px}
  .figs dd{font-size:1.1875rem}
  .figs dd.is-range{font-size:.875rem}
}
/* the native band select has to hold a long range string on a 320px phone */
@media (max-width:380px){
  select.band-select{font-size:.8125rem;padding-right:26px}
}""", "css: drop the chip media queries")

once(".note{font-size:var(--t-cap);line-height:1.6;color:var(--muted);margin:var(--s3) 0 0;max-width:var(--measure)}",
     """/* The remark under the band ladder is a NOTE on the description above it, not
   body copy: it sits one step under the 13px hint (23 Nov — the client asked for
   it to read slightly smaller than the text it follows). 12px is the smallest
   step the system already owns, so nothing new enters the scale. */
.note{font-size:var(--t-eyebrow);line-height:1.6;color:var(--muted);margin:var(--s3) 0 0;max-width:var(--measure)}""",
     "css: band note one step under its hint")

once("""#result.is-below-min .result,
#result.is-below-min .benefit,
#result.is-below-min .assump{display:none}""",
     """#result.is-below-min .result,
#result.is-below-min .benefit,
#result.is-below-min .assump-block{display:none}""",
     "css: below-min hides the whole assumption block")

once("""#assumption{margin-top:var(--s6);padding-top:var(--s4);border-top:1px solid var(--line)}
#assumption + .assump{margin-top:6px}""",
     """/* The assumption is a numbered note of three lines (23 Nov). It closes the
   block on the same rule and the same rhythm the single line used. */
.assump-block{margin-top:var(--s6);padding-top:var(--s4);border-top:1px solid var(--line)}
.assump-block .assump + .assump{margin-top:6px}""",
     "css: three-line assumption block")

once(""".msg{font-size:var(--t-cap);margin:5px 0 0;color:var(--err)}
.msg.ok{color:var(--ok)}""",
     """.msg{font-size:var(--t-cap);margin:5px 0 0;color:var(--err)}
.msg.ok{color:var(--ok)}

/* ── the payment-reference help popover ────────────────────────
   It walks the donor to the AlipayHK transaction ID. An overlay INSIDE this
   frame, anchored to its own field — never a viewport-fixed dialog: the host
   hands the iframe a fixed height, and in ?part=all a full-screen modal would
   centre hundreds of pixels below where the donor is looking. Width is capped at
   the column and height at 560px with its own scroll, so the host can never clip
   it. Flat, like everything else: a hairline and white, no shadow, no blur. */
.reffield{position:relative}
.reflabel{display:flex;align-items:center;gap:8px}
.helpbtn{
  display:inline-flex;align-items:center;justify-content:center;
  width:44px;height:44px;margin:-13px -12px -13px -6px;padding:0;
  border:0;background:none;color:var(--navy);cursor:pointer;
}
.helpbtn .i{
  display:grid;place-items:center;width:19px;height:19px;border-radius:50%;
  border:1.5px solid currentColor;font-size:12px;font-weight:700;line-height:1;
}
.helpbtn:hover .i,.helpbtn[aria-expanded="true"] .i{background:var(--navy);color:#fff}
.helppop{
  position:absolute;left:0;right:0;top:calc(100% + 6px);z-index:30;
  max-width:560px;max-height:min(60vh,560px);overflow:auto;overscroll-behavior:contain;
  padding:var(--s4);background:var(--white);
  border:1px solid var(--line-2);border-radius:6px;
}
.helppop h3{margin:0 22px var(--s2) 0;font-size:var(--t-sm);font-weight:700;
            letter-spacing:-.01em;color:var(--navy)}
.helppop p{font-size:var(--t-cap);line-height:1.55;color:var(--muted);margin:0;max-width:var(--measure)}
.hclose{
  position:absolute;right:4px;top:4px;width:44px;height:44px;
  border:0;background:none;color:var(--muted);font-size:17px;line-height:1;cursor:pointer;
}
.hclose:hover{color:var(--navy)}
.hsteps{list-style:none;margin:var(--s3) 0 0;padding:0;display:grid;gap:var(--s4)}
.hsteps li{display:grid;gap:6px}
.hsteps .n{font-size:var(--t-eyebrow);font-weight:700;letter-spacing:.06em;
           text-transform:uppercase;color:var(--muted)}
.hsteps img{width:100%;max-width:400px;height:auto;border:1px solid var(--line);border-radius:4px}
.hsteps p{font-size:var(--t-cap);line-height:1.55;color:var(--ink-2);margin:0}""",
     "css: help popover")

# ═══════════════════════════════════════════════════════════════════ SECTION 1
once('<div class="step"><span class="step-n" aria-hidden="true">1</span><h2 id="s1h" data-i18n="s1.h">Your gift</h2></div>',
     '<div class="step"><span class="step-n" aria-hidden="true">1</span>'
     '<h2 id="s1h" data-i18n="s1.h">Please select and input your donation amount</h2></div>',
     "s1: heading")

once("""        <div class="quick quick-amt" role="group" aria-label="Quick amounts" data-i18n-aria="s1.quickamt">
          <span class="qlab" data-i18n="s1.quicklab">or</span>
          <button type="button" data-amt="300">300</button>
          <button type="button" data-amt="500">500</button>
          <button type="button" data-amt="1300">1,300</button>
          <button type="button" data-amt="3000">3,000</button>
        </div>
""", "", "s1: remove the quick-amount chips")

once("""
      <details class="q inset" id="what-counts">
        <summary data-i18n="s1.what.summary">What counts as a deductible gift</summary>
        <p data-i18n="s1.what.body">Only money given to a charity approved under section 88 of the Inland Revenue Ordinance can be deducted. Money paid for something in return is not a donation — raffle tickets, auction purchases, dinner seats, sponsorship that buys advertising. At or below the basic allowance you pay no salaries tax, so a gift saves you nothing.</p>
      </details>
""", "", "s1: remove the 'what counts' disclosure")

# ═══════════════════════════════════════════════════════════════════ SECTION 2
once('<div class="step"><span class="step-n" aria-hidden="true">2</span><h2 id="s1bh" data-i18n="s1.band.label">Your assessable income this year, roughly</h2></div>',
     '<div class="step"><span class="step-n" aria-hidden="true">2</span>'
     '<h2 id="s1bh" data-i18n="s1.band.label">Please select your income range or input your yearly income</h2></div>',
     "s2: heading")

once('<p class="hint" id="band-hint" data-i18n="s1.band.hint">Before allowances; the basic allowance is assumed at HK$145,000.</p>',
     '<p class="hint" id="band-hint" data-i18n="s1.band.hint">Estimated based on a single person\u2019s basic allowance of HK$145,000</p>',
     "s2: band hint")

once('<p class="note" data-i18n="s1.band.note">Above HK$2,132,500 the standard rate takes over — 15% on the first HK$5 million, 16% above it — so the last two rungs fall rather than rise. That is how the tax is built, not a bug.</p>',
     '<p class="note" data-i18n="s1.band.note">Note: Standard rates (15% on the first HK$5M; 16% thereafter) apply once Net Chargeable Income exceeds HK$2,132,500, lowering the marginal rate for the top two brackets (not a calculation error).</p>',
     "s2: band note")

once('<span data-i18n="s1.exact.summary">Use your exact income</span>',
     '<span data-i18n="s1.exact.summary">Enter exact income instead</span>',
     "s2: exact-income link")

once('<a class="btn" href="#result" id="goto-result" data-i18n="s1.goto">See what it costs you</a>',
     '<a class="btn" href="#result" id="goto-result" data-i18n="s1.goto">Check the calculation result</a>',
     "s2: CTA")

# ═══════════════════════════════════════════════════════════════════ SECTION 3
once('<div class="step"><span class="step-n" aria-hidden="true">3</span><h2 id="s2h" data-i18n="s2.h">What it costs you</h2></div>',
     '<div class="step"><span class="step-n" aria-hidden="true">3</span>'
     '<h2 id="s2h" data-i18n="s2.h">Tax Deduction Summary</h2></div>',
     "s3: heading")

once('<p class="net-label" id="net-label" data-i18n="s2.netlabel">You pay</p>',
     '<p class="net-label" id="net-label" data-i18n="s2.netlabel">Your donation</p>',
     "s3: hero label")

once('<p class="net" id="net"><span class="cur">HK$</span>1,079</p>',
     '<p class="net" id="net"><span class="cur">HK$</span>1,300</p>',
     "s3: hero figure now carries the gift")

once('<p class="hint" id="net-caption" data-i18n="s2.caption">Between the top and bottom of the range you chose.</p>',
     '<p class="hint" id="net-caption" data-i18n="s2.caption">gift powers sight-saving work\u2014with a tax deduction in return</p>',
     "s3: hero caption")

once("""        <div><dt id="gift-label" data-i18n="s2.gift">Donation</dt><dd id="gift-out">HK$1,300</dd></div>
""", "", "s3: remove the ledger row that repeated the gift")

once('<p class="benefit" id="benefit" data-i18n="s2.benefit">You give HK$1,300, all of it deductible. Every HK$100 costs you about HK$83.</p>',
     '<p class="benefit" id="benefit" data-i18n="s2.benefit">Your HK$1,300 gift qualifies for full tax deduction (est. HK$182 \u2013 221 relief), '
     'meaning just HK$1,079 \u2013 1,118 net support delivers the full sight-saving impact.</p>',
     "s3: benefit sentence")

once("""    <p class="assump" id="assumption" data-i18n="s2.assume.def">Assumed assessable income HK$345,000 – 2,132,500.</p>
    <p class="assump" id="cap" data-i18n="s2.cap.def">The cap is 35% of assessable income for the year; an ordinary gift does not reach it.</p>

    <div class="faq">
      <h3 class="faq-h" data-i18n="s2.faq.label">Common questions</h3>
      <details class="q inset" id="spouse">
        <summary data-i18n="s2.spouse.q">Can a couple combine the deduction?</summary>
        <p data-i18n="s2.spouse.a">Partly. What you cannot use — including the part above the 35% cap — your spouse may claim on their own BIR60. Their claim is capped at 35% of their own income or profits, so an unused deduction does not pass across in full.</p>
      </details>
    </div>""",
     """    <!-- the assumption, as the client numbered it on 23 Nov. Line 1 is the
         premise (the band, or the figure the donor typed), line 2 the 35% cap,
         line 3 the scope — that third line RESTORES the salaries-tax-only
         statement an earlier round removed, which closes a compliance gap. -->
    <div class="assump-block" id="assumption">
      <p class="assump" id="assume-1">Assumed Net Chargeable Income Range: HK$345,000 – 2,132,500</p>
      <p class="assump" id="cap">2. 35% deduction cap: Your full donation qualifies for deduction</p>
      <p class="assump" id="assume-3" data-i18n="s2.line3">3. Estimate for personal Salaries Tax only; does not constitute tax advice</p>
    </div>""",
     "s3: numbered assumption block; spouse FAQ removed")

# ═══════════════════════════════════════════════════════════════════ SECTION 5
once("""      <div>
        <label for="rref" data-i18n="rc.ref">Payment reference</label>
        <input id="rref" type="text" autocomplete="off" placeholder="e.g. 2026111800123"
               aria-describedby="rref-hint rref-msg" data-i18n-ph="rc.ref.ph">
        <p class="hint" id="rref-hint" data-i18n="rc.ref.hint">The transaction ID in your payment app, or on your card receipt.</p>
        <p class="msg" id="rref-msg" hidden></p>
      </div>""",
     """      <div class="reffield">
        <div class="reflabel">
          <label for="rref" data-i18n="rc.ref">Payment reference</label>
          <button type="button" class="helpbtn" id="ref-help" aria-expanded="false"
                  aria-controls="ref-help-panel" data-i18n-aria="rc.ref.help.btn">
            <span class="i" aria-hidden="true">?</span>
          </button>
        </div>
        <input id="rref" type="text" autocomplete="off" placeholder="e.g. 2026111800123"
               aria-describedby="rref-hint rref-msg" data-i18n-ph="rc.ref.ph">
        <p class="hint" id="rref-hint" data-i18n="rc.ref.hint">The transaction ID in your payment app, or on your card receipt.</p>
        <p class="msg" id="rref-msg" hidden></p>

        <!-- Where the donor finds the AlipayHK transaction ID. Two of Denise's
             three screencaps are used, cropped from the same HK$1.00 test gift:
             the success screen and the receipt record — the second one twice,
             because the ID sits at the foot of a screen whose header is what
             identifies the payment. The merchant-console capture (SC2.png) is
             deliberately not used: it is the ops view, labelled "PayMe for
             Business app", and it is not a path a donor can follow. -->
        <div class="helppop" id="ref-help-panel" role="dialog" aria-labelledby="ref-help-title" hidden>
          <button type="button" class="hclose" data-help-close
                  aria-label="Close" data-i18n-aria="rc.help.close">&#10005;</button>
          <h3 id="ref-help-title" data-i18n="rc.help.title">Finding your AlipayHK transaction ID</h3>
          <p data-i18n="rc.help.intro">When the payment completes, AlipayHK files it under Transaction History — the transaction ID is the long string of letters and numbers at the foot of that record.</p>
          <ol class="hsteps">
            <li>
              <span class="n" data-i18n="rc.help.s1t">Step 1</span>
              <img loading="lazy" src="../assets/help/alipay-step-1.jpg" width="760" height="469"
                   alt="AlipayHK payment confirmation screen" data-i18n-alt="rc.help.alt1">
              <p data-i18n="rc.help.s1">The confirmation screen shows the amount and the charity — check it is the donation you just made, then tap Done.</p>
            </li>
            <li>
              <span class="n" data-i18n="rc.help.s2t">Step 2</span>
              <img loading="lazy" src="../assets/help/alipay-step-2.jpg" width="760" height="605"
                   alt="AlipayHK transaction detail page" data-i18n-alt="rc.help.alt2">
              <p data-i18n="rc.help.s2">Open the payment again from Transaction History: the detail page repeats the merchant, the amount and the time.</p>
            </li>
            <li>
              <span class="n" data-i18n="rc.help.s3t">Step 3</span>
              <img loading="lazy" src="../assets/help/alipay-step-3.jpg" width="760" height="202"
                   alt="The transaction ID at the foot of the record" data-i18n-alt="rc.help.alt3">
              <p data-i18n="rc.help.s3">At the bottom of that page, the code above the barcode is the transaction ID. Copy the whole string and paste it here.</p>
            </li>
          </ol>
          <p data-i18n="rc.help.outro">The screens above are examples; your transaction ID appears in the same place.</p>
        </div>
      </div>""",
     "s5: payment-reference help popover")

# ═══════════════════════════════════════════════════════════════════ I18N zh-HK
Z = [
    ('"s1.h": "您的捐款",', '"s1.h": "請選擇並輸入您的捐款金額",'),
    ('      "s1.quickamt": "常用金額",\n      "s1.quickmonths": "常用月數",\n      "s1.quicklab": "或",\n', ""),
    ('"s1.band.label": "您全年應評稅入息（大約）",', '"s1.band.label": "請選擇您的收入範圍或輸入您的年薪",'),
    ('"s1.band.hint": "未扣除免稅額（以 HK$145,000 估算）。",', '"s1.band.hint": "以單身人士免稅額 HK$145,000 估算",'),
    ('"s1.band.aria": "您全年應評稅入息（大約）",', '"s1.band.aria": "請選擇您的收入範圍或輸入您的年薪",'),
    ('"s1.band.note": "應評稅入息淨額超過 HK$2,132,500 後改用標準稅率（15%，其後 16%），故最頂兩級回落，並非計算錯誤。",',
     '"s1.band.note": "註：應評稅入息淨額超過 HK$2,132,500 後改按標準稅率（首 500 萬 15%，其後 16%）計算，故最頂兩級的邊際稅率有所回落，並非計算錯誤。",'),
    ('"s1.exact.summary": "改用自己的入息數字",', '"s1.exact.summary": "改用實際入息計算",'),
    ('      "s1.what.summary": "哪些捐款才可扣稅",\n      "s1.what.body": "只有捐予《稅務條例》第 88 條認可慈善團體的款項才可扣稅。換取貨品、服務或利益的付款不屬捐款，例如獎券、拍賣購入的物品、慈善晚宴或酒席、以及帶廣告回報的贊助。應評稅入息不高於基本免稅額者無須繳付薪俸稅，捐款亦不會減少稅款。",\n', ""),
    ('"s1.goto": "看實際付出",', '"s1.goto": "查看計算結果",'),
    ('"s2.h": "實際付出",', '"s2.h": "捐款扣稅計算結果",'),
    ('"s2.netlabel": "您實際付出",', '"s2.netlabel": "您的全額捐款",'),
    ('"s2.caption": "按所選入息範圍的下限與上限計算。",', '"s2.caption": "帶來滿滿救盲力量，同時享扣稅回饋",'),
    ('      "s2.gift": "捐款金額",\n', ""),
    ('"s2.saved": "節省稅款",', '"s2.saved": "預計慈善捐款扣稅額",'),
    ('"s2.benefit": "您捐 HK$1,300，全數可作認可慈善捐款扣除。每捐 HK$100，實際付出約 HK$83。",',
     '"s2.benefit": "您的 HK$1,300 捐款可全數扣稅，享約 HK$182 – 221 稅務扣減；只需約 HK$1,079 – 1,118 實際支持，即可成就全額100%救盲力量。",'),
    ('      "s2.assume.def": "假設入息 HK$345,000 – 2,132,500。",\n      "s2.cap.def": "扣稅上限為應評稅入息的 35%（全年合計）；一般捐款不會觸及上限。",\n', ""),
    ('      "s2.faq.label": "常見問題",\n      "s2.spouse.q": "夫婦的扣稅額可否合併使用？",\n      "s2.spouse.a": "可以，但只限未用的部分。您未能用盡的扣稅額（包括超出 35% 上限而未扣除的部分），配偶可在其 BIR60 報稅表內申報；配偶本人的申報同樣以 35% 為上限，上限按其本人的入息或利潤計算，因此未用的扣稅額不能全數轉移。",\n', ""),
    ('"d.netlabel.once": "您實際付出",', '"d.netlabel.once": "您的全額捐款",'),
    ('"d.netlabel.monthly": "本年度實際付出",\n      "d.netlabel.bound": "（最少）",\n',
     '"d.netlabel.monthly": "您的全額捐款",\n'),
    ('      "d.cap.exact": "按您輸入的 {inc} 精確計算。",\n      "d.cap.unknown": "未指定入息範圍：下限為節省 HK$0，上限為最高邊際稅率 17%。",\n      "d.cap.range": "按範圍上下限計算。",\n      "d.cap.same": "範圍兩端相同。",\n      "d.gift.once": "捐款金額",\n      "d.gift.monthly": "全年總額（{n} 個月）",\n      "d.saved.once": "節省稅款",\n      "d.saved.most": "節省稅款（最多）",\n', ""),
    ('"d.assume.exact": "假設入息 {inc}（您輸入）。",', '"d.assume.exact": "1. 根據您輸入的全年應評稅入息 {inc} 計算",'),
    ('"d.assume.band": "假設入息 {band}。",', '"d.assume.band": "假設全年應評稅入息範圍：{band}",'),
    ('"d.capline.empty": "扣稅上限為應評稅入息的 35%（全年合計）。",', '"d.capline.empty": "2. 扣稅上限為應評稅入息的 35%（全年合計）。",'),
    ('"d.capline.exact.capped": "35% 上限：可扣除 {taxed}，其餘不能扣除。",', '"d.capline.exact.capped": "2. 35% 捐款扣稅上限：可扣除 {taxed}，其餘不能扣除",'),
    ('"d.capline.exact.ok": "35% 上限；未觸及，全數可扣除。",', '"d.capline.exact.ok": "2. 35% 捐款扣稅上限：此捐款額可全數扣除",'),
    ('"d.capline.unknown": "已計 35% 上限。",', '"d.capline.unknown": "2. 已計 35% 捐款扣稅上限。",'),
    ('"d.capline.zero": "扣稅上限為應評稅入息的 35%（全年合計）；捐款仍可扣除，但沒有應繳稅款可減少。",',
     '"d.capline.zero": "2. 扣稅上限為應評稅入息的 35%（全年合計）；捐款仍可扣除，但沒有應繳稅款可減少。",'),
    ('"d.capline.band.capped": "35% 上限；範圍下限可扣除 {d}。",', '"d.capline.band.capped": "2. 35% 捐款扣稅上限：範圍下限可扣除 {d}，其餘不能扣除",'),
    ('"d.capline.band.ok": "35% 上限；範圍下限全數可扣除。",', '"d.capline.band.ok": "2. 35% 捐款扣稅上限：此捐款額可全數扣除",'),
    ('      "d.benefit.range": "您捐 {g}，可作認可慈善捐款扣除。每捐 HK$100，實際付出約 {a} 至 {b}。",\n'
     '      "d.benefit.range.capped": "您捐 {g}，可作認可慈善捐款扣除（受 35% 上限所限）。每捐 HK$100，實際付出約 {a} 至 {b}。",\n'
     '      "d.benefit.capnote": "（受 35% 上限所限）",\n',
     '      "d.benefit.ok": "您的 {g} 捐款可全數扣稅，享約 {s} 稅務扣減；只需約 {n} 實際支持，即可成就全額100%救盲力量。",\n'
     '      "d.benefit.capped": "您的 {g} 捐款的扣稅額受 35% 上限所限，享約 {s} 稅務扣減；只需約 {n} 實際支持，即可成就全額100%救盲力量。",\n'),
    ('      "d.benefit.capped": "受應評稅入息 35% 上限所限，可扣除 {taxed}；節省稅款 {s}。",\n'
     '      "d.benefit.ok": "您捐 {g}，全數可作認可慈善捐款扣除。每捐 HK$100，實際付出約 {per}。",\n', ""),
]
for old, new in Z:
    once(old, new, f"i18n zh: {old.strip()[:48]}")
once('      "s2.min": "捐款金額達到或超過 HK$100 可獲得稅收減免。",',
     '      "s2.min": "捐款金額達到或超過 HK$100 可獲得稅收減免。",\n'
     '      "s2.line3": "3. 以上僅估算個人薪俸稅下的捐款扣稅，並不構成稅務建議",',
     "i18n zh: assumption line 3")
once('      "rc.ref.hint": "付款 App 交易紀錄或信用卡收據上的交易編號。",',
     '''      "rc.ref.hint": "付款 App 交易紀錄或信用卡收據上的交易編號。",
      "rc.ref.help.btn": "如何找到 AlipayHK 交易編號",
      "rc.help.title": "如何找到 AlipayHK 交易編號",
      "rc.help.intro": "付款完成後，AlipayHK 會把該筆捐款存入「交易紀錄」；交易編號就是紀錄頁最底部的長串字母與數字。",
      "rc.help.s1t": "第 1 步",
      "rc.help.s1": "付款完成的畫面會顯示金額及受惠機構，確認是您剛完成的捐款，然後按「完成」。",
      "rc.help.s2t": "第 2 步",
      "rc.help.s2": "在 AlipayHK 的「交易紀錄」找回這筆付款並開啟詳情頁，頁面會顯示受惠機構、金額及時間。",
      "rc.help.s3t": "第 3 步",
      "rc.help.s3": "在該頁最底部，條碼上方的那串字元就是交易編號；請整段複製並貼到上方的付款參考編號欄。",
      "rc.help.outro": "以上畫面僅供參考；您的交易編號會出現在相同位置。",
      "rc.help.close": "關閉",
      "rc.help.alt1": "AlipayHK 付款成功畫面",
      "rc.help.alt2": "AlipayHK 交易詳情頁",
      "rc.help.alt3": "交易詳情頁最底部的交易編號",''',
     "i18n zh: help popover strings")

# ═══════════════════════════════════════════════════════════════════ I18N en
E = [
    ('"s1.h": "Your gift",', '"s1.h": "Please select and input your donation amount",'),
    ('      "s1.quickamt": "Quick amounts",\n      "s1.quickmonths": "Quick month counts",\n      "s1.quicklab": "or",\n', ""),
    ('"s1.band.label": "Your assessable income this year, roughly",', '"s1.band.label": "Please select your income range or input your yearly income",'),
    ('"s1.band.hint": "Before allowances (HK$145,000 assumed).",', '"s1.band.hint": "Estimated based on a single person\\u2019s basic allowance of HK$145,000",'),
    ('"s1.band.aria": "Your assessable income this year, roughly",', '"s1.band.aria": "Please select your income range or input your yearly income",'),
    ('"s1.band.note": "Above HK$2,132,500 the standard rate applies — 15%, then 16% — so the last two rungs fall, by design.",',
     '"s1.band.note": "Note: Standard rates (15% on the first HK$5M; 16% thereafter) apply once Net Chargeable Income exceeds HK$2,132,500, lowering the marginal rate for the top two brackets (not a calculation error).",'),
    ('"s1.exact.summary": "Use your exact income",', '"s1.exact.summary": "Enter exact income instead",'),
    ('      "s1.what.summary": "What counts as a deductible gift",\n      "s1.what.body": "Only money given to a charity approved under section 88 of the Inland Revenue Ordinance can be deducted. Money paid for something in return is not a donation — raffle tickets, auction purchases, dinner seats, sponsorship that buys advertising. At or below the basic allowance you pay no salaries tax, so a gift saves you nothing.",\n', ""),
    ('"s1.goto": "See what it costs you",', '"s1.goto": "Check the calculation result",'),
    ('"s2.h": "What it costs you",', '"s2.h": "Tax Deduction Summary",'),
    ('"s2.netlabel": "You pay",', '"s2.netlabel": "Your donation",'),
    ('"s2.caption": "Between the top and bottom of the range you chose.",', '"s2.caption": "gift powers sight-saving work\\u2014with a tax deduction in return",'),
    ('      "s2.gift": "Donation",\n', ""),
    ('"s2.saved": "Tax saved",', '"s2.saved": "Estimated charitable tax deduction",'),
    ('"s2.benefit": "You give HK$1,300, all of it deductible. Every HK$100 costs you about HK$83.",',
     '"s2.benefit": "Your HK$1,300 gift qualifies for full tax deduction (est. HK$182 \\u2013 221 relief), meaning just HK$1,079 \\u2013 1,118 net support delivers the full sight-saving impact.",'),
    ('      "s2.assume.def": "Income assumed HK$345,000 – 2,132,500.",\n      "s2.cap.def": "The cap is 35% of assessable income for the year; an ordinary gift does not reach it.",\n', ""),
    ('      "s2.faq.label": "Common questions",\n      "s2.spouse.q": "Can a couple combine the deduction?",\n      "s2.spouse.a": "Partly. What you cannot use — including the part above the 35% cap — your spouse may claim on their own BIR60. Their claim is capped at 35% of their own income or profits, so an unused deduction does not pass across in full.",\n', ""),
    ('"d.netlabel.once": "You pay",', '"d.netlabel.once": "Your donation",'),
    ('"d.netlabel.monthly": "You pay this year",\n      "d.netlabel.bound": " (at least)",\n', '"d.netlabel.monthly": "Your donation",\n'),
    ('      "d.cap.exact": "Worked exactly from {inc}.",\n      "d.cap.unknown": "No range chosen: HK$0 at one end, the top 17% at the other.",\n      "d.cap.range": "Both ends of your range.",\n      "d.cap.same": "The same at both ends.",\n      "d.gift.once": "Donation",\n      "d.gift.monthly": "Total for the year ({n} months)",\n      "d.saved.once": "Tax saved",\n      "d.saved.most": "Tax saved at most",\n', ""),
    ('"d.assume.exact": "Income assumed {inc}, as you entered it.",', '"d.assume.exact": "1. Based on your entered Net Chargeable Income of {inc}",'),
    ('"d.assume.band": "Income assumed {band}.",', '"d.assume.band": "Assumed Net Chargeable Income Range: {band}",'),
    ('"d.capline.empty": "The cap is 35% of assessable income for the year.",', '"d.capline.empty": "2. The cap is 35% of assessable income for the year",'),
    ('"d.capline.exact.capped": "35% cap: {taxed} deductible, the rest not.",', '"d.capline.exact.capped": "2. 35% deduction cap: {taxed} is deductible, the rest is not",'),
    ('"d.capline.exact.ok": "35% cap — not reached, so all of it is deductible.",', '"d.capline.exact.ok": "2. 35% deduction cap: Your full donation qualifies for deduction",'),
    ('"d.capline.unknown": "35% cap applied.",', '"d.capline.unknown": "2. 35% deduction cap applied",'),
    ('"d.capline.zero": "The cap is 35% of assessable income for the year; the gift is still deductible, but there is no tax to reduce.",',
     '"d.capline.zero": "2. The cap is 35% of assessable income for the year; the gift is still deductible, but there is no tax to reduce",'),
    ('"d.capline.band.capped": "35% cap — {d} deductible at your range\'s low end.",', '"d.capline.band.capped": "2. 35% deduction cap: {d} is deductible at the low end of your range",'),
    ('"d.capline.band.ok": "35% cap — all of it deductible at your range\'s low end.",', '"d.capline.band.ok": "2. 35% deduction cap: Your full donation qualifies for deduction",'),
    ('      "d.benefit.range": "{g} given, all of it deductible. Every HK$100 costs you about {a} to {b}.",\n'
     '      "d.benefit.range.capped": "{g} given; the deductible part is held to the 35% cap. Every HK$100 costs you about {a} to {b}.",\n'
     '      "d.benefit.capnote": " (held to the 35% cap)",\n',
     '      "d.benefit.ok": "Your {g} gift qualifies for full tax deduction (est. {s} relief), meaning just {n} net support delivers the full sight-saving impact.",\n'
     '      "d.benefit.capped": "Your {g} gift is deductible up to the 35% cap (est. {s} relief), meaning just {n} net support delivers the full sight-saving impact.",\n'),
    ('      "d.benefit.capped": "The 35% cap holds the deduction to {taxed}. Tax saved {s}.",\n'
     '      "d.benefit.ok": "{g} given, all of it deductible as a recognised charitable donation. Every HK$100 costs you about {per}.",\n', ""),
]
for old, new in E:
    once(old, new, f"i18n en: {old.strip()[:48]}")
once('      "s2.min": "Donation amount at HK$100 or above will receive tax deduction receipt",',
     '      "s2.min": "Donation amount at HK$100 or above will receive tax deduction receipt",\n'
     '      "s2.line3": "3. Estimate for personal Salaries Tax only; does not constitute tax advice",',
     "i18n en: assumption line 3")
once('      "rc.ref.hint": "The transaction ID in your payment app, or on your card receipt.",',
     '''      "rc.ref.hint": "The transaction ID in your payment app, or on your card receipt.",
      "rc.ref.help.btn": "How to find your AlipayHK transaction ID",
      "rc.help.title": "Finding your AlipayHK transaction ID",
      "rc.help.intro": "When the payment completes, AlipayHK files it under Transaction History \\u2014 the transaction ID is the long string of letters and numbers at the foot of that record.",
      "rc.help.s1t": "Step 1",
      "rc.help.s1": "The confirmation screen shows the amount and the charity \\u2014 check it is the donation you just made, then tap Done.",
      "rc.help.s2t": "Step 2",
      "rc.help.s2": "Open the payment again from Transaction History: the detail page repeats the merchant, the amount and the time.",
      "rc.help.s3t": "Step 3",
      "rc.help.s3": "At the bottom of that page, the code above the barcode is the transaction ID. Copy the whole string and paste it here.",
      "rc.help.outro": "The screens above are examples; your transaction ID appears in the same place.",
      "rc.help.close": "Close",
      "rc.help.alt1": "AlipayHK payment confirmation screen",
      "rc.help.alt2": "AlipayHK transaction detail page",
      "rc.help.alt3": "The transaction ID at the foot of the record",''',
     "i18n en: help popover strings")

# ═══════════════════════════════════════════════════════════════════ JS · render
span("    /* hero */", "    $$(\".qr-amount\")",
     """    /* hero — the figure is the DONATION itself (23 Nov): the block's headline
       label is 您的全額捐款 / Your donation, and the ledger row that used to
       repeat the gift is gone, so the amount lives here and nowhere else. The
       net-cost figure did not disappear — it is the 實際支持 number in the
       benefit sentence, computed from the donor's own gift. */
    var netEl = $("#net");
    netEl.innerHTML = '<span class="cur">HK$</span>' + (annual > 0 ? fmt(annual) : "—");
    netEl.classList.remove("is-range");
    $("#net-label").textContent = st.mode === "monthly"
      ? t("d.netlabel.monthly") : t("d.netlabel.once");
    /* The caption is the client's brand line, not a computation: the range
       provenance it used to carry now lives in assumption line 1. */
    $("#net-caption").textContent = annual <= 0 ? t("d.cap.empty") : t("s2.caption");

    /* the ledger: the saving and the rate. The gift row is gone. */
    $("#saved").textContent = annual <= 0 ? money(0)
      : isRange ? money(savedLow) + t("d.range.sep") + money(savedHigh)
      : money(savedHigh);
    $("#saved").classList.toggle("is-range", isRange);

    /* the rate word: marginal only where the saving really is marginal (one
       rate across the deducted amount); standard in the standard-rate zone;
       generic once the gift crosses slices, because the average is then not a
       marginal rate. */
    var rateKey = "generic";
    if (!isRange && !isUnknown && exactInc) {
      var marg = __fhfTax.marginal(exactInc);
      if (Math.abs(rateHigh - marg) < 0.0006) {
        rateKey = exactInc >= __fhfTax.stdZoneFrom ? "standard" : "marginal";
      }
    }
    $("#rate-label").textContent = t("d.ratelabel." + rateKey);
    $("#rate").textContent = annual <= 0 ? "—"
      : isRange ? pct(rateLow) + " – " + pct(rateHigh) : pct(rateHigh);

    /* the numbered assumption. Line 1 is the premise — the band, or the figure
       the donor typed; line 2 the 35% cap, computed so it can never claim the
       gift is fully deductible once the cap bites; line 3 is static copy. */
    $("#assume-1").textContent = annual <= 0 ? t("d.assume.empty")
      : exactInc ? t("d.assume.exact", {inc: money(exactInc)})
      : isUnknown ? t("d.assume.unknown")
      : t("d.assume.band", {band: t("band." + st.band)});

    $("#cap").textContent = annual <= 0
      ? t("d.capline.empty")
      : exactInc ? (capped
          ? t("d.capline.exact.capped", {taxed: money(taxed)})
          : t("d.capline.exact.ok"))
      : isUnknown ? t("d.capline.unknown")
      : (!isRange && savedHigh === 0)
          ? t("d.capline.zero")
      : (capped
          ? t("d.capline.band.capped", {d: money(__fhfTax.deductible(annual, lo))})
          : t("d.capline.band.ok"));

    /* C6 — "you give this, you get that back". The sentence is the client's
       (23 Nov); every figure in it computes from the donor's own gift. Two
       shapes, because one sentence cannot be true for a capped gift: the
       "可全數扣稅 / full tax deduction" clause belongs to the uncapped case
       only, and the capped shape says so instead. */
    var bEl = $("#benefit");
    if (bEl) {
      /* HK$182 – 221, HK$1,079 – 1,118: one currency mark, then the second
         figure bare — the client's own rendering of a two-figure range. */
      var span2 = function (a, b) {
        a = Math.round(a); b = Math.round(b);
        return a === b ? money(a) : "HK$" + fmt(a) + " – " + fmt(b);
      };
      var netLo = annual - savedHigh, netHi = annual - savedLow;
      if (annual <= 0) {
        bEl.textContent = t("d.benefit.empty");
      } else if (savedHigh === 0) {
        bEl.textContent = t("d.benefit.zero", {g: money(annual)});
      } else {
        bEl.textContent = t(capped ? "d.benefit.capped" : "d.benefit.ok", {
          g: money(annual),
          s: span2(savedLow, savedHigh),
          n: span2(netLo, netHi)
        });
      }
    }

""", "js: render — donation hero, three-line assumption, computed benefit")

once("""    if (touched) { $("#upd").hidden = false; }
    syncChips();
    scheduleHeight();""",
     """    if (touched) { $("#upd").hidden = false; }
    scheduleHeight();""", "js: drop the chip sync call")

once("""  /* ---------- quick-value chips reflect the current value ----------
     Presentation only: the value still lives in st.amount / st.months, and
     the chips only ever set it. No new copy, no new state. */
  function syncChips(){
    $$("[data-amt]").forEach(function(b){
      b.classList.toggle("is-on", String(st.amount) === String(b.getAttribute("data-amt")));
    });
  }
""", "", "js: remove syncChips")

once("""  $$("[data-amt]").forEach(function (b) {
    b.addEventListener("click", function () {
      firstTouch(); touched = true;
      st.amount = parseInt(b.dataset.amt,10);
      $("#gift").value = fmt(st.amount);
      render(); resultShown();
    });
  });
""", "", "js: remove the chip click handlers")

once("""  /* ---------- boot ---------- */""",
     """  /* ---------- the payment-reference help popover ----------
     A disclosure that happens to be an overlay: a real <button> with
     aria-expanded, a panel with role="dialog" and aria-labelledby, Escape to
     close, focus returned to the button, and NO focus trap — the panel is not
     modal, so Tab must still be able to leave it. */
  var $helpBtn = $("#ref-help"), $helpPop = $("#ref-help-panel");
  function helpOpen(on){
    if (!$helpBtn || !$helpPop) return;
    $helpPop.hidden = !on;
    $helpBtn.setAttribute("aria-expanded", on ? "true" : "false");
    scheduleHeight();
  }
  if ($helpBtn && $helpPop) {
    $helpBtn.addEventListener("click", function () { helpOpen($helpPop.hidden); });
    $helpPop.addEventListener("click", function (e) {
      var el = e.target;
      while (el && el !== $helpPop) {
        if (el.hasAttribute && el.hasAttribute("data-help-close")) {
          helpOpen(false); $helpBtn.focus(); return;
        }
        el = el.parentNode;
      }
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && !$helpPop.hidden) { helpOpen(false); $helpBtn.focus(); }
    });
    document.addEventListener("click", function (e) {
      if ($helpPop.hidden) return;
      if ($helpPop.contains(e.target) || $helpBtn.contains(e.target)) return;
      helpOpen(false);
    });
  }

  /* ---------- boot ---------- */""", "js: help popover behaviour")

TARGET.write_text(src, encoding="utf-8")
print(f"{len(edits)} edits applied to embed/index.html")
for i, e in enumerate(edits, 1):
    print(f"  {i:>2}. {e}")
