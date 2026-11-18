# Copy changes — Direction B (product-grade fintech)

Baseline: `index.orig.html` (byte-identical to the delivered `embed/index.html`). Result: `index.html`.

- String table: **142 → 133 keys**, identical key sets in both languages (the parity test asserts it, and that English carries no CJK).
- **112 keys touched**: 131 rewrites across 75 keys, 14 keys added, 23 keys removed — the same edits in both tables.
- Where a column reads *(unchanged)*, that language already carried the shorter form (zh `約 2%` is the compact notation already; en moved `About 2%` → `~2%`).


## Shared

| key | zh-HK before | zh-HK after | en before | en after |
|---|---|---|---|---|
| `title` | 慈善捐款扣稅計算機 | 捐款扣稅計算機 | Donation tax calculator | *(unchanged)* |
| `foot.legal` | * 實際可扣除金額以稅務局的評定為準。扣稅上限為應評稅入息或利潤的 35%；在可扣除的金額之內，所節省的稅款約為該金額乘以您的適用稅率（最高 17%）。 | * 實際可扣除金額以稅務局評定為準。上限為應評稅入息或利潤的 35%；在可扣除金額之內，節省的稅款約為該金額乘以您的適用稅率（最高 17%）。 | * The amount you may deduct is determined by the Inland Revenue Department. The cap is 35% of assessable income or profits. Within the deductible amount, the tax saved is roughly that amount times your applicable rate, up to 17%. | *(unchanged)* |

## Step 1 — order pad (calc / input)

