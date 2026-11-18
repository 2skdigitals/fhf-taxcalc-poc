#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Add the EN build to embed/index.html — a language layer, not a fork.

Run from a clean backup so the change list is generated from the applied
record rather than transcribed:

    python3 qa/apply_en_20261115.py --dry
    python3 qa/apply_en_20261115.py

Every replacement is asserted to occur EXACTLY ONCE. A string appearing twice
means the change lands in the wrong place; one appearing zero times means the
copy has already drifted. Nothing about the tax engine, the 35% cap, the exact
income path, the payment rails, the receipt capture, postMessage or GTM moves:
the only things added are two string tables and the attributes that point at
them.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "embed" / "index.html.bak-pre-en-20261115"
OUT = ROOT / "embed" / "index.html"

P = []          # (name, old, new)


def R(name, old, new):
    P.append((name, old, new))


# ===========================================================================
# 1 · the two string tables, the lookup, and the two entry points
# ===========================================================================
TABLE = r'''  var st = {amount:1300, band:"r17", mode:"once", months:12, exact:0};
  var touched = false, lastH = 0, sent = {};

  /* ============================================================
     LANGUAGE LAYER — one build, two authored string tables.

     Nothing below this comment knows about tax, and nothing in the tax
     engine or the event wiring knows about language. `?lang=en` at boot,
     or {type:"fhf-config", config:{lang:"en"}} at any moment, swaps every
     user-facing string in place. The frame is never re-loaded: re-setting
     iframe.src from inside a ready handler is the infinite-reload trap
     (docs/INTERFACE.md §4).

     The Chinese table is the delivered zh-HK copy, character for character;
     qa/lang_parity.py proves it against the pre-change file. The English
     column is authored English, not a transliteration — IRD terminology,
     second person, short sentences.
     ============================================================ */
  var I18N = {
  "zh-HK": {
    "title": "慈善捐款扣稅計算機 — POC",
    "poc.demo": "示範用 · 二維碼為測試碼，非真實收款碼",

    "s1.eyebrow": "步驟一",
    "s1.h": "輸入兩項資料",
    "s1.lede": "只需一個捐款金額，以及大約的入息範圍。",
    "s1.legend": "捐款方式",
    "s1.once": "單次捐款",
    "s1.monthly": "每月捐款",
    "s1.gift": "捐款金額（HK$）",
    "s1.quickamt": "快速金額",
    "s1.gifthint": "可直接輸入金額，或選用上方預設金額。",
    "s1.months.label": "本課稅年度內的捐款月數",
    "s1.months.hint": "扣稅按全年捐款總額計算；如只捐款數個月，請填寫實際月數。",
    "s1.quickmonths": "快速月數",
    "s1.band.legend": "您全年應評稅入息大約是？（未扣除免稅額；免稅額以 HK$145,000 估算）",
    "s1.band.aria": "您全年應評稅入息大約是？（未扣除免稅額）",
    "s1.band.unknown": "不確定 — 顯示估算範圍",
    "s1.band.r0": "無須繳稅",
    "s1.band.r2": "約 2%",
    "s1.band.r6": "約 6%",
    "s1.band.r10": "約 10%",
    "s1.band.r14": "約 14%",
    "s1.band.r17": "約 17%",
    "s1.band.r15": "標準 15%",
    "s1.band.r16": "標準 16%",
    "s1.band.note": "應評稅入息低於約 HK$145,000（基本免稅額）者，或無須繳付薪俸稅，該筆捐款便不能扣稅。\n      應評稅入息越高，邊際稅率通常越高（最高 17%）；但應評稅入息淨額超過約 HK$2,132,500 後，稅務局會改用<b>標準稅率</b>計算\n      （首 HK$500 萬 15%，其後 16%），因此最頂兩級的比率反而回落 —— 這是香港薪俸稅的設計，並非計算錯誤。",
    "s1.band.r0.label": "HK$145,000 以下",
    "s1.band.r16.label": "HK$5,000,000 以上",
    "s1.mob.unknown": "不確定 — 顯示 2% – 17% 範圍",
    "s1.mob.r0": "HK$145,000 以下 — 無須繳稅",
    "s1.mob.r2": "HK$145,000 – 195,000 — 約 2%",
    "s1.mob.r6": "HK$195,000 – 245,000 — 約 6%",
    "s1.mob.r10": "HK$245,000 – 295,000 — 約 10%",
    "s1.mob.r14": "HK$295,000 – 345,000 — 約 14%",
    "s1.mob.r17": "HK$345,000 – 2,132,500 — 約 17%",
    "s1.mob.r15": "HK$2,132,500 – 5,000,000 — 標準 15%",
    "s1.mob.r16": "HK$5,000,000 以上 — 標準 16%",
    "s1.exact.summary": "想更準確？輸入您的應評稅入息",
    "s1.exact.label": "全年應評稅入息（HK$，未扣除免稅額）",
    "s1.exact.ph": "例如 500,000",
    "s1.exact.hint": "填寫後改用單一數字，並計入累進稅級及 35% 上限。此數字只用於本頁計算，不會傳送或儲存。",
    "s1.goto": "查看結果 →",
    "s1.updated": "結果已更新",

    "s2.eyebrow": "步驟二",
    "s2.h": "您的估算結果",
    "s2.netlabel": "實際付出",
    "s2.caption": "這是實際由您支付的金額。",
    "s2.gift": "捐款金額",
    "s2.saved": "預計節省稅款",
    "s2.rate": "估算採用的邊際稅率",
    "s2.benefit": "您捐 HK$1,300，全數可作認可慈善捐款扣除；估算稅務回饋 HK$221，即每捐 HK$100，實際付出約 HK$83。",
    "s2.assump.k1": "假設：",
    "s2.assume.def": "應評稅入息 HK$345,000 – 2,132,500 · 邊際稅率 17%。",
    "s2.assume.tail": "更改上述任何一項，估算會即時更新。此為估算，並未計算其他扣除或免稅額。",
    "s2.assump.k2": "上限：",
    "s2.cap.def": "扣稅上限為應評稅入息的 35%（全年合計）；一般捐款金額不會觸及上限。",
    "s2.scope": "本計算機只估算個人在薪俸稅下的捐款扣稅，並非稅務建議。",
    "s2.spouse.q": "夫婦的扣稅額可以合併使用嗎？",
    "s2.spouse.a": "若您未能用盡扣稅額（包括超過 35% 上限而未扣除的部分），配偶可在其 BIR60 報稅表內申報。但配偶本人的申報同樣以 35% 為上限，上限按其本人的入息或利潤計算；因此未用的扣稅額並非可全數轉移。",

    "s3.eyebrow": "步驟三 · 付款方式",
    "s3.h": "三種捐款方式",
    "s3.lede": "PayMe、AlipayHK 二維碼，以及前往護瞳行動網站的信用卡。",
    "s3.badge": "POC 測試 <span style=\"opacity:.6\">test mode</span>",
    "s3.note": "PayMe 及 AlipayHK 以二維碼於您自己的 App 內完成；信用卡則前往護瞳行動現有的捐款頁。正式上線時會換成客戶提供的商戶碼。",
    "s3.payme.desk": "用手機掃描下方二維碼完成捐款",
    "s3.payme.mob": "長按下方二維碼儲存，並於 PayMe 內完成捐款",
    "s3.alipay.desk": "用手機掃描下方二維碼完成捐款",
    "s3.alipay.mob": "長按下方二維碼儲存，並於 AlipayHK 內完成捐款",
    "s3.card.nm": "信用卡",
    "s3.card.sub": "前往護瞳行動捐款頁，以信用卡完成捐款",
    "s3.qr.payme": "PayMe 二維碼",
    "s3.qr.alipay": "AlipayHK 二維碼",
    "s3.qr.poc": "POC 測試碼",
    "s3.qr.alt.payme": "PayMe 測試二維碼（POC，非真實收款碼）",
    "s3.qr.alt.alipay": "AlipayHK 測試二維碼（POC，非真實收款碼）",
    "s3.qr.desk.h": "用手機掃描二維碼捐款",
    "s3.qr.desk.p": "請以另一部手機的相機或付款 App 掃描，然後輸入 <strong class=\"qr-amount\">HK$1,300</strong>。",
    "s3.qr.mob.h": "以手機捐款：長按二維碼，分享至付款 App",
    "s3.qr.mob.p": "長按上方<strong>對應的</strong>二維碼儲存圖片（每個 App 一個碼），再開啟 <b>PayMe</b> 或 <b>AlipayHK</b>，使用該 App 內的「掃描」或「相簿」功能選取該二維碼，然後輸入 <strong class=\"qr-amount\">HK$1,300</strong>。",
    "s3.qr.fine": "二維碼為靜態碼，本身不包含金額，須於付款 App 內自行輸入金額。",
    "s3.dl.hint": "<b>App 開啟測試（POC）：</b>點按下方按鈕，測試 iframe 內能否開啟付款 App。正式版將採用商戶提供的 deep link。",
    "s3.dl.payme": "測試叫起 PayMe",
    "s3.dl.alipay": "測試叫起 AlipayHK",
    "s3.monthly": "想每月捐款？",

    "rc.h": "需要扣稅收據？只需留下姓名及電郵。",
    "rc.lede": "我們只需收據抬頭及電郵，用以發出正式收據。課稅年度內捐款總額滿 HK$100，方可獲發正式收據。",
    "rc.name": "姓名（收據抬頭）",
    "rc.email": "電郵",
    "rc.name.ph": "陳大文",
    "rc.consent": "本人同意護瞳行動使用本人的姓名及電郵，以發出扣稅收據。",
    "rc.disclink": "使用本計算機及提交資料前，請先閱讀<a href=\"#disclaimer\" id=\"disc-link\">免責聲明</a>。",
    "rc.submit": "留下資料",
    "rc.poc": "POC 示範：資料只保留於本測試頁的記憶體，不會傳送至任何伺服器，亦不會儲存。正式版將由 2SK 建立的收據系統接收，並依客戶指示傳送至其 CRM。",
    "rc.disc.summary": "免責聲明",
    "rc.disc.body": "本計算機只提供估算，並非稅務建議，亦不能取代專業意見。估算依據稅務局於所示課稅年度的規定，只計入認可慈善捐款的扣稅，並未計算其他扣除、免稅額或稅務寬減；亦不涵蓋利潤稅、個人入息課稅或夫婦合併評稅。實際可扣除金額及應繳稅款以稅務局的評定為準。本計算機不會收集或儲存任何資料；您在本表格自願提供的姓名及電郵，只用作發出扣稅收據。",
    "foot.legal": "* 實際可扣除金額以稅務局的評定為準。扣稅上限為應評稅入息或利潤的 35%；在可扣除的金額之內，所節省的稅款約為該金額乘以您的適用稅率（最高 17%）。",

    "band.unknown": "不確定",
    "band.r0": "HK$145,000 以下",
    "band.r2": "HK$145,000 – 195,000",
    "band.r6": "HK$195,000 – 245,000",
    "band.r10": "HK$245,000 – 295,000",
    "band.r14": "HK$295,000 – 345,000",
    "band.r17": "HK$345,000 – 2,132,500",
    "band.r15": "HK$2,132,500 – 5,000,000",
    "band.r16": "HK$5,000,000 以上",

    "d.netlabel.once": "實際付出",
    "d.netlabel.monthly": "本年度實際付出",
    "d.netlabel.bound": "（最少）",
    "d.cap.monthly": "每月 {a} × {n} 個月 = 全年合計 {total}。",
    "d.cap.empty": "輸入捐款金額後，這裡會顯示您實際付出多少。",
    "d.cap.exact": "按您輸入的應評稅入息 {inc} 精確計算，已計入累進稅級及 35% 上限。",
    "d.cap.unknown": "未指定入息範圍：下限為無須繳稅（節省 HK$0），上限為最高邊際稅率 17%。",
    "d.cap.range": "範圍來自所選入息範圍的下限與上限。",
    "d.cap.same": "在所選入息範圍內，這筆捐款節省的稅款相同。",
    "d.gift.once": "捐款金額",
    "d.gift.monthly": "全年捐款總額（{n} 個月）",
    "d.saved.once": "預計節省稅款",
    "d.saved.most": "預計節省稅款（最多）",
    "d.range.sep": " 至 ",
    "d.rate.generic": "稅率",
    "d.rate.marginal": "邊際稅率",
    "d.rate.standard": "標準稅率",
    "d.ratelabel.generic": "估算採用的稅率",
    "d.ratelabel.marginal": "估算採用的邊際稅率",
    "d.ratelabel.standard": "估算採用的標準稅率",
    "d.assume.empty": "尚未輸入捐款金額。",
    "d.assume.exact": "應評稅入息 {inc}（您輸入）· 已計入累進稅級及 35% 上限。",
    "d.assume.unknown": "應評稅入息範圍未指定 · 由無須繳稅（0%）至最高 17%。",
    "d.assume.band": "應評稅入息 {band} · 按範圍下限與上限分別計算。",
    "d.capline.empty": "扣稅上限為應評稅入息的 35%（全年合計）。",
    "d.capline.exact.capped": "扣稅上限為應評稅入息的 35%（全年合計）：可扣除 {taxed}，超出部分不能扣除。",
    "d.capline.exact.ok": "扣稅上限為應評稅入息的 35%（全年合計）；未觸及上限，全數可扣除。",
    "d.capline.unknown": "扣稅上限為應評稅入息的 35%（全年合計）；上限已計入。",
    "d.capline.zero": "扣稅上限為應評稅入息的 35%（全年合計）；捐款仍可扣除，但沒有應繳稅款可減少。",
    "d.capline.band.capped": "扣稅上限為應評稅入息的 35%（全年合計）；所選範圍下限可扣除 {d}。",
    "d.capline.band.ok": "扣稅上限為應評稅入息的 35%（全年合計）；所選範圍下限全數可扣除。",
    "d.benefit.empty": "輸入捐款金額後，這裡會顯示您實際付出多少、節省多少稅款。",
    "d.benefit.range": "您捐 {g}，可作認可慈善捐款扣除{cap}；預計稅務回饋 {lo} 至 {hi}，即每捐 HK$100，實際付出約 {a} 至 {b}。",
    "d.benefit.capnote": "（受 35% 上限限制）",
    "d.benefit.zero": "您捐 {g}，可作認可慈善捐款扣除。以您的入息水平估算，無須繳付薪俸稅，因此這筆捐款不會減少稅款。",
    "d.benefit.capped": "您捐 {g}。可扣除金額受應評稅入息 35% 上限所限，為 {taxed}，超出部分不能扣除；預計節省稅款 {s}。",
    "d.benefit.ok": "您捐 {g}，全數可作認可慈善捐款扣除；預計稅務回饋 {s}，即每捐 HK$100，實際付出約 {per}。",
    "d.announce.monthly": "每月 {a}，共 {n} 個月，全年合計 {total}。",
    "d.announce.once": "捐款 {v}。",
    "d.announce.range": " 預計節省稅款由 {lo} 至 {hi}。",
    "d.announce.single": " 預計節省稅款 {v}，{w} {p}。",
    "d.months.one": "1 個月",
    "d.months.n": "{n} 個月",
    "d.dl.open": "已嘗試開啟 {app}…",
    "d.dl.notframed": "本頁未嵌入 iframe，因此無法測試 App 跳轉 —— 請在 Test Bench 或 CMS 內的 iframe 版本測試。",
    "d.dl.blocked": "⚠️ 被 iframe 阻止（需要 allow-top-navigation-by-user-activation）。",
    "d.dl.noapp": "頁面仍然停留於此 —— 表示瀏覽器或 iframe 未處理此 App scheme（iOS Safari 及沙盒 iframe 常見）。正式版需要二維碼或頂層跳轉。",
    "d.rv.name": "請輸入收據抬頭姓名。",
    "d.rv.mail": "請輸入有效電郵。",
    "d.rv.consent": "請先勾選同意。",
    "d.rv.ok": "多謝您。我們會於您捐款後跟進發出收據（POC：尚未接駁後端）。",
    "d.rv.done": "已收到"
  },

  "en": {
    "title": "Donation tax calculator — POC",
    "poc.demo": "Demo only · these QR codes are test codes, not live payment codes",

    "s1.eyebrow": "Step 1",
    "s1.h": "Enter two things",
    "s1.lede": "Just the amount you are giving, and roughly what you earn.",
    "s1.legend": "How you give",
    "s1.once": "One-off",
    "s1.monthly": "Monthly",
    "s1.gift": "Donation amount (HK$)",
    "s1.quickamt": "Quick amounts",
    "s1.gifthint": "Type an amount, or pick one above.",
    "s1.months.label": "Months you give in this year of assessment",
    "s1.months.hint": "The deduction uses your total for the year, so if you give for only some months, enter the months you actually give.",
    "s1.quickmonths": "Quick month counts",
    "s1.band.legend": "Roughly what is your assessable income for the year? (Before allowances; the allowance is estimated at HK$145,000)",
    "s1.band.aria": "Roughly what is your assessable income for the year? (Before allowances)",
    "s1.band.unknown": "Not sure — show me a range",
    "s1.band.r0": "No tax payable",
    "s1.band.r2": "About 2%",
    "s1.band.r6": "About 6%",
    "s1.band.r10": "About 10%",
    "s1.band.r14": "About 14%",
    "s1.band.r17": "About 17%",
    "s1.band.r15": "Standard 15%",
    "s1.band.r16": "Standard 16%",
    "s1.band.note": "If your assessable income is below about HK$145,000 (the basic allowance), or you pay no salaries tax, this donation saves you nothing.\n      The higher your assessable income, the higher your marginal rate usually is, up to 17%. Above about HK$2,132,500 of net assessable income the Inland Revenue Department charges the <b>standard rate</b> instead\n      — 15% on the first HK$5 million, 16% above it — so the top two rungs go down, not up. That is how Hong Kong salaries tax is designed, not a calculation error.",
    "s1.band.r0.label": "Below HK$145,000",
    "s1.band.r16.label": "HK$5,000,000 and above",
    "s1.mob.unknown": "Not sure — show a 2% – 17% range",
    "s1.mob.r0": "Below HK$145,000 — no tax payable",
    "s1.mob.r2": "HK$145,000 – 195,000 — about 2%",
    "s1.mob.r6": "HK$195,000 – 245,000 — about 6%",
    "s1.mob.r10": "HK$245,000 – 295,000 — about 10%",
    "s1.mob.r14": "HK$295,000 – 345,000 — about 14%",
    "s1.mob.r17": "HK$345,000 – 2,132,500 — about 17%",
    "s1.mob.r15": "HK$2,132,500 – 5,000,000 — standard 15%",
    "s1.mob.r16": "HK$5,000,000 and above — standard 16%",
    "s1.exact.summary": "Want a closer figure? Enter your assessable income",
    "s1.exact.label": "Assessable income for the year (HK$, before allowances)",
    "s1.exact.ph": "e.g. 500,000",
    "s1.exact.hint": "A figure here gives you one number, worked through the progressive bands and the 35% cap. It is used for this page only — never sent, never stored.",
    "s1.goto": "See the result →",
    "s1.updated": "Result updated",

    "s2.eyebrow": "Step 2",
    "s2.h": "Your estimate",
    "s2.netlabel": "You actually pay",
    "s2.caption": "This is the amount you actually pay.",
    "s2.gift": "Donation",
    "s2.saved": "Estimated tax saved",
    "s2.rate": "Marginal rate used",
    "s2.benefit": "You give HK$1,300, all of it deductible as a recognised charitable donation. Estimated tax back HK$221, so every HK$100 you give costs you about HK$83.",
    "s2.assump.k1": "Assumptions:",
    "s2.assume.def": "Assessable income HK$345,000 – 2,132,500 · marginal rate 17%.",
    "s2.assume.tail": "Change either one and the estimate updates. Other deductions and allowances are not included.",
    "s2.assump.k2": "Cap:",
    "s2.cap.def": "The cap is 35% of your assessable income, taken for the year. An ordinary donation does not reach it.",
    "s2.scope": "This estimates the donation deduction for one person under salaries tax only. It is not tax advice.",
    "s2.spouse.q": "Can a couple combine their deduction?",
    "s2.spouse.a": "If you cannot use all of your deduction — including the part above the 35% cap — your spouse may claim it on their own BIR60. Their claim is still capped at 35% of their own income or profits, so an unused deduction cannot be passed across in full.",

    "s3.eyebrow": "Step 3 · Payment",
    "s3.h": "Three ways to give",
    "s3.lede": "PayMe and AlipayHK QR codes, and a credit card that takes you to the Fred Hollows Foundation site.",
    "s3.badge": "POC test mode",
    "s3.note": "PayMe and AlipayHK are paid by QR code in your own app. The credit card goes to the Foundation's existing donation page. Live, these become the merchant codes the charity supplies.",
    "s3.payme.desk": "Scan the QR code below on your phone to give",
    "s3.payme.mob": "Press and hold the QR code below to save it, then give in PayMe",
    "s3.alipay.desk": "Scan the QR code below on your phone to give",
    "s3.alipay.mob": "Press and hold the QR code below to save it, then give in AlipayHK",
    "s3.card.nm": "Credit card",
    "s3.card.sub": "Go to the Foundation's donation page and give by card",
    "s3.qr.payme": "PayMe QR code",
    "s3.qr.alipay": "AlipayHK QR code",
    "s3.qr.poc": "POC test code",
    "s3.qr.alt.payme": "PayMe test QR code (POC, not a live payment code)",
    "s3.qr.alt.alipay": "AlipayHK test QR code (POC, not a live payment code)",
    "s3.qr.desk.h": "Scan the QR code to give",
    "s3.qr.desk.p": "Scan it with the camera or payment app on another phone, then enter <strong class=\"qr-amount\">HK$1,300</strong>.",
    "s3.qr.mob.h": "Giving on this phone: press and hold the QR code, then share it to your payment app",
    "s3.qr.mob.p": "Press and hold the <strong>matching</strong> QR code above and save the image — one code per app. Open <b>PayMe</b> or <b>AlipayHK</b>, choose that app's scan or photo-library option, pick the code, then enter <strong class=\"qr-amount\">HK$1,300</strong>.",
    "s3.qr.fine": "These are static codes. They carry no amount, so you enter it in the payment app yourself.",
    "s3.dl.hint": "<b>App open test (POC):</b> the buttons below check whether this iframe can open a payment app. The live build uses the deep links the charity supplies.",
    "s3.dl.payme": "Test opening PayMe",
    "s3.dl.alipay": "Test opening AlipayHK",
    "s3.monthly": "Would you rather give monthly?",

    "rc.h": "Need a tax receipt? Leave your name and email.",
    "rc.lede": "We need only the name for the receipt and an email address. A receipt is issued once your total for the year of assessment reaches HK$100.",
    "rc.name": "Name (as it should appear on the receipt)",
    "rc.email": "Email",
    "rc.name.ph": "Chan Tai Man",
    "rc.consent": "I agree that the Fred Hollows Foundation may use my name and email to issue a tax receipt.",
    "rc.disclink": "Before you use this calculator or send anything, please read the <a href=\"#disclaimer\" id=\"disc-link\">disclaimer</a>.",
    "rc.submit": "Leave your details",
    "rc.poc": "POC demo: what you type stays in this test page's memory. It is not sent anywhere and not stored. In the live build a receipt system built by 2SK receives it and passes it to the charity's CRM as they direct.",
    "rc.disc.summary": "Disclaimer",
    "rc.disc.body": "This calculator gives an estimate only. It is not tax advice, and it does not replace professional advice. The estimate follows Inland Revenue Department rules for the year of assessment shown. It covers the deduction for recognised charitable donations only, and includes no other deduction, allowance or tax reduction. It does not cover profits tax, personal assessment, or joint assessment for a married couple. The amount you may deduct, and the tax you actually pay, are determined by the Inland Revenue Department. The calculator itself collects and stores nothing; the name and email you choose to give in this form are used only to issue your tax receipt.",
    "foot.legal": "* The amount you may deduct is determined by the Inland Revenue Department. The cap is 35% of assessable income or profits. Within the deductible amount, the tax saved is roughly that amount times your applicable rate, up to 17%.",

    "band.unknown": "not sure",
    "band.r0": "below HK$145,000",
    "band.r2": "HK$145,000 – 195,000",
    "band.r6": "HK$195,000 – 245,000",
    "band.r10": "HK$245,000 – 295,000",
    "band.r14": "HK$295,000 – 345,000",
    "band.r17": "HK$345,000 – 2,132,500",
    "band.r15": "HK$2,132,500 – 5,000,000",
    "band.r16": "HK$5,000,000 and above",

    "d.netlabel.once": "You actually pay",
    "d.netlabel.monthly": "You actually pay this year",
    "d.netlabel.bound": " (at least)",
    "d.cap.monthly": "{a} a month × {n} months = {total} for the year.",
    "d.cap.empty": "Enter a donation amount and this shows what you actually pay.",
    "d.cap.exact": "Worked exactly from the assessable income you entered, {inc}, through the progressive bands and the 35% cap.",
    "d.cap.unknown": "No income range chosen: from no tax payable (HK$0 saved) up to the top marginal rate, 17%.",
    "d.cap.range": "The range comes from the bottom and the top of the income range you chose.",
    "d.cap.same": "Across the income range you chose, this donation saves the same amount.",
    "d.gift.once": "Donation",
    "d.gift.monthly": "Total for the year ({n} months)",
    "d.saved.once": "Estimated tax saved",
    "d.saved.most": "Estimated tax saved (at most)",
    "d.range.sep": " to ",
    "d.rate.generic": "rate",
    "d.rate.marginal": "marginal rate",
    "d.rate.standard": "standard rate",
    "d.ratelabel.generic": "Rate used in this estimate",
    "d.ratelabel.marginal": "Marginal rate used in this estimate",
    "d.ratelabel.standard": "Standard rate used in this estimate",
    "d.assume.empty": "No donation amount entered yet.",
    "d.assume.exact": "Assessable income {inc} (the figure you entered) · progressive bands and the 35% cap applied.",
    "d.assume.unknown": "No income range chosen · from no tax payable (0%) to a top of 17%.",
    "d.assume.band": "Assessable income {band} · worked at both ends of the range.",
    "d.capline.empty": "The cap is 35% of your assessable income, taken for the whole year.",
    "d.capline.exact.capped": "The cap is 35% of your assessable income for the year: {taxed} is deductible, and the rest cannot be deducted.",
    "d.capline.exact.ok": "The cap is 35% of your assessable income for the year. You are under it, so all of the gift is deductible.",
    "d.capline.unknown": "The cap is 35% of your assessable income for the year; the cap is included.",
    "d.capline.zero": "The cap is 35% of your assessable income for the year. The gift is still deductible, but there is no tax to reduce.",
    "d.capline.band.capped": "The cap is 35% of your assessable income for the year; at the bottom of the range you chose, {d} is deductible.",
    "d.capline.band.ok": "The cap is 35% of your assessable income for the year; at the bottom of the range you chose, all of it is deductible.",
    "d.benefit.empty": "Once you enter an amount, this line shows what you pay and what you save.",
    "d.benefit.range": "You give {g}, deductible as a recognised charitable donation{cap}. Estimated tax back {lo} to {hi}, so every HK$100 you give costs you about {a} to {b}.",
    "d.benefit.capnote": " (limited by the 35% cap)",
    "d.benefit.zero": "You give {g}, deductible as a recognised charitable donation. At this income you pay no salaries tax, so the donation does not reduce your tax.",
    "d.benefit.capped": "You give {g}. The 35% cap on assessable income limits the deduction to {taxed}, and the rest cannot be deducted. Estimated tax saved {s}.",
    "d.benefit.ok": "You give {g}, all of it deductible as a recognised charitable donation. Estimated tax back {s}, so every HK$100 you give costs you about {per}.",
    "d.announce.monthly": "{a} a month, {n} months, {total} for the year.",
    "d.announce.once": "Donation {v}.",
    "d.announce.range": " Estimated tax saved {lo} to {hi}.",
    "d.announce.single": " Estimated tax saved {v}, {w} {p}.",
    "d.months.one": "1 month",
    "d.months.n": "{n} months",
    "d.dl.open": "Trying to open {app}…",
    "d.dl.notframed": "This page is not inside an iframe, so the app jump cannot be tested here. Use the Test Bench or the iframe version in the CMS.",
    "d.dl.blocked": "⚠️ Blocked by the iframe (needs allow-top-navigation-by-user-activation).",
    "d.dl.noapp": "The page is still here, so the browser or the iframe did not handle this app scheme. That is common on iOS Safari and in sandboxed iframes. A live build needs the QR code or a top-level jump.",
    "d.rv.name": "Please enter the name for the receipt.",
    "d.rv.mail": "Please enter a valid email address.",
    "d.rv.consent": "Please tick the consent box first.",
    "d.rv.ok": "Thank you. We will follow up with your receipt once the donation is in (POC: not connected to a backend yet).",
    "d.rv.done": "Received"
  }
  };

  var L = "zh-HK";
  function normLang(v){
    v = String(v || "").toLowerCase();
    return (v === "en" || v.indexOf("en-") === 0) ? "en" : "zh-HK";
  }
  function t(k, v){
    var s = I18N[L] ? I18N[L][k] : undefined;
    if (s === undefined && I18N["zh-HK"]) s = I18N["zh-HK"][k];
    if (s === undefined) return k;
    if (v) for (var p in v) s = s.split("{" + p + "}").join(v[p]);
    return s;
  }
  function monthWord(n){
    n = String(n);
    return t(n === "1" ? "d.months.one" : "d.months.n", {n: n});
  }
  /* Swap every user-facing string in place. Nothing is re-fetched and the
     frame is never re-loaded — this is the same discipline the height config
     already uses (docs/INTERFACE.md §4). The tax engine is untouched: render()
     reads the same numbers and formats them in the current table. */
  function applyLang(l){
    L = normLang(l);
    document.documentElement.setAttribute("lang", L === "en" ? "en" : "zh-Hant-HK");
    document.title = t("title");
    $$("[data-i18n]").forEach(function(e){ e.textContent = t(e.getAttribute("data-i18n")); });
    $$("[data-i18n-html]").forEach(function(e){ e.innerHTML = t(e.getAttribute("data-i18n-html")); });
    $$("[data-i18n-ph]").forEach(function(e){ e.setAttribute("placeholder", t(e.getAttribute("data-i18n-ph"))); });
    $$("[data-i18n-aria]").forEach(function(e){ e.setAttribute("aria-label", t(e.getAttribute("data-i18n-aria"))); });
    $$("[data-i18n-alt]").forEach(function(e){ e.setAttribute("alt", t(e.getAttribute("data-i18n-alt"))); });
    /* a month count is a value, not copy: one template, singular kept */
    $$("#months option").forEach(function(o){ o.textContent = monthWord(o.value); });
    $$("[data-mo]").forEach(function(b){ b.textContent = monthWord(b.getAttribute("data-mo")); });
    render();
    scheduleHeight();
  }
  function setLang(l){ if (normLang(l) === L) { applyLang(l); return; } applyLang(l); }
'''

R("i18n-tables",
  '  var st = {amount:1300, band:"r17", mode:"once", months:12, exact:0};\n'
  '  var touched = false, lastH = 0, sent = {};',
  TABLE.rstrip("\n"))

# ---- BANDS: drop the zh-only label, keep lo/hi byte-identical -------------
# The band NAMES are copy and move into I18N as band.<id>; the arithmetic, the
# 35% cap and the exact-income logic never read a label.
R("bands-labels",
  '''  var BANDS = {
    unknown:{lo:0,       hi:0,        label:"不確定"},
    r0:  {lo:0,       hi:145000,   label:"HK$145,000 以下"},
    r2:  {lo:145000,  hi:195000,   label:"HK$145,000 – 195,000"},
    r6:  {lo:195000,  hi:245000,   label:"HK$195,000 – 245,000"},
    r10: {lo:245000,  hi:295000,   label:"HK$245,000 – 295,000"},
    r14: {lo:295000,  hi:345000,   label:"HK$295,000 – 345,000"},
    r17: {lo:345000,  hi:2132500,  label:"HK$345,000 – 2,132,500"},
    r15: {lo:2132500, hi:5000000,  label:"HK$2,132,500 – 5,000,000"},
    r16: {lo:5000000, hi:10000000, label:"HK$5,000,000 以上"}''',
  '''  var BANDS = {
    unknown:{lo:0,       hi:0},
    r0:  {lo:0,       hi:145000},
    r2:  {lo:145000,  hi:195000},
    r6:  {lo:195000,  hi:245000},
    r10: {lo:245000,  hi:295000},
    r14: {lo:295000,  hi:345000},
    r17: {lo:345000,  hi:2132500},
    r15: {lo:2132500, hi:5000000},
    r16: {lo:5000000, hi:10000000}''')