| key | zh-HK before | zh-HK after | en before | en after |
|---|---|---|---|---|
| `s1.h` | 輸入兩項資料 | 捐款扣稅估算 | Enter two things | Donation tax estimate |
| `s1.once` | 單次捐款 | 單次 | One-off | *(unchanged)* |
| `s1.monthly` | 每月捐款 | 每月 | Monthly | *(unchanged)* |
| `s1.months.label` | 本課稅年度內的捐款月數 | 本年度捐款月數 | Months you give in this year of assessment | Months you give this year |
| `s1.months.hint` | 扣稅按全年捐款總額計算；如只捐款數個月，請填寫實際月數。 | 按全年總額計算；只捐數個月，就填實際月數。 | The deduction uses your total for the year, so if you give for only some months, enter the months you actually give. | The deduction uses your total for the year, so enter the months you actually give. |
| `s1.band.legend` | 您全年應評稅入息大約是？（未扣除免稅額；免稅額以 HK$145,000 估算） | 應評稅入息（HK$，未扣免稅額） | Roughly what is your assessable income for the year? (Before allowances; the allowance is estimated at HK$145,000) | Assessable income, before allowances (HK$) |
| `s1.band.unknown` | 不確定 — 顯示估算範圍 | 不確定 — 顯示 2%–17% 範圍 | Not sure — show me a range | Not sure — show a 2%–17% range |
| `s1.band.r0.label` | HK$145,000 以下 | 145k 以下 | Below HK$145,000 | under 145k |
| `s1.band.r0` | 無須繳稅 | 0% | No tax payable | 0% |
| `s1.band.r15` | 標準 15% | 15% | Standard 15% | 15% |
| `s1.band.r16.label` | HK$5,000,000 以上 | 5M 以上 | HK$5,000,000 and above | 5M and up |
| `s1.band.r16` | 標準 16% | 16% | Standard 16% | 16% |
| `s1.band.note` | 應評稅入息低於約 HK$145,000（基本免稅額）者，或無須繳付薪俸稅，該筆捐款便不能扣稅。    應評稅入息越高，邊際稅率通常越高（最高 17%）；但應評稅入息淨額超過約 HK$2,132,500 後，稅務局會改用<b>標準稅率</b>計算    （首 HK$500 萬 15%，其後 16%），因此最頂兩級的比率反而回落 —— 這是香港薪俸稅的設計，並非計算錯誤。 | 低於 HK$145,000（基本免稅額）者無須繳稅，捐款不能扣稅。超過約 HK$2,132,500 後改用<b>標準稅率</b>（首 HK$500 萬 15%，其後 16%），所以最頂兩級回落 —— 稅例如此，不是計算錯誤。 | If your assessable income is below about HK$145,000 (the basic allowance), or you pay no salaries tax, this donation saves you nothing.    The higher your assessable income, the higher your marginal rate usually is, up to 17%. Above about HK$2,132,500 of net assessable income the Inland Revenue Department charges the <b>standard rate</b> instead    — 15% on the first HK$5 million, 16% above it — so the top two rungs go down, not up. That is how Hong Kong salaries tax is designed, not a calculation error. | Below HK$145,000 (the basic allowance) there is no salaries tax, so nothing can be deducted. Above about HK$2,132,500 the IRD charges the <b>standard rate</b> instead — 15% on the first HK$5 million, 16% above — so the top two rungs fall. That is how the tax is designed, not a calculation error. |
| `s1.exact.summary` | 想更準確？輸入您的應評稅入息 | 有準確數字？輸入應評稅入息 | Want a closer figure? Enter your assessable income | Have the exact figure? Enter your assessable income |
| `s1.exact.label` | 全年應評稅入息（HK$，未扣除免稅額） | 全年應評稅入息（HK$，未扣免稅額） | Assessable income for the year (HK$, before allowances) | *(unchanged)* |
| `s1.exact.ph` | 例如 500,000 | 500,000 | e.g. 500,000 | 500,000 |
| `s1.exact.hint` | 填寫後改用單一數字，並計入累進稅級及 35% 上限。此數字只用於本頁計算，不會傳送或儲存。 | 改用單一數字，計入累進稅級及 35% 上限。不會傳送或儲存。 | A figure here gives you one number, worked through the progressive bands and the 35% cap. It is used for this page only — never sent, never stored. | One figure, worked through the progressive bands and the 35% cap. Never sent, never stored. |
| `s1.goto` | 查看結果 → | 查看結果 | See the result → | See the result |
| `s1.updated` | 結果已更新 | 已更新 | Result updated | Updated |
| `d.cap.monthly` | 每月 {a} × {n} 個月 = 全年合計 {total}。 | 每月 {a} × {n} 個月 = {total}。 | {a} a month × {n} months = {total} for the year. | {a} a month × {n} months = {total}. |
| `d.cap.empty` | 輸入捐款金額後，這裡會顯示您實際付出多少。 | 輸入金額後即見實際付出。 | Enter a donation amount and this shows what you actually pay. | Enter an amount to see what you pay. |
| `d.cap.exact` | 按您輸入的應評稅入息 {inc} 精確計算，已計入累進稅級及 35% 上限。 | 按應評稅入息 {inc} 精算。 | Worked exactly from the assessable income you entered, {inc}, through the progressive bands and the 35% cap. | Worked exactly from your income, {inc}. |
| `d.cap.unknown` | 未指定入息範圍：下限為無須繳稅（節省 HK$0），上限為最高邊際稅率 17%。 | 未選入息：由無須繳稅至 17%。 | No income range chosen: from no tax payable (HK$0 saved) up to the top marginal rate, 17%. | No income range: from no tax payable up to 17%. |
| `d.cap.range` | 範圍來自所選入息範圍的下限與上限。 | 來自所選範圍的上下限。 | The range comes from the bottom and the top of the income range you chose. | From the two ends of the band you chose. |
| `d.cap.same` | 在所選入息範圍內，這筆捐款節省的稅款相同。 | 所選範圍內，節省金額相同。 | Across the income range you chose, this donation saves the same amount. | The same saving across the band you chose. |
| `d.gift.monthly` | 全年捐款總額（{n} 個月） | 全年總額（{n} 個月） | Total for the year ({n} months) | *(unchanged)* |
| `d.announce.monthly` | 每月 {a}，共 {n} 個月，全年合計 {total}。 | 每月 {a}，{n} 個月，全年 {total}。 | {a} a month, {n} months, {total} for the year. | *(unchanged)* |
| `d.announce.range` |  預計節省稅款由 {lo} 至 {hi}。 |  預計節省稅款 {lo} 至 {hi}。 |  Estimated tax saved {lo} to {hi}. | *(unchanged)* |
| `s1.band.r2` | 約 2% | *(unchanged)* | About 2% | ~2% |
| `s1.band.r6` | 約 6% | *(unchanged)* | About 6% | ~6% |
| `s1.band.r10` | 約 10% | *(unchanged)* | About 10% | ~10% |
| `s1.band.r14` | 約 14% | *(unchanged)* | About 14% | ~14% |
| `s1.band.r17` | 約 17% | *(unchanged)* | About 17% | ~17% |
| `s1.band.std` | *(new key)* |  | | |
| `s1.band.r2.label` | *(new key)* |  | | |
| `s1.band.r6.label` | *(new key)* |  | | |
| `s1.band.r10.label` | *(new key)* |  | | |
| `s1.band.r14.label` | *(new key)* |  | | |
| `s1.band.r17.label` | *(new key)* |  | | |
| `s1.band.r15.label` | *(new key)* |  | | |
| `s2.cap` | *(new key)* |  | | |