# ---- head + step 1 --------------------------------------------------------
R("pocbar",
  '  <div class="pocbar"><b>POC</b><span>示範用 · 二維碼為測試碼，非真實收款碼</span></div>',
  '  <div class="pocbar"><b>POC</b><span data-i18n="poc.demo">示範用 · 二維碼為測試碼，非真實收款碼</span></div>')

R("s1-head",
  '''    <p class="eyebrow">步驟一</p>
    <h2 id="s1h">輸入兩項資料</h2>
    <p class="lede">只需一個捐款金額，以及大約的入息範圍。</p>''',
  '''    <p class="eyebrow" data-i18n="s1.eyebrow">步驟一</p>
    <h2 id="s1h" data-i18n="s1.h">輸入兩項資料</h2>
    <p class="lede" data-i18n="s1.lede">只需一個捐款金額，以及大約的入息範圍。</p>''')

R("s1-mode",
  '''      <legend>捐款方式</legend>
      <div class="seg">
        <label><input type="radio" name="mode" value="once" checked><span>單次捐款</span></label>
        <label><input type="radio" name="mode" value="monthly"><span>每月捐款</span></label>
      </div>''',
  '''      <legend data-i18n="s1.legend">捐款方式</legend>
      <div class="seg">
        <label><input type="radio" name="mode" value="once" checked><span data-i18n="s1.once">單次捐款</span></label>
        <label><input type="radio" name="mode" value="monthly"><span data-i18n="s1.monthly">每月捐款</span></label>
      </div>''')