## Step 2 — estimate panel (result)

| key | zh-HK before | zh-HK after | en before | en after |
|---|---|---|---|---|
| `s2.h` | 您的估算結果 | 您的估算 | Your estimate | *(unchanged)* |
| `s2.benefit` | 您捐 HK$1,300，全數可作認可慈善捐款扣除；估算稅務回饋 HK$221，即每捐 HK$100，實際付出約 HK$83。 | 每捐 HK$100，實際付出約 HK$83。 | You give HK$1,300, all of it deductible as a recognised charitable donation. Estimated tax back HK$221, so every HK$100 you give costs you about HK$83. | Every HK$100 you give costs you about HK$83. |
| `s2.assume.tail` | 更改上述任何一項，估算會即時更新。此為估算，並未計算其他扣除或免稅額。 | 改動任何一項，估算即時更新。並未計算其他扣除或免稅額。 | Change either one and the estimate updates. Other deductions and allowances are not included. | Change any of it and the estimate updates. Other deductions and allowances are not included. |
| `s2.scope` | 本計算機只估算個人在薪俸稅下的捐款扣稅，並非稅務建議。 | 只估算個人在薪俸稅下的捐款扣稅，並非稅務建議。 | This estimates the donation deduction for one person under salaries tax only. It is not tax advice. | Estimates the donation deduction for one person under salaries tax only. Not tax advice. |
| `s2.spouse.q` | 夫婦的扣稅額可以合併使用嗎？ | 夫婦可以合併使用扣稅額嗎？ | Can a couple combine their deduction? | Can a couple combine the deduction? |
| `s2.spouse.a` | 若您未能用盡扣稅額（包括超過 35% 上限而未扣除的部分），配偶可在其 BIR60 報稅表內申報。但配偶本人的申報同樣以 35% 為上限，上限按其本人的入息或利潤計算；因此未用的扣稅額並非可全數轉移。 | 若您未能用盡扣稅額，配偶可在其 BIR60 報稅表內申報。但配偶的申報同樣以 35% 為上限，上限按其本人入息或利潤計算；未用的扣稅額不能全數轉移。 | If you cannot use all of your deduction — including the part above the 35% cap — your spouse may claim it on their own BIR60. Their claim is still capped at 35% of their own income or profits, so an unused deduction cannot be passed across in full. | If you cannot use all of your deduction, your spouse may claim it on their own BIR60. Their claim is still capped at 35% of their own income or profits, so an unused deduction cannot be passed across in full. |
| `d.saved.most` | 預計節省稅款（最多） | 預計節省稅款（上限） | Estimated tax saved (at most) | *(unchanged)* |
| `d.assume.exact` | 應評稅入息 {inc}（您輸入）· 已計入累進稅級及 35% 上限。 | 應評稅入息 {inc}，已計入累進稅級及 35% 上限。 | Assessable income {inc} (the figure you entered) · progressive bands and the 35% cap applied. | Assessable income {inc}, through the progressive bands and the 35% cap. |
| `d.assume.unknown` | 應評稅入息範圍未指定 · 由無須繳稅（0%）至最高 17%。 | 未指定入息範圍，由無須繳稅至 17%。 | No income range chosen · from no tax payable (0%) to a top of 17%. | No income range chosen: from no tax payable up to 17%. |
| `d.assume.band` | 應評稅入息 {band} · 按範圍下限與上限分別計算。 | 應評稅入息 {band}，按範圍上下限計算。 | Assessable income {band} · worked at both ends of the range. | Assessable income {band}, worked at both ends of the range. |
| `d.capline.empty` | 扣稅上限為應評稅入息的 35%（全年合計）。 | 扣稅上限：應評稅入息的 35%（全年合計）。 | The cap is 35% of your assessable income, taken for the whole year. | Cap: 35% of assessable income for the year. |
| `d.capline.exact.capped` | 扣稅上限為應評稅入息的 35%（全年合計）：可扣除 {taxed}，超出部分不能扣除。 | 上限為應評稅入息的 35%：可扣除 {taxed}，超出部分不能扣除。 | The cap is 35% of your assessable income for the year: {taxed} is deductible, and the rest cannot be deducted. | Cap 35% of assessable income: {taxed} deductible, the rest is not. |
| `d.capline.exact.ok` | 扣稅上限為應評稅入息的 35%（全年合計）；未觸及上限，全數可扣除。 | 上限為應評稅入息的 35%；未觸及上限，全數可扣除。 | The cap is 35% of your assessable income for the year. You are under it, so all of the gift is deductible. | Cap 35% of assessable income; under it, so all of the gift is deductible. |
| `d.capline.unknown` | 扣稅上限為應評稅入息的 35%（全年合計）；上限已計入。 | 上限為應評稅入息的 35%，已計入。 | The cap is 35% of your assessable income for the year; the cap is included. | Cap 35% of assessable income, included. |
| `d.capline.zero` | 扣稅上限為應評稅入息的 35%（全年合計）；捐款仍可扣除，但沒有應繳稅款可減少。 | 上限為應評稅入息的 35%；無應繳稅款可減，捐款仍屬可扣除。 | The cap is 35% of your assessable income for the year. The gift is still deductible, but there is no tax to reduce. | Cap 35% of assessable income; no tax to reduce, the gift is still deductible. |
| `d.capline.band.capped` | 扣稅上限為應評稅入息的 35%（全年合計）；所選範圍下限可扣除 {d}。 | 上限為應評稅入息的 35%；範圍下限可扣除 {d}。 | The cap is 35% of your assessable income for the year; at the bottom of the range you chose, {d} is deductible. | Cap 35% of assessable income; {d} deductible at the bottom of the band. |
| `d.capline.band.ok` | 扣稅上限為應評稅入息的 35%（全年合計）；所選範圍下限全數可扣除。 | 上限為應評稅入息的 35%；範圍下限全數可扣除。 | The cap is 35% of your assessable income for the year; at the bottom of the range you chose, all of it is deductible. | Cap 35% of assessable income; all of it deductible at the bottom of the band. |
| `d.benefit.empty` | 輸入捐款金額後，這裡會顯示您實際付出多少、節省多少稅款。 | 輸入金額後，這裡顯示實際付出與節省稅款。 | Once you enter an amount, this line shows what you pay and what you save. | Enter an amount to see what you pay and save. |
| `d.benefit.range` | 您捐 {g}，可作認可慈善捐款扣除{cap}；預計稅務回饋 {lo} 至 {hi}，即每捐 HK$100，實際付出約 {a} 至 {b}。 | 每捐 HK$100，實際付出約 {a} 至 {b}{cap}。 | You give {g}, deductible as a recognised charitable donation{cap}. Estimated tax back {lo} to {hi}, so every HK$100 you give costs you about {a} to {b}. | Every HK$100 you give costs about {a} to {b}{cap}. |
| `d.benefit.capnote` | （受 35% 上限限制） | （已受 35% 上限限制） |  (limited by the 35% cap) | *(unchanged)* |
| `d.benefit.zero` | 您捐 {g}，可作認可慈善捐款扣除。以您的入息水平估算，無須繳付薪俸稅，因此這筆捐款不會減少稅款。 | 此入息水平無須繳稅，捐款不減稅款。 | You give {g}, deductible as a recognised charitable donation. At this income you pay no salaries tax, so the donation does not reduce your tax. | At this income you pay no salaries tax, so the gift does not reduce it. |
| `d.benefit.capped` | 您捐 {g}。可扣除金額受應評稅入息 35% 上限所限，為 {taxed}，超出部分不能扣除；預計節省稅款 {s}。 | 受 35% 上限所限，可扣除 {taxed}，超出部分不能扣除。 | You give {g}. The 35% cap on assessable income limits the deduction to {taxed}, and the rest cannot be deducted. Estimated tax saved {s}. | The 35% cap limits the deduction to {taxed}; the rest is not deductible. |
| `d.benefit.ok` | 您捐 {g}，全數可作認可慈善捐款扣除；預計稅務回饋 {s}，即每捐 HK$100，實際付出約 {per}。 | 全數可作認可慈善捐款扣除；每捐 HK$100，實際付出約 {per}。 | You give {g}, all of it deductible as a recognised charitable donation. Estimated tax back {s}, so every HK$100 you give costs you about {per}. | All of it deductible as a recognised charitable donation. Every HK$100 you give costs about {per}. |
| `d.dl.notframed` | 本頁未嵌入 iframe，因此無法測試 App 跳轉 —— 請在 Test Bench 或 CMS 內的 iframe 版本測試。 | 本頁未嵌入 iframe，無法測試 App 跳轉。 | This page is not inside an iframe, so the app jump cannot be tested here. Use the Test Bench or the iframe version in the CMS. | This page is not inside an iframe, so the app jump cannot be tested. |
| `d.dl.blocked` | ⚠️ 被 iframe 阻止（需要 allow-top-navigation-by-user-activation）。 | 被 iframe 阻止（需要 allow-top-navigation-by-user-activation）。 | ⚠️ Blocked by the iframe (needs allow-top-navigation-by-user-activation). | Blocked by the iframe (needs allow-top-navigation-by-user-activation). |
| `d.dl.noapp` | 頁面仍然停留於此 —— 表示瀏覽器或 iframe 未處理此 App scheme（iOS Safari 及沙盒 iframe 常見）。正式版需要二維碼或頂層跳轉。 | 頁面仍停留於此，表示瀏覽器或 iframe 未處理此 App scheme。 | The page is still here, so the browser or the iframe did not handle this app scheme. That is common on iOS Safari and in sandboxed iframes. A live build needs the QR code or a top-level jump. | The page is still here, so the browser or iframe did not handle this app scheme. |
| `s2.assume.q` | *(new key)* |  | | |
| `s2.facts.q` | *(new key)* |  | | |
| `s2.facts.s88` | *(new key)* |  | | |
| `s2.facts.nondeduct` | *(new key)* |  | | |
| `s2.facts.keep` | *(new key)* |  | | |
| `s2.facts.ya` | *(new key)* |  | | |

## Step 3 — payment

| key | zh-HK before | zh-HK after | en before | en after |
|---|---|---|---|---|
| `s3.h` | 三種捐款方式 | 三種付款方式 | Three ways to give | *(unchanged)* |
| `s3.payme.sub` | 於護瞳行動捐款頁以 PayMe 完成捐款 | 護瞳行動捐款頁 | Give by PayMe on the Foundation's donation page | The Foundation's donation page |
| `s3.alipay.sub` | 於護瞳行動捐款頁以 AlipayHK 完成捐款 | 護瞳行動捐款頁 | Give by AlipayHK on the Foundation's donation page | The Foundation's donation page |
| `s3.card.sub` | 前往護瞳行動捐款頁，以信用卡完成捐款 | 護瞳行動捐款頁 | Go to the Foundation's donation page and give by card | The Foundation's donation page |

## Receipt form

| key | zh-HK before | zh-HK after | en before | en after |
|---|---|---|---|---|
| `rc.h` | 需要扣稅收據？留下姓名、電郵及付款參考編號。 | 申請扣稅收據 | Need a tax receipt? Leave your name, email and payment reference. | Request a tax receipt |
| `rc.lede` | 我們需要收據抬頭、電郵，以及付款交易編號，用以核對您的捐款並發出正式收據。課稅年度內捐款總額滿 HK$100，方可獲發正式收據。 | 用於核對捐款、發出正式收據。全年捐款總額滿 HK$100 方可獲發。 | We need the name for the receipt, an email address, and the transaction reference from your payment, so we can match your gift before issuing the receipt. A receipt is issued once your total for the year of assessment reaches HK$100. | Used to match your gift and issue the receipt. A receipt is issued once your total for the year reaches HK$100. |
| `rc.ref.hint` | 請填寫付款 App 交易紀錄或信用卡收據上的交易編號；我們憑此核對您的捐款，再發出正式收據。 | 付款 App 的交易紀錄，或信用卡收據上的交易編號。 | The transaction ID shown in your payment app, or on your card receipt. We use it to match your donation before issuing the receipt. | The transaction ID in your payment app, or on your card receipt. |
| `rc.consent` | 本人同意護瞳行動使用上述資料核對本人的捐款，並發出扣稅收據。 | 本人同意護瞳行動使用上述資料核對捐款並發出扣稅收據。 | I agree that the Fred Hollows Foundation may use the details above to match my donation and issue a tax receipt. | I agree that the Fred Hollows Foundation may use these details to match my donation and issue a tax receipt. |
| `rc.disc.summary` | 免責聲明 | 免責聲明（提交前請先閱讀） | Disclaimer | Disclaimer (please read before you submit) |
| `d.ratelabel.generic` | 估算採用的稅率 | 稅率 | Rate used in this estimate | Rate |
| `d.ratelabel.marginal` | 估算採用的邊際稅率 | 邊際稅率 | Marginal rate used in this estimate | Marginal rate |
| `d.ratelabel.standard` | 估算採用的標準稅率 | 標準稅率 | Standard rate used in this estimate | Standard rate |
| `d.rv.ok` | 多謝您。我們會先核對您的付款，核對後發出扣稅收據。 | 多謝您。我們會先核對付款，核對後發出扣稅收據。 | Thank you. We will match your payment first, then issue the tax receipt. | *(unchanged)* |
| `rc.name` | 姓名（收據抬頭） | *(unchanged)* | Name (as it should appear on the receipt) | Name on the receipt |