R("s1-gift",
  '''      <label for="gift">捐款金額（HK$）</label>''',
  '''      <label for="gift" data-i18n="s1.gift">捐款金額（HK$）</label>''')

R("s1-quickamt",
  '''      <div class="chips" role="group" aria-label="快速金額">''',
  '''      <div class="chips" role="group" aria-label="快速金額" data-i18n-aria="s1.quickamt">''')

R("s1-gifthint",
  '''      <p class="hint" id="gift-hint">可直接輸入金額，或選用上方預設金額。</p>''',
  '''      <p class="hint" id="gift-hint" data-i18n="s1.gifthint">可直接輸入金額，或選用上方預設金額。</p>''')

R("s1-months-label",
  '''      <label for="months">本課稅年度內的捐款月數</label>''',
  '''      <label for="months" data-i18n="s1.months.label">本課稅年度內的捐款月數</label>''')

R("s1-quickmonths",
  '''      <div class="chips" role="group" aria-label="快速月數">''',
  '''      <div class="chips" role="group" aria-label="快速月數" data-i18n-aria="s1.quickmonths">''')

R("s1-months-hint",
  '''      <p class="hint" id="months-hint">扣稅按全年捐款總額計算；如只捐款數個月，請填寫實際月數。</p>''',
  '''      <p class="hint" id="months-hint" data-i18n="s1.months.hint">扣稅按全年捐款總額計算；如只捐款數個月，請填寫實際月數。</p>''')

R("s1-band-legend",
  '''      <legend>您全年應評稅入息大約是？（未扣除免稅額；免稅額以 HK$145,000 估算）</legend>''',
  '''      <legend data-i18n="s1.band.legend">您全年應評稅入息大約是？（未扣除免稅額；免稅額以 HK$145,000 估算）</legend>''')