## Keys added

| key | zh-HK | en |
|---|---|---|
| `s1.band.std` | 標準稅率（取代累進稅率） | Standard rate (replaces the progressive rates) |
| `s1.band.r2.label` | 145–195k | 145–195k |
| `s1.band.r6.label` | 195–245k | 195–245k |
| `s1.band.r10.label` | 245–295k | 245–295k |
| `s1.band.r14.label` | 295–345k | 295–345k |
| `s1.band.r17.label` | 345k–2.1M | 345k–2.1M |
| `s1.band.r15.label` | 2.1M–5M | 2.1M–5M |
| `s2.assume.q` | 計算假設 | What this assumes |
| `s2.cap` | 扣稅上限：應評稅入息的 35%（全年合計）。 | Cap: 35% of assessable income for the year. |
| `s2.facts.q` | 扣稅須知 | What counts |
| `s2.facts.s88` | 捐款須捐予《稅務條例》第 88 條獲認可的慈善機構，方可扣稅。 | The gift must go to a charity approved under section 88 of the Inland Revenue Ordinance. |
| `s2.facts.nondeduct` | 不獲扣除的例子：購買貨品、服務、抽獎券或拍賣品的付款，以及捐予非認可機構的款項。 | Not deductible: payment for goods, services, raffle or auction tickets, and gifts to bodies that are not approved. |
| `s2.facts.keep` | 收據及相關紀錄須保留六年。 | Keep receipts and records for six years. |
| `s2.facts.ya` | 課稅年度於每年 3 月 31 日結束。 | The year of assessment ends on 31 March. |