R("s1-band-rows",
  '''        <label><input type="radio" name="band" value="unknown"><span>不確定 — 顯示估算範圍</span><span class="r">2% – 17%</span></label>
        <label><input type="radio" name="band" value="r0"><span>HK$145,000 以下</span><span class="r">無須繳稅</span></label>
        <label><input type="radio" name="band" value="r2"><span>HK$145,000 – 195,000</span><span class="r">約 2%</span></label>
        <label><input type="radio" name="band" value="r6"><span>HK$195,000 – 245,000</span><span class="r">約 6%</span></label>
        <label><input type="radio" name="band" value="r10"><span>HK$245,000 – 295,000</span><span class="r">約 10%</span></label>
        <label><input type="radio" name="band" value="r14"><span>HK$295,000 – 345,000</span><span class="r">約 14%</span></label>
        <label><input type="radio" name="band" value="r17" checked><span>HK$345,000 – 2,132,500</span><span class="r">約 17%</span></label>
        <label><input type="radio" name="band" value="r15"><span>HK$2,132,500 – 5,000,000</span><span class="r">標準 15%</span></label>
        <label><input type="radio" name="band" value="r16"><span>HK$5,000,000 以上</span><span class="r">標準 16%</span></label>''',
  '''        <label><input type="radio" name="band" value="unknown"><span data-i18n="s1.band.unknown">不確定 — 顯示估算範圍</span><span class="r">2% – 17%</span></label>
        <label><input type="radio" name="band" value="r0"><span data-i18n="s1.band.r0.label">HK$145,000 以下</span><span class="r" data-i18n="s1.band.r0">無須繳稅</span></label>
        <label><input type="radio" name="band" value="r2"><span>HK$145,000 – 195,000</span><span class="r" data-i18n="s1.band.r2">約 2%</span></label>
        <label><input type="radio" name="band" value="r6"><span>HK$195,000 – 245,000</span><span class="r" data-i18n="s1.band.r6">約 6%</span></label>
        <label><input type="radio" name="band" value="r10"><span>HK$245,000 – 295,000</span><span class="r" data-i18n="s1.band.r10">約 10%</span></label>
        <label><input type="radio" name="band" value="r14"><span>HK$295,000 – 345,000</span><span class="r" data-i18n="s1.band.r14">約 14%</span></label>
        <label><input type="radio" name="band" value="r17" checked><span>HK$345,000 – 2,132,500</span><span class="r" data-i18n="s1.band.r17">約 17%</span></label>
        <label><input type="radio" name="band" value="r15"><span>HK$2,132,500 – 5,000,000</span><span class="r" data-i18n="s1.band.r15">標準 15%</span></label>
        <label><input type="radio" name="band" value="r16"><span data-i18n="s1.band.r16.label">HK$5,000,000 以上</span><span class="r" data-i18n="s1.band.r16">標準 16%</span></label>''')

R("s1-band-mobile",
  '''      <select id="band-mobile" class="band-mobile" aria-label="您全年應評稅入息大約是？（未扣除免稅額）">
        <option value="unknown">不確定 — 顯示 2% – 17% 範圍</option>
        <option value="r0">HK$145,000 以下 — 無須繳稅</option>
        <option value="r2">HK$145,000 – 195,000 — 約 2%</option>
        <option value="r6">HK$195,000 – 245,000 — 約 6%</option>
        <option value="r10">HK$245,000 – 295,000 — 約 10%</option>
        <option value="r14">HK$295,000 – 345,000 — 約 14%</option>
        <option value="r17" selected>HK$345,000 – 2,132,500 — 約 17%</option>
        <option value="r15">HK$2,132,500 – 5,000,000 — 標準 15%</option>
        <option value="r16">HK$5,000,000 以上 — 標準 16%</option>
      </select>''',
  '''      <select id="band-mobile" class="band-mobile" aria-label="您全年應評稅入息大約是？（未扣除免稅額）" data-i18n-aria="s1.band.aria">
        <option value="unknown" data-i18n="s1.mob.unknown">不確定 — 顯示 2% – 17% 範圍</option>
        <option value="r0" data-i18n="s1.mob.r0">HK$145,000 以下 — 無須繳稅</option>
        <option value="r2" data-i18n="s1.mob.r2">HK$145,000 – 195,000 — 約 2%</option>
        <option value="r6" data-i18n="s1.mob.r6">HK$195,000 – 245,000 — 約 6%</option>
        <option value="r10" data-i18n="s1.mob.r10">HK$245,000 – 295,000 — 約 10%</option>
        <option value="r14" data-i18n="s1.mob.r14">HK$295,000 – 345,000 — 約 14%</option>
        <option value="r17" selected data-i18n="s1.mob.r17">HK$345,000 – 2,132,500 — 約 17%</option>
        <option value="r15" data-i18n="s1.mob.r15">HK$2,132,500 – 5,000,000 — 標準 15%</option>
        <option value="r16" data-i18n="s1.mob.r16">HK$5,000,000 以上 — 標準 16%</option>
      </select>''')

R("s1-band-note",
  '''      <p class="note">應評稅入息低於約 HK$145,000（基本免稅額）者，或無須繳付薪俸稅，該筆捐款便不能扣稅。
      應評稅入息越高，邊際稅率通常越高（最高 17%）；但應評稅入息淨額超過約 HK$2,132,500 後，稅務局會改用<b>標準稅率</b>計算
      （首 HK$500 萬 15%，其後 16%），因此最頂兩級的比率反而回落 —— 這是香港薪俸稅的設計，並非計算錯誤。</p>''',
  '''      <p class="note" data-i18n-html="s1.band.note">應評稅入息低於約 HK$145,000（基本免稅額）者，或無須繳付薪俸稅，該筆捐款便不能扣稅。
      應評稅入息越高，邊際稅率通常越高（最高 17%）；但應評稅入息淨額超過約 HK$2,132,500 後，稅務局會改用<b>標準稅率</b>計算
      （首 HK$500 萬 15%，其後 16%），因此最頂兩級的比率反而回落 —— 這是香港薪俸稅的設計，並非計算錯誤。</p>''')

R("s1-exact",
  '''      <summary>想更準確？輸入您的應評稅入息</summary>
      <div class="field" style="margin-top:6px">
        <label for="exact">全年應評稅入息（HK$，未扣除免稅額）</label>
        <div class="amt"><span class="pre">HK$</span><input id="exact" type="text" inputmode="numeric" autocomplete="off" value="" placeholder="例如 500,000" aria-describedby="exact-hint"></div>
        <p class="hint" id="exact-hint">填寫後改用單一數字，並計入累進稅級及 35% 上限。此數字只用於本頁計算，不會傳送或儲存。</p>''',
  '''      <summary data-i18n="s1.exact.summary">想更準確？輸入您的應評稅入息</summary>
      <div class="field" style="margin-top:6px">
        <label for="exact" data-i18n="s1.exact.label">全年應評稅入息（HK$，未扣除免稅額）</label>
        <div class="amt"><span class="pre">HK$</span><input id="exact" type="text" inputmode="numeric" autocomplete="off" value="" placeholder="例如 500,000" aria-describedby="exact-hint" data-i18n-ph="s1.exact.ph"></div>
        <p class="hint" id="exact-hint" data-i18n="s1.exact.hint">填寫後改用單一數字，並計入累進稅級及 35% 上限。此數字只用於本頁計算，不會傳送或儲存。</p>''')

R("s1-goto",
  '''      <a class="btn" href="#result" id="goto-result" style="width:auto;text-decoration:none">查看結果 →</a>
      <span id="upd" hidden style="font-size:var(--t-cap);color:var(--ok)">結果已更新</span>''',
  '''      <a class="btn" href="#result" id="goto-result" style="width:auto;text-decoration:none" data-i18n="s1.goto">查看結果 →</a>
      <span id="upd" hidden style="font-size:var(--t-cap);color:var(--ok)" data-i18n="s1.updated">結果已更新</span>''')

# ---- step 2 ---------------------------------------------------------------
R("s2-head",
  '''    <p class="eyebrow">步驟二</p>
    <h2 id="s2h">您的估算結果</h2>

    <p class="net-label" id="net-label">實際付出</p>''',
  '''    <p class="eyebrow" data-i18n="s2.eyebrow">步驟二</p>
    <h2 id="s2h" data-i18n="s2.h">您的估算結果</h2>

    <p class="net-label" id="net-label" data-i18n="s2.netlabel">實際付出</p>''')

R("s2-caption",
  '''    <p class="caption" id="net-caption">這是實際由您支付的金額。</p>''',
  '''    <p class="caption" id="net-caption" data-i18n="s2.caption">這是實際由您支付的金額。</p>''')

R("s2-figs",
  '''      <div><dt id="gift-label">捐款金額</dt><dd id="gift-out">HK$1,300</dd></div>
      <div><dt id="saved-label">預計節省稅款</dt><dd id="saved">−HK$221</dd></div>
      <div><dt id="rate-label">估算採用的邊際稅率</dt><dd id="rate">17%</dd></div>''',
  '''      <div><dt id="gift-label" data-i18n="s2.gift">捐款金額</dt><dd id="gift-out">HK$1,300</dd></div>
      <div><dt id="saved-label" data-i18n="s2.saved">預計節省稅款</dt><dd id="saved">−HK$221</dd></div>
      <div><dt id="rate-label" data-i18n="s2.rate">估算採用的邊際稅率</dt><dd id="rate">17%</dd></div>''')

R("s2-benefit",
  '''    <p class="benefit" id="benefit">您捐 HK$1,300，全數可作認可慈善捐款扣除；估算稅務回饋 HK$221，即每捐 HK$100，實際付出約 HK$83。</p>''',
  '''    <p class="benefit" id="benefit" data-i18n="s2.benefit">您捐 HK$1,300，全數可作認可慈善捐款扣除；估算稅務回饋 HK$221，即每捐 HK$100，實際付出約 HK$83。</p>''')

R("s2-assump",
  '''      <div><span class="k">假設：</span><p><span id="assumption">應評稅入息 HK$345,000 – 2,132,500 · 邊際稅率 17%。</span> 更改上述任何一項，估算會即時更新。此為估算，並未計算其他扣除或免稅額。</p></div>
      <div><span class="k">上限：</span><p id="cap">扣稅上限為應評稅入息的 35%（全年合計）；一般捐款金額不會觸及上限。</p></div>''',
  '''      <div><span class="k" data-i18n="s2.assump.k1">假設：</span><p><span id="assumption" data-i18n="s2.assume.def">應評稅入息 HK$345,000 – 2,132,500 · 邊際稅率 17%。</span> <span data-i18n="s2.assume.tail">更改上述任何一項，估算會即時更新。此為估算，並未計算其他扣除或免稅額。</span></p></div>
      <div><span class="k" data-i18n="s2.assump.k2">上限：</span><p id="cap" data-i18n="s2.cap.def">扣稅上限為應評稅入息的 35%（全年合計）；一般捐款金額不會觸及上限。</p></div>''')

R("s2-scope",
  '''    <p class="fine scope">本計算機只估算個人在薪俸稅下的捐款扣稅，並非稅務建議。</p>''',
  '''    <p class="fine scope" data-i18n="s2.scope">本計算機只估算個人在薪俸稅下的捐款扣稅，並非稅務建議。</p>''')

R("s2-spouse",
  '''      <summary>夫婦的扣稅額可以合併使用嗎？</summary>
      <p>若您未能用盡扣稅額（包括超過 35% 上限而未扣除的部分），配偶可在其 BIR60 報稅表內申報。但配偶本人的申報同樣以 35% 為上限，上限按其本人的入息或利潤計算；因此未用的扣稅額並非可全數轉移。</p>''',
  '''      <summary data-i18n="s2.spouse.q">夫婦的扣稅額可以合併使用嗎？</summary>
      <p data-i18n="s2.spouse.a">若您未能用盡扣稅額（包括超過 35% 上限而未扣除的部分），配偶可在其 BIR60 報稅表內申報。但配偶本人的申報同樣以 35% 為上限，上限按其本人的入息或利潤計算；因此未用的扣稅額並非可全數轉移。</p>''')

# ---- step 3 · payment -----------------------------------------------------
R("s3-head",
  '''    <p class="eyebrow">步驟三 · 付款方式</p>
    <h2 id="s3h">三種捐款方式</h2>
    <p class="lede">PayMe、AlipayHK 二維碼，以及前往護瞳行動網站的信用卡。</p>''',
  '''    <p class="eyebrow" data-i18n="s3.eyebrow">步驟三 · 付款方式</p>
    <h2 id="s3h" data-i18n="s3.h">三種捐款方式</h2>
    <p class="lede" data-i18n="s3.lede">PayMe、AlipayHK 二維碼，以及前往護瞳行動網站的信用卡。</p>''')

R("s3-badge",
  '''    <span class="badge"><span class="dot"></span>POC 測試 <span style="opacity:.6">test mode</span></span>
    <p class="note" style="margin:0 0 14px">PayMe 及 AlipayHK 以二維碼於您自己的 App 內完成；信用卡則前往護瞳行動現有的捐款頁。正式上線時會換成客戶提供的商戶碼。</p>''',
  '''    <span class="badge"><span class="dot"></span><span style="display:contents" data-i18n-html="s3.badge">POC 測試 <span style="opacity:.6">test mode</span></span></span>
    <p class="note" style="margin:0 0 14px" data-i18n="s3.note">PayMe 及 AlipayHK 以二維碼於您自己的 App 內完成；信用卡則前往護瞳行動現有的捐款頁。正式上線時會換成客戶提供的商戶碼。</p>''')

R("s3-rails",
  '''        <span class="nm">PayMe</span>
        <span class="sub"><span class="qr-desk">用手機掃描下方二維碼完成捐款</span><span class="qr-mob">長按下方二維碼儲存，並於 PayMe 內完成捐款</span></span>''',
  '''        <span class="nm">PayMe</span>
        <span class="sub"><span class="qr-desk" data-i18n="s3.payme.desk">用手機掃描下方二維碼完成捐款</span><span class="qr-mob" data-i18n="s3.payme.mob">長按下方二維碼儲存，並於 PayMe 內完成捐款</span></span>''')

R("s3-rail-alipay",
  '''        <span class="nm">AlipayHK</span>
        <span class="sub"><span class="qr-desk">用手機掃描下方二維碼完成捐款</span><span class="qr-mob">長按下方二維碼儲存，並於 AlipayHK 內完成捐款</span></span>''',
  '''        <span class="nm">AlipayHK</span>
        <span class="sub"><span class="qr-desk" data-i18n="s3.alipay.desk">用手機掃描下方二維碼完成捐款</span><span class="qr-mob" data-i18n="s3.alipay.mob">長按下方二維碼儲存，並於 AlipayHK 內完成捐款</span></span>''')

R("s3-rail-card",
  '''        <span class="nm">信用卡</span>
        <span class="sub">前往護瞳行動捐款頁，以信用卡完成捐款</span>''',
  '''        <span class="nm" data-i18n="s3.card.nm">信用卡</span>
        <span class="sub" data-i18n="s3.card.sub">前往護瞳行動捐款頁，以信用卡完成捐款</span>''')

R("s3-qr-figs",
  '''        <img id="qr-payme" src="../assets/qr-payme.svg" alt="PayMe 測試二維碼（POC，非真實收款碼）" width="150" height="150">
        <figcaption>PayMe 二維碼<span class="poc">POC 測試碼</span></figcaption>''',
  '''        <img id="qr-payme" src="../assets/qr-payme.svg" alt="PayMe 測試二維碼（POC，非真實收款碼）" width="150" height="150" data-i18n-alt="s3.qr.alt.payme">
        <figcaption><span data-i18n="s3.qr.payme">PayMe 二維碼</span><span class="poc" data-i18n="s3.qr.poc">POC 測試碼</span></figcaption>''')

R("s3-qr-figs-2",
  '''        <img id="qr-alipay" src="../assets/qr-alipay.svg" alt="AlipayHK 測試二維碼（POC，非真實收款碼）" width="150" height="150">
        <figcaption>AlipayHK 二維碼<span class="poc">POC 測試碼</span></figcaption>''',
  '''        <img id="qr-alipay" src="../assets/qr-alipay.svg" alt="AlipayHK 測試二維碼（POC，非真實收款碼）" width="150" height="150" data-i18n-alt="s3.qr.alt.alipay">
        <figcaption><span data-i18n="s3.qr.alipay">AlipayHK 二維碼</span><span class="poc" data-i18n="s3.qr.poc">POC 測試碼</span></figcaption>''')

R("s3-qr-copy",
  '''        <h3>用手機掃描二維碼捐款</h3>
        <p>請以另一部手機的相機或付款 App 掃描，然後輸入 <strong class="qr-amount">HK$1,300</strong>。</p>''',
  '''        <h3 data-i18n="s3.qr.desk.h">用手機掃描二維碼捐款</h3>
        <p data-i18n-html="s3.qr.desk.p">請以另一部手機的相機或付款 App 掃描，然後輸入 <strong class="qr-amount">HK$1,300</strong>。</p>''')

R("s3-qr-copy-mob",
  '''        <h3>以手機捐款：長按二維碼，分享至付款 App</h3>
        <p>長按上方<strong>對應的</strong>二維碼儲存圖片（每個 App 一個碼），再開啟 <b>PayMe</b> 或 <b>AlipayHK</b>，使用該 App 內的「掃描」或「相簿」功能選取該二維碼，然後輸入 <strong class="qr-amount">HK$1,300</strong>。</p>''',
  '''        <h3 data-i18n="s3.qr.mob.h">以手機捐款：長按二維碼，分享至付款 App</h3>
        <p data-i18n-html="s3.qr.mob.p">長按上方<strong>對應的</strong>二維碼儲存圖片（每個 App 一個碼），再開啟 <b>PayMe</b> 或 <b>AlipayHK</b>，使用該 App 內的「掃描」或「相簿」功能選取該二維碼，然後輸入 <strong class="qr-amount">HK$1,300</strong>。</p>''')

R("s3-qr-fine",
  '''      <p class="fine">二維碼為靜態碼，本身不包含金額，須於付款 App 內自行輸入金額。</p>''',
  '''      <p class="fine" data-i18n="s3.qr.fine">二維碼為靜態碼，本身不包含金額，須於付款 App 內自行輸入金額。</p>''')

R("s3-deeplink",
  '''      <p class="hint" style="margin:0 0 8px"><b>App 開啟測試（POC）：</b>點按下方按鈕，測試 iframe 內能否開啟付款 App。正式版將採用商戶提供的 deep link。</p>
      <div class="chips">
        <button type="button" data-deeplink="payme">測試叫起 PayMe</button>
        <button type="button" data-deeplink="alipay">測試叫起 AlipayHK</button>''',
  '''      <p class="hint" style="margin:0 0 8px" data-i18n-html="s3.dl.hint"><b>App 開啟測試（POC）：</b>點按下方按鈕，測試 iframe 內能否開啟付款 App。正式版將採用商戶提供的 deep link。</p>
      <div class="chips">
        <button type="button" data-deeplink="payme" data-i18n="s3.dl.payme">測試叫起 PayMe</button>
        <button type="button" data-deeplink="alipay" data-i18n="s3.dl.alipay">測試叫起 AlipayHK</button>''')

R("s3-monthly-link",
  '''    <p class="alt"><a href="https://www.hollows.org/zh-Hant-HK/donate/monthly-donation/" target="_top" rel="noopener">想每月捐款？</a></p>''',
  '''    <p class="alt"><a href="https://www.hollows.org/zh-Hant-HK/donate/monthly-donation/" target="_top" rel="noopener" data-i18n="s3.monthly">想每月捐款？</a></p>''')