## Keys removed

All of them were restatements of something the block already said, never a fact.

| key | zh-HK | en |
|---|---|---|
| `s1.eyebrow` | 步驟一 | Step 1 |
| `s1.lede` | 只需一個捐款金額，以及大約的入息範圍。 | Just the amount you are giving, and roughly what you earn. |
| `s1.gifthint` | 可直接輸入金額，或選用上方預設金額。 | Type an amount, or pick one above. |
| `s1.band.aria` | 您全年應評稅入息大約是？（未扣除免稅額） | Roughly what is your assessable income for the year? (Before allowances) |
| `s1.mob.unknown` | 不確定 — 顯示 2% – 17% 範圍 | Not sure — show a 2% – 17% range |
| `s1.mob.r0` | HK$145,000 以下 — 無須繳稅 | Below HK$145,000 — no tax payable |
| `s1.mob.r2` | HK$145,000 – 195,000 — 約 2% | HK$145,000 – 195,000 — about 2% |
| `s1.mob.r6` | HK$195,000 – 245,000 — 約 6% | HK$195,000 – 245,000 — about 6% |
| `s1.mob.r10` | HK$245,000 – 295,000 — 約 10% | HK$245,000 – 295,000 — about 10% |
| `s1.mob.r14` | HK$295,000 – 345,000 — 約 14% | HK$295,000 – 345,000 — about 14% |
| `s1.mob.r17` | HK$345,000 – 2,132,500 — 約 17% | HK$345,000 – 2,132,500 — about 17% |
| `s1.mob.r15` | HK$2,132,500 – 5,000,000 — 標準 15% | HK$2,132,500 – 5,000,000 — standard 15% |
| `s1.mob.r16` | HK$5,000,000 以上 — 標準 16% | HK$5,000,000 and above — standard 16% |
| `s2.eyebrow` | 步驟二 | Step 2 |
| `s2.caption` | 這是實際由您支付的金額。 | This is the amount you actually pay. |
| `s2.rate` | 估算採用的邊際稅率 | Marginal rate used |
| `s2.assump.k1` | 假設： | Assumptions: |
| `s2.assume.def` | 應評稅入息 HK$345,000 – 2,132,500 · 邊際稅率 17%。 | Assessable income HK$345,000 – 2,132,500 · marginal rate 17%. |
| `s2.assump.k2` | 上限： | Cap: |
| `s2.cap.def` | 扣稅上限為應評稅入息的 35%（全年合計）；一般捐款金額不會觸及上限。 | The cap is 35% of your assessable income, taken for the year. An ordinary donation does not reach it. |
| `s3.eyebrow` | 步驟三 · 付款方式 | Step 3 · Payment |
| `s3.lede` | PayMe、AlipayHK 及信用卡，全部於護瞳行動的捐款頁完成。 | PayMe, AlipayHK or a credit card — all completed on the Foundation's donation page. |
| `rc.disclink` | 使用本計算機及提交資料前，請先閱讀<a href="#disclaimer" id="disc-link">免責聲明</a>。 | Before you use this calculator or send anything, please read the <a href="#disclaimer" id="disc-link">disclaimer</a>. |