# ---- receipt --------------------------------------------------------------
R("rc-head",
  '''    <h2 id="rch" style="font-size:1.05rem">需要扣稅收據？只需留下姓名及電郵。</h2>
    <p class="lede" style="margin-bottom:14px">我們只需收據抬頭及電郵，用以發出正式收據。課稅年度內捐款總額滿 HK$100，方可獲發正式收據。</p>''',
  '''    <h2 id="rch" style="font-size:1.05rem" data-i18n="rc.h">需要扣稅收據？只需留下姓名及電郵。</h2>
    <p class="lede" style="margin-bottom:14px" data-i18n="rc.lede">我們只需收據抬頭及電郵，用以發出正式收據。課稅年度內捐款總額滿 HK$100，方可獲發正式收據。</p>''')

R("rc-fields",
  '''          <label for="rname">姓名（收據抬頭）</label>
          <input id="rname" type="text" autocomplete="name" placeholder="陳大文" aria-describedby="rname-msg">''',
  '''          <label for="rname" data-i18n="rc.name">姓名（收據抬頭）</label>
          <input id="rname" type="text" autocomplete="name" placeholder="陳大文" aria-describedby="rname-msg" data-i18n-ph="rc.name.ph">''')

R("rc-email",
  '''          <label for="rmail">電郵</label>''',
  '''          <label for="rmail" data-i18n="rc.email">電郵</label>''')

R("rc-consent",
  '''        <label for="consent">本人同意護瞳行動使用本人的姓名及電郵，以發出扣稅收據。</label>
      </div>
      <p class="fine" style="margin:0 0 0 31px">使用本計算機及提交資料前，請先閱讀<a href="#disclaimer" id="disc-link">免責聲明</a>。</p>
      <button class="btn" type="submit" id="rsubmit">留下資料</button>''',
  '''        <label for="consent" data-i18n="rc.consent">本人同意護瞳行動使用本人的姓名及電郵，以發出扣稅收據。</label>
      </div>
      <p class="fine" style="margin:0 0 0 31px" data-i18n-html="rc.disclink">使用本計算機及提交資料前，請先閱讀<a href="#disclaimer" id="disc-link">免責聲明</a>。</p>
      <button class="btn" type="submit" id="rsubmit" data-i18n="rc.submit">留下資料</button>''')

R("rc-poc",
  '''      <p class="fine">POC 示範：資料只保留於本測試頁的記憶體，不會傳送至任何伺服器，亦不會儲存。正式版將由 2SK 建立的收據系統接收，並依客戶指示傳送至其 CRM。</p>''',
  '''      <p class="fine" data-i18n="rc.poc">POC 示範：資料只保留於本測試頁的記憶體，不會傳送至任何伺服器，亦不會儲存。正式版將由 2SK 建立的收據系統接收，並依客戶指示傳送至其 CRM。</p>''')

R("rc-disclaimer",
  '''      <summary>免責聲明</summary>
      <p>本計算機只提供估算，並非稅務建議，亦不能取代專業意見。估算依據稅務局於所示課稅年度的規定，只計入認可慈善捐款的扣稅，並未計算其他扣除、免稅額或稅務寬減；亦不涵蓋利潤稅、個人入息課稅或夫婦合併評稅。實際可扣除金額及應繳稅款以稅務局的評定為準。本計算機不會收集或儲存任何資料；您在本表格自願提供的姓名及電郵，只用作發出扣稅收據。</p>''',
  '''      <summary data-i18n="rc.disc.summary">免責聲明</summary>
      <p data-i18n="rc.disc.body">本計算機只提供估算，並非稅務建議，亦不能取代專業意見。估算依據稅務局於所示課稅年度的規定，只計入認可慈善捐款的扣稅，並未計算其他扣除、免稅額或稅務寬減；亦不涵蓋利潤稅、個人入息課稅或夫婦合併評稅。實際可扣除金額及應繳稅款以稅務局的評定為準。本計算機不會收集或儲存任何資料；您在本表格自願提供的姓名及電郵，只用作發出扣稅收據。</p>''')

R("foot-legal",
  '''  <p class="fine" style="max-width:70ch">* 實際可扣除金額以稅務局的評定為準。扣稅上限為應評稅入息或利潤的 35%；在可扣除的金額之內，所節省的稅款約為該金額乘以您的適用稅率（最高 17%）。</p>''',
  '''  <p class="fine" style="max-width:70ch" data-i18n="foot.legal">* 實際可扣除金額以稅務局的評定為準。扣稅上限為應評稅入息或利潤的 35%；在可扣除的金額之內，所節省的稅款約為該金額乘以您的適用稅率（最高 17%）。</p>''')

# ===========================================================================
# 2 · the script: config, the eight-payload dimension, render(), messages
# ===========================================================================
R("cfg-lang",
  '''    locale: qs.get("locale") || "zh-Hant-HK",
    debug: qs.get("debug") === "1"
  };''',
  '''    locale: qs.get("locale") || "zh-Hant-HK",
    lang: normLang(qs.get("lang")),
    debug: qs.get("debug") === "1"
  };
  L = cfg.lang;   /* fhf_init below must report the language, not the default */''')

R("post-lang",
  '''  function post(msg){
    if (!host) return;
    msg.source = "fhf-taxcalc"; msg.v = V;''',
  '''  function post(msg){
    if (!host) return;
    msg.source = "fhf-taxcalc"; msg.v = V; msg.lang = L;''')

R("track-lang",
  '''  function track(name, params){
    var p = params || {};
    post({type:"event", name:name, params:p});''',
  '''  function track(name, params){
    var p = params || {};
    /* `lang` is a DIMENSION (zh-HK | en), like band and state: it names which
       build the donor used, and carries no amount, income or rate. It needs a
       7th GA4 custom dimension (Event scope) or it reads as (not set). */
    p.lang = L;
    post({type:"event", name:name, params:p});''')

R("config-message",
  '''      if (d.config && d.config.reveal) {
        var el = document.getElementById(d.config.reveal);
        if (el) el.scrollIntoView({block:"start"});
      }''',
  '''      if (d.config && d.config.reveal) {
        var el = document.getElementById(d.config.reveal);
        if (el) el.scrollIntoView({block:"start"});
      }
      /* language arrives the same way height does — by postMessage, never by
         re-setting iframe.src (that is the infinite-reload trap, INTERFACE §4) */
      if (d.config && d.config.lang) setLang(d.config.lang);''')

R("gtm-init-lang",
  '''      embed_url: location.href,
      part: part || "full"
    });''',
  '''      embed_url: location.href,
      part: part || "full",
      lang: L
    });''')

R("boot-apply",
  '''  render();
  post({type:"ready", height: measure(), contract: 1});''',
  '''  applyLang(cfg.lang);   /* applies every string, then renders */
  post({type:"ready", height: measure(), contract: 1});''')

R("export-lang",
  '''  window.__fhfPoc = {version:V, state:function(){return st;}, measure:measure, post:post, track:track};''',
  '''  window.__fhfPoc = {version:V, state:function(){return st;}, measure:measure, post:post, track:track,
                     lang:function(){return L;}, setLang:setLang};''')

R("version",
  '  var V = "1.0.1";',
  '  var V = "1.1.0";')

# ---- render(): same maths, same order of operations, strings from the table
# The body is sliced out of the source at run time by its own markers, so the
# "old" side is the file's own text rather than a transcription.
RENDER_NEW = r'''  function render(){
    var b = BANDS[st.band];
    var once = digits(st.amount);
    var months = clampMonths(st.months);
    var annual = st.mode === "monthly" ? once * months : once;
    var exactInc = st.exact > 0 ? st.exact : 0;
    var isUnknown = st.band === "unknown";
    var lo = b.lo, hi = b.hi;
    var savedLow = 0, savedHigh = 0, isRange = false, capped = false, taxed = 0;

    if (annual > 0) {
      if (exactInc) {
        savedHigh = savedLow = Math.round(__fhfTax.saving(annual, exactInc));
        capped = __fhfTax.deductible(annual, exactInc) < annual;
        taxed = __fhfTax.deductible(annual, exactInc);
      } else if (isUnknown) {
        /* No band selected, so there is no floor/ceiling pair to bracket. The
           honest bounds are analytic: 0% is reachable (any income at or below
           the allowance pays no tax) and 17% is the top marginal rate, so
           gift × 17% can never be exceeded. */
        savedLow = 0;
        savedHigh = Math.round(annual * 0.17);
      } else {
        /* Band mode: compute at BOTH ends of the selected band. The saving in
           Hong Kong is a function of the income the deduction is taken from,
           so a band wide enough to cross a slice produces a genuine range —
           not one invented rate. */
        var atLo = Math.round(__fhfTax.saving(annual, lo));
        var atHi = Math.round(__fhfTax.saving(annual, hi));
        savedLow = Math.min(atLo, atHi); savedHigh = Math.max(atLo, atHi);
        /* ignore an end whose income is 0: its deductible is 0 by arithmetic,
           not because the 35% ceiling bites (that is the r0 band, below the
           allowance, where there is simply no tax to save) */
        capped = (lo > 0 && __fhfTax.deductible(annual, lo) < annual)
              || (hi > 0 && __fhfTax.deductible(annual, hi) < annual);
      }
      isRange = annual > 0 && savedLow !== savedHigh;
    }
    var netLow = annual - savedHigh, netHigh = annual - savedLow;
    var rateLow = annual > 0 ? savedLow / annual : 0;
    var rateHigh = annual > 0 ? savedHigh / annual : 0;

    /* hero */
    var netEl = $("#net");
    if (annual <= 0) { netEl.innerHTML = '<span class="cur">HK$</span>—'; }
    else if (isRange) { netEl.innerHTML = '<span class="cur">HK$</span>' + fmt(netLow) + " – " + fmt(netHigh); }
    else { netEl.innerHTML = '<span class="cur">HK$</span>' + fmt(netHigh); }
    netEl.classList.toggle("is-range", isRange || annual <= 0);

    $("#net-label").textContent = (st.mode === "monthly" ? t("d.netlabel.monthly") : t("d.netlabel.once"))
      + (!isRange && capped ? t("d.netlabel.bound") : "");

    var cap = "";
    if (st.mode === "monthly") {
      cap = t("d.cap.monthly", {a: money(once), n: months, total: money(annual)});
    }
    if (annual <= 0) {
      cap += t("d.cap.empty");
    } else if (exactInc) {
      cap += t("d.cap.exact", {inc: money(exactInc)});
    } else if (isUnknown) {
      cap += t("d.cap.unknown");
    } else if (isRange) {
      /* the caption must name the source of the range: the band's two ends */
      cap += t("d.cap.range");
    } else {
      cap += t("d.cap.same");
    }
    $("#net-caption").textContent = cap;

    $("#gift-label").textContent = st.mode === "monthly" ? t("d.gift.monthly", {n: months}) : t("d.gift.once");
    $("#gift-out").textContent = money(annual);

    /* The label may only promise what the figure is. A range is visibly a
       range ("−X to −Y") and the caption names its source, so the plain label
       is the honest one. A single figure that the 35% cap has already limited
       IS the most this donor can save, so "at most" is true there; otherwise
       the figure is exact and the plain label fits it too. */
    $("#saved-label").textContent = (!isRange && capped && annual > 0)
      ? t("d.saved.most") : t("d.saved.once");
    $("#saved").textContent = annual <= 0 ? "−HK$0"
      : isRange ? "−" + money(savedLow) + t("d.range.sep") + "−" + money(savedHigh)
      : "−" + money(savedHigh);
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

    $("#assumption").textContent = annual <= 0 ? t("d.assume.empty")
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

    /* C6 — "you give this, you get that back". Reads the numbers the engine
       already produced; it computes nothing the figures strip does not show. */
    var bEl = $("#benefit");
    if (bEl) {
      if (annual <= 0) {
        bEl.textContent = t("d.benefit.empty");
      } else if (isRange) {
        bEl.textContent = t("d.benefit.range", {
          g: money(annual),
          cap: capped ? t("d.benefit.capnote") : "",
          lo: money(savedLow), hi: money(savedHigh),
          a: "HK$" + Math.round(100*(1-rateHigh)),
          b: "HK$" + Math.round(100*(1-rateLow))
        });
      } else if (savedHigh === 0) {
        bEl.textContent = t("d.benefit.zero", {g: money(annual)});
      } else if (capped) {
        bEl.textContent = t("d.benefit.capped", {g: money(annual), taxed: money(taxed), s: money(savedHigh)});
      } else {
        bEl.textContent = t("d.benefit.ok", {g: money(annual), s: money(savedHigh),
          per: "HK$" + Math.round(100*(1-rateHigh))});
      }
    }

    $$(".qr-amount").forEach(function(e){ e.textContent = money(annual); });

    /* announce once, settled */
    clearTimeout(annT);
    annT = setTimeout(function(){
      $("#announce").textContent =
        (st.mode === "monthly"
          ? t("d.announce.monthly", {a: money(once), n: months, total: money(annual)})
          : t("d.announce.once", {v: money(annual)}))
        + (annual <= 0 ? ""
          : isRange ? t("d.announce.range", {lo: money(savedLow), hi: money(savedHigh)})
          : t("d.announce.single", {v: money(savedHigh), w: t("d.rate." + rateKey), p: pct(rateHigh)}));
    }, 600);

    if (touched) { $("#upd").hidden = false; }
    scheduleHeight();
  }
'''


def swap_render(src: str) -> tuple[str, bool]:
    """Slice render() out between its own markers and swap the body."""
    start = src.find("\n  function render(){")
    end_marker = "\n  /* ---------- events ---------- */"
    end = src.find(end_marker, start)
    if start < 0 or end < 0:
        return src, False
    return src[:start] + "\n" + RENDER_NEW.rstrip("\n") + src[end:], True

R("engine-comment",
  '''    /* Top marginal rate at this income — decides which word the result row may
       use (邊際 / 標準 / generic 適用). It never produces a figure. */''',
  '''    /* Top marginal rate at this income — decides which of the three rate words
       the result row may use (marginal / standard / generic). It never produces
       a figure, and it holds no locale string: the words live in I18N. */''')

# ---- deeplink + receipt messages ------------------------------------------
R("dl-messages",
  '''      msg.textContent = "已嘗試開啟 " + (rail === "payme" ? "PayMe" : "AlipayHK") + "…";

      if (window.top === window) {
        msg.textContent = "本頁未嵌入 iframe，因此無法測試 App 跳轉 —— 請在 Test Bench 或 CMS 內的 iframe 版本測試。";''',
  '''      msg.textContent = t("d.dl.open", {app: rail === "payme" ? "PayMe" : "AlipayHK"});

      if (window.top === window) {
        msg.textContent = t("d.dl.notframed");''')

R("dl-blocked",
  '''          msg.textContent = "⚠️ 被 iframe 阻止（需要 allow-top-navigation-by-user-activation）。";''',
  '''          msg.textContent = t("d.dl.blocked");''')

R("dl-noapp",
  '''        msg.textContent = "頁面仍然停留於此 —— 表示瀏覽器或 iframe 未處理此 App scheme（iOS Safari 及沙盒 iframe 常見）。正式版需要二維碼或頂層跳轉。";''',
  '''        msg.textContent = t("d.dl.noapp");''')

R("rv-messages",
  '''    if (name.length < 2) { $("#rname-msg").textContent = "請輸入收據抬頭姓名。"; $("#rname-msg").hidden = false; ok = false; }
    if (!/^[^\\s@]+@[^\\s@]+\\.[^\\s@]{2,}$/.test(mail)) { $("#rmail-msg").textContent = "請輸入有效電郵。"; $("#rmail-msg").hidden = false; ok = false; }
    if (!$("#consent").checked) { $("#capture-status").textContent = "請先勾選同意。"; $("#capture-status").className = "msg"; $("#capture-status").hidden = false; return; }''',
  '''    if (name.length < 2) { $("#rname-msg").textContent = t("d.rv.name"); $("#rname-msg").hidden = false; ok = false; }
    if (!/^[^\\s@]+@[^\\s@]+\\.[^\\s@]{2,}$/.test(mail)) { $("#rmail-msg").textContent = t("d.rv.mail"); $("#rmail-msg").hidden = false; ok = false; }
    if (!$("#consent").checked) { $("#capture-status").textContent = t("d.rv.consent"); $("#capture-status").className = "msg"; $("#capture-status").hidden = false; return; }''')

R("rv-success",
  '''    s.textContent = "多謝您。我們會於您捐款後跟進發出收據（POC：尚未接駁後端）。";''',
  '''    s.textContent = t("d.rv.ok");''')

R("rv-done",
  '''    $("#rsubmit").textContent = "已收到";''',
  '''    $("#rsubmit").textContent = t("d.rv.done");''')

# the consent-line link is re-created by applyLang(), so bind by delegation
R("disc-link-binding",
  '''  /* the consent-line link must OPEN the collapsed text, not just jump to it */
  var dl_ = $("#disc-link");
  $$("details.q").forEach(function(d){
    d.addEventListener("toggle", function(){ scheduleHeight(); });
  });
  if (dl_) dl_.addEventListener("click", function () {
    var d = $("#disclaimer"); if (d) { d.open = true; scheduleHeight(); }
  });''',
  '''  $$("details.q").forEach(function(d){
    d.addEventListener("toggle", function(){ scheduleHeight(); });
  });
  /* The consent-line link must OPEN the collapsed text, not just jump to it.
     Bound on the document because applyLang() re-creates that paragraph when
     the language changes — a listener on the old node would be orphaned. */
  document.addEventListener("click", function (e) {
    var el = e.target;
    while (el && el !== document) {
      if (el.id === "disc-link") {
        var d = $("#disclaimer"); if (d) { d.open = true; scheduleHeight(); }
        return;
      }
      el = el.parentNode;
    }
  });''')


def main():
    dry = "--dry" in sys.argv
    src = SRC.read_text(encoding="utf-8")
    out = src
    applied, failed = [], []

    out, render_ok = swap_render(out)
    if render_ok:
        applied.append(("render-body", 1))
    else:
        failed.append(("render-body", 0))

    for name, old, new in P:
        n = out.count(old)
        if n != 1:
            failed.append((name, n))
            continue
        if old != new:
            out = out.replace(old, new, 1)
            applied.append((name, n))
        else:
            applied.append((name, 0))      # explicit no-op, recorded
    for name, n in failed:
        print(f"MISS  {name:<22} occurrences={n}  (expected exactly 1)")
    if failed:
        print(f"\n{len(failed)} replacement(s) did not match — nothing written.")
        return 1
    print(f"{len(applied)} replacements applied, 0 failed\n")
    print(f"{'#':>3}  {'replacement':<22} occurrences")
    for i, (name, n) in enumerate(applied, 1):
        print(f"{i:>3}  {name:<22} {'exactly 1' if n else 'no-op (asserted unique)'}")
    if dry:
        print("\n--dry: file not written")
        return 0
    OUT.write_text(out, encoding="utf-8")
    print(f"\nwrote {OUT.relative_to(ROOT)}  ({len(out.encode('utf-8')):,} bytes, was {len(src.encode('utf-8')):,})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
