#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Apply the Denise (14 Nov 2026) revision to embed/index.html.

Every entry is an exact, single-occurrence string replacement so the change can
be re-verified: the script asserts each `old` occurs exactly `n` times before it
replaces it, and exits non-zero otherwise. The same list is dumped to
/tmp/fhf-change-list.json, which the change document is generated from — the
before -> after table in the client notes is therefore not hand-transcribed.

Tags: C1 register · C2 disclaimer · C4 mobile · C6 benefit line · C7 IRD terms
MATH: none. Nothing here touches BANDS, CAP_FLAG_FROM, savedLow/savedHigh,
      netLow/netHigh, or the money() formatter.
"""
import json
import sys

SRC = "/Users/cya822/2SK/fred-hollows/work/iframe-poc/embed/index.html"
OUT = "/tmp/fhf-change-list.json"

# (tag, reason, old, new, expected_count)
E = []
def e(tag, reason, old, new, n=1):
    E.append(dict(tag=tag, reason=reason, old=old, new=new, n=n))

# ---------------------------------------------------------------- C1 · register
e("C1", "口語化；「步驟一」與後續區塊一致",
  '<p class="eyebrow">第一步</p>',
  '<p class="eyebrow">步驟一</p>')

e("C1", "「就咁多」過於口語",
  '<p class="lede">一個金額，一個大概嘅入息範圍。就咁多。</p>',
  '<p class="lede">只需一個捐款金額，以及大約的入息範圍。</p>')

e("C1", "「您想捐幾多？」口語；標籤應為欄位名稱",
  '<label for="gift">您想捐幾多？(HK$)</label>',
  '<label for="gift">捐款金額（HK$）</label>')

e("C1", "「銀碼」「揀選」口語用詞",
  '<p class="hint" id="gift-hint">直接輸入銀碼，或用上面嘅金額快速揀選。</p>',
  '<p class="hint" id="gift-hint">可直接輸入金額，或選用上方預設金額。</p>')

e("C1", "「會捐幾個月？」口語；「捐款月數」為書面語",
  '<label for="months">課稅年度內會捐幾個月？</label>',
  '<label for="months">本課稅年度內的捐款月數</label>')

e("C1", "「係…嘅話」口語句式",
  '<p class="hint" id="months-hint">扣稅係按全年捐款總額計算，所以只捐幾個月嘅話，請填實際月數。</p>',
  '<p class="hint" id="months-hint">扣稅按全年捐款總額計算；如只捐款數個月，請填寫實際月數。</p>')

e("C1", "「您嘅…係？」口語句尾",
  '<legend>您嘅全年應評稅入息大約係？（未扣免稅額；免稅額以 HK$145,000 估算）</legend>',
  '<legend>您全年應評稅入息大約是？（未扣除免稅額；免稅額以 HK$145,000 估算）</legend>')

e("C1", "「唔知道」口語",
  '<span>唔知道 — 顯示範圍</span>',
  '<span>不確定 — 顯示估算範圍</span>')

e("C7", "「未需繳稅」非正式用語；稅局慣用「無須繳稅」",
  '<span>HK$145,000 以下</span><span class="r">未需繳稅</span>',
  '<span>HK$145,000 以下</span><span class="r">無須繳稅</span>')

e("C1", "流動版下拉選單的無障礙標籤同步改寫",
  'aria-label="您嘅全年應評稅入息大約係？（未扣免稅額）"',
  'aria-label="您全年應評稅入息大約是？（未扣除免稅額）"')

e("C1", "下拉選單選項同步改寫",
  '<option value="unknown">唔知道 — 顯示 2% – 17% 範圍</option>',
  '<option value="unknown">不確定 — 顯示 2% – 17% 範圍</option>')

e("C7", "下拉選單選項同步改寫為「無須繳稅」",
  '<option value="r0">HK$145,000 以下 — 未需繳稅</option>',
  '<option value="r0">HK$145,000 以下 — 無須繳稅</option>')

e("C1", "整段註解口語化（嘅/呢筆/唔係計錯）；改為書面語並保留標準稅率解釋的位置",
  '''      <p class="note">入息低於約 HK$145,000（單身免稅額）嘅話，可能未需要繳交薪俸稅，呢筆捐款就扣唔到稅。
      入息越高邊際稅率通常越高（最高 17%）；但入息淨額超過約 HK$2,132,500 之後，稅局會改用<b>標準稅率</b>計算
      （首 HK$500 萬 15%，超過部分 16%），所以最頂兩級嘅比率反而回落 —— 呢個係香港薪俸稅嘅設計，唔係計錯。</p>''',
  '''      <p class="note">應評稅入息低於約 HK$145,000（基本免稅額）者，或無須繳付薪俸稅，該筆捐款便不能扣稅。
      應評稅入息越高，邊際稅率通常越高（最高 17%）；但應評稅入息淨額超過約 HK$2,132,500 後，稅務局會改用<b>標準稅率</b>計算
      （首 HK$500 萬 15%，其後 16%），因此最頂兩級的比率反而回落 —— 這是香港薪俸稅的設計，並非計算錯誤。</p>''')

e("C1", "「第二步」與後續區塊一致",
  '<p class="eyebrow">第二步</p>',
  '<p class="eyebrow">步驟二</p>')

e("C1", "「您嘅」→「您的」",
  '<h2 id="s2h">您嘅估算結果</h2>',
  '<h2 id="s2h">您的估算結果</h2>')

e("C1", "「慳稅」為粵語；書面語為「節省稅款」",
  '<div><dt id="saved-label">預計慳稅</dt><dd id="saved">−HK$221</dd></div>',
  '<div><dt id="saved-label">預計節省稅款</dt><dd id="saved">−HK$221</dd></div>')

e("C1", "「估算用嘅」→「估算採用的」",
  '<div><dt id="rate-label">估算用嘅邊際稅率</dt><dd id="rate">17%</dd></div>',
  '<div><dt id="rate-label">估算採用的邊際稅率</dt><dd id="rate">17%</dd></div>')

e("C1", "假設行的說明句口語化",
  '更改上面任何一項，答案會即時更新。呢個係估算，未計算其他扣除或免稅額。',
  '更改上述任何一項，估算會即時更新。此為估算，並未計算其他扣除或免稅額。')

e("C1", "上限行口語化",
  '<p id="cap">扣稅上限係應評稅入息嘅 35%（全年合計）；一般捐款金額唔會觸及上限。</p>',
  '<p id="cap">扣稅上限為應評稅入息的 35%（全年合計）；一般捐款金額不會觸及上限。</p>')

e("C1", "「第三步」與後續區塊一致",
  '<p class="eyebrow">第三步 · 付款方式</p>',
  '<p class="eyebrow">步驟三 · 付款方式</p>')

e("C1", "「同埋」「嘅」口語",
  '<p class="lede">PayMe、AlipayHK 二維碼，同埋前往護瞳行動網站嘅信用卡。</p>',
  '<p class="lede">PayMe、AlipayHK 二維碼，以及前往護瞳行動網站的信用卡。</p>')

e("C1", "付款說明段落全面書面化（同/喺/就會/換成…嘅）",
  '<p class="note" style="margin:0 0 14px">PayMe 同 AlipayHK 用二維碼喺您自己嘅 App 內完成；信用卡就會帶您去護瞳行動現有嘅捐款頁。正式上線時二維碼會換成客戶提供嘅商戶碼。</p>',
  '<p class="note" style="margin:0 0 14px">PayMe 及 AlipayHK 以二維碼於您自己的 App 內完成；信用卡則會帶您前往護瞳行動現有的捐款頁。正式上線時，二維碼將換成客戶提供的商戶碼。</p>')

e("C1", "「喺…內」→「並於…內」",
  '<span class="qr-mob">長按下方二維碼儲存，喺 PayMe 內完成捐款</span>',
  '<span class="qr-mob">長按下方二維碼儲存，並於 PayMe 內完成捐款</span>')

e("C1", "同上，AlipayHK",
  '<span class="qr-mob">長按下方二維碼儲存，喺 AlipayHK 內完成捐款</span>',
  '<span class="qr-mob">長按下方二維碼儲存，並於 AlipayHK 內完成捐款</span>')

e("C1", "「用手機捐？」「分享到」口語",
  '<h3>用手機捐？長按二維碼，分享到付款 App</h3>',
  '<h3>以手機捐款：長按二維碼，分享至付款 App</h3>')

e("C1", "「搵返嗰張」「用該 App 內嘅」口語；整段改寫",
  '<p>長按上面<strong>對應嘅</strong>二維碼儲存圖片（每個 App 一個碼），再打開 <b>PayMe</b> 或 <b>AlipayHK</b>，用該 App 內嘅「掃描」或「相簿」功能揀返嗰張二維碼，然後輸入 <strong class="qr-amount">HK$1,300</strong>。</p>',
  '<p>長按上方<strong>對應的</strong>二維碼儲存圖片（每個 App 一個碼），再開啟 <b>PayMe</b> 或 <b>AlipayHK</b>，使用該 App 內的「掃描」或「相簿」功能選取該二維碼，然後輸入 <strong class="qr-amount">HK$1,300</strong>。</p>')

e("C1", "掃描說明句書面化",
  '<p>用另一部手機嘅相機或付款 App 掃描，再輸入 <strong class="qr-amount">HK$1,300</strong>。</p>',
  '<p>請以另一部手機的相機或付款 App 掃描，然後輸入 <strong class="qr-amount">HK$1,300</strong>。</p>')

e("C1", "「唔會帶金額」「喺…內」口語",
  '<p class="fine">二維碼為靜態碼，本身唔會帶金額，金額要喺付款 App 內自行輸入。</p>',
  '<p class="fine">二維碼為靜態碼，本身不包含金額，須於付款 App 內自行輸入金額。</p>')

e("C1", "「撳一下睇…能唔能夠」口語",
  '<p class="hint" style="margin:0 0 8px"><b>App 開啟測試（POC）：</b>撳一下睇 iframe 內能唔能夠叫起付款 App。正式版會用商戶提供嘅 deep link。</p>',
  '<p class="hint" style="margin:0 0 8px"><b>App 開啟測試（POC）：</b>點按下方按鈕，測試 iframe 內能否開啟付款 App。正式版將採用商戶提供的 deep link。</p>')

e("C1", "「留低…就得」口語",
  '<h2 id="rch" style="font-size:1.05rem">想收到扣稅收據？留低姓名同電郵就得。</h2>',
  '<h2 id="rch" style="font-size:1.05rem">需要扣稅收據？只需留下姓名及電郵。</h2>')

e("C7", "HK$100 門檻是全年「捐款總額」的合計測試，不是每筆捐款測試；同時書面化",
  '<p class="lede" style="margin-bottom:14px">我哋只需要收據抬頭同電郵，用嚟發出正式收據。捐款滿 HK$100 先可以獲發正式收據。</p>',
  '<p class="lede" style="margin-bottom:14px">我們只需收據抬頭及電郵，用以發出正式收據。課稅年度內捐款總額滿 HK$100，方可獲發正式收據。</p>')

e("C1", "同意書句法書面化（我哋/嘅/用…為我）",
  '<label for="consent">我同意護瞳行動用我嘅姓名同電郵，為我發出扣稅收據。</label>',
  '<label for="consent">本人同意護瞳行動使用本人的姓名及電郵，以發出扣稅收據。</label>')

e("C1", "POC 說明書面化；「記憶體」為正寫",
  '<p class="fine">POC 示範：資料只會留喺呢個測試頁嘅記憶體，唔會傳送去任何伺服器，亦唔會儲存。正式版會由 2SK 建嘅收據系統接收，並依客戶指示傳送至其 CRM。</p>',
  '<p class="fine">POC 示範：資料只保留於本測試頁的記憶體，不會傳送至任何伺服器，亦不會儲存。正式版將由 2SK 建立的收據系統接收，並依客戶指示傳送至其 CRM。</p>')

e("C1", "頁尾說明書面化；「慳到嘅稅額」→「所節省的稅款」",
  '<p class="fine" style="max-width:70ch">* 計算機只估算<strong>薪俸稅</strong>下嘅捐款扣稅，並非稅務建議。實際可扣稅額以稅務局評定為準。扣稅上限為應評稅入息或利潤嘅 35%，而慳到嘅稅額等於捐款乘以您嘅適用稅率。</p>',
  '<p class="fine" style="max-width:70ch">* 本計算機只估算<strong>薪俸稅</strong>下的捐款扣稅，並非稅務建議。實際可扣除金額以稅務局的評定為準。扣稅上限為應評稅入息或利潤的 35%；所節省的稅款等於捐款金額乘以您的適用稅率。</p>')

# ------------------------------------------------------------ C1 · JS copy
e("C1", "範圍模式的說明句口語化",
  'cap += "入息範圍未指定，所以顯示 2% 至 17% 嘅估算範圍。";',
  'cap += "未指定入息範圍，因此顯示 2% 至 17% 的估算範圍。";')

e("C1", "「想睇確實數字，揀一個就得」口語",
  'cap = "呢個係範圍 —— 由最低 2% 到最高 17%。想睇確實數字，揀一個入息範圍就得。";',
  'cap = "這是估算範圍 —— 由最低 2% 至最高 17%。如需準確數字，請選擇一個入息範圍。";')

e("C1", "「呢個先係真正離開您戶口嘅金額」口語",
  'cap = "呢個先係真正離開您戶口嘅金額。";',
  'cap = "這是實際由您支付的金額。";')

e("C1", "「預計慳稅（最多）」→「預計節省稅款（最多）」",
  '$("#saved-label").textContent = "預計慳稅" + (annual >= CAP_FLAG_FROM ? "（最多）" : "");',
  '$("#saved-label").textContent = "預計節省稅款" + (annual >= CAP_FLAG_FROM ? "（最多）" : "");')

e("C1", "「估算用嘅」→「估算採用的」",
  '$("#rate-label").textContent = "估算用嘅" + rateWord;',
  '$("#rate-label").textContent = "估算採用的" + rateWord;')

e("C1", "假設句口語化",
  '? "應評稅入息範圍未指定 · 適用稅率 2% – 17% 之間。"',
  '? "應評稅入息範圍未指定 · 適用稅率介乎 2% – 17%。"')

e("C1", "觸及上限時的說明口語化",
  '? "扣稅上限係應評稅入息嘅 35%（全年合計）。呢個金額比較大，最終可扣稅額可能受 35% 上限限制。"\n      : "扣稅上限係應評稅入息嘅 35%（全年合計）；一般捐款金額唔會觸及上限。";',
  '? "扣稅上限為應評稅入息的 35%（全年合計）。此金額較大，最終可扣除額可能受 35% 上限限制。"\n      : "扣稅上限為應評稅入息的 35%（全年合計）；一般捐款金額不會觸及上限。";')

e("C1", "螢幕報讀語句口語化（慳稅）",
  '+ (isRange ? " 估算慳稅由 " + money(savedLow) + " 至 " + money(savedHigh) + "。" : " 估算慳稅 " + money(savedHigh) + "，適用" + rateWord + " " + Math.round(rHigh*100) + "%。");',
  '+ (isRange ? " 估算節省稅款由 " + money(savedLow) + " 至 " + money(savedHigh) + "。" : " 估算節省稅款 " + money(savedHigh) + "，適用" + rateWord + " " + Math.round(rHigh*100) + "%。");')

e("C1", "deep link 狀態訊息口語化",
  'msg.textContent = "已嘗試叫起 " + (rail === "payme" ? "PayMe" : "AlipayHK") + "…";',
  'msg.textContent = "已嘗試開啟 " + (rail === "payme" ? "PayMe" : "AlipayHK") + "…";')

e("C1", "「冇得測」「請喺」口語",
  'msg.textContent = "呢一頁未放入 iframe，所以冇得測 App 跳轉 —— 請喺 Test Bench 或 CMS 內嘅 iframe 版本測試。";',
  'msg.textContent = "本頁未嵌入 iframe，因此無法測試 App 跳轉 —— 請在 Test Bench 或 CMS 內的 iframe 版本測試。";')

e("C1", "「停喺呢度」「冇處理」「同」口語",
  'msg.textContent = "頁面仍然停喺呢度 —— 表示瀏覽器／iframe 冇處理呢個 App scheme（iOS Safari 同沙盒 iframe 常見）。正式版需要二維碼或頂層跳轉。";',
  'msg.textContent = "頁面仍然停留於此 —— 表示瀏覽器或 iframe 未處理此 App scheme（iOS Safari 及沙盒 iframe 常見）。正式版需要二維碼或頂層跳轉。";')

e("C1", "提交成功訊息口語化",
  's.textContent = "多謝您。我哋會喺捐款後跟進發出收據（POC：未接駁後端）。";',
  's.textContent = "多謝您。我們會於您捐款後跟進發出收據（POC：尚未接駁後端）。";')

# --------------------------------------------- C6 · benefit line (markup + CSS)
e("C6", "新增「稅務回饋」一句（客戶認為的 selling point）：捐款多少、可扣多少、實際付出多少",
  '''    </dl>

    <div class="assump">''',
  '''    </dl>

    <p class="benefit" id="benefit">您捐 HK$1,300，全數可作認可慈善捐款扣除；估算稅務回饋 HK$221，即每捐 HK$100，實際付出約 HK$83。</p>

    <div class="assump">''')

e("C6", "benefit line 樣式：橙色左線，讀起來像一句結論而不是另一行數據",
  '.assump{display:grid;gap:8px;margin-top:14px;font-size:var(--t-cap);color:var(--muted)}',
  '''/* the C6 line — the client's "selling point": what the donor actually gets back */
.benefit{font-size:var(--t-sm);color:#3a3a44;margin:16px 0 0;padding:2px 0 2px 12px;
  border-left:3px solid var(--orange);line-height:1.55}
.assump{display:grid;gap:8px;margin-top:14px;font-size:var(--t-cap);color:var(--muted)}''')

# --------------------------------- C2 · scope line, spouse note, disclaimer
e("C2", "境界守則：一句講清計算機只模擬個人薪俸稅，並非稅務建議（放在數字旁邊，而非頁尾）",
  '''      <div><span class="k">上限：</span><p id="cap">扣稅上限為應評稅入息的 35%（全年合計）；一般捐款金額不會觸及上限。</p></div>
    </div>
  </section>''',
  '''      <div><span class="k">上限：</span><p id="cap">扣稅上限為應評稅入息的 35%（全年合計）；一般捐款金額不會觸及上限。</p></div>
    </div>

    <p class="fine scope">本計算機只估算個人在薪俸稅下的捐款扣稅，並非稅務建議。</p>

    <details class="q" id="spouse">
      <summary>夫婦的扣稅額可以合併使用嗎？</summary>
      <p>若您未能用盡扣稅額（包括超過 35% 上限而未扣除的部分），配偶可在其 BIR60 報稅表內申報。但配偶本人的申報同樣以 35% 為上限，上限按其本人的入息或利潤計算；因此未用的扣稅額並非可全數轉移。</p>
    </details>
  </section>''')

e("C2", "折疊式問答的樣式（summary 具 44px 觸控高度）",
  '.pocbar b{letter-spacing:.06em}',
  '''.pocbar b{letter-spacing:.06em}
details.q{margin:16px 0 0;border-top:1px solid var(--line);padding-top:4px;font-size:var(--t-cap)}
details.q summary{cursor:pointer;font-size:var(--t-sm);font-weight:600;min-height:44px;display:flex;align-items:center;gap:8px}
details.q summary::marker{color:var(--muted)}
details.q p{margin:2px 0 0;color:var(--muted);line-height:1.6}
p.fine.scope{font-size:var(--t-cap);color:#6a6a74}''')

e("C2", "免責聲明：同意書下方一條連結（方案 B），全文折疊在收據區底部",
  '''        <label for="consent">本人同意護瞳行動使用本人的姓名及電郵，以發出扣稅收據。</label>
      </div>''',
  '''        <label for="consent">本人同意護瞳行動使用本人的姓名及電郵，以發出扣稅收據。</label>
      </div>
      <p class="fine" style="margin:0 0 0 31px">使用本計算機及提交資料前，請先閱讀<a href="#disclaimer" id="disc-link">免責聲明</a>。</p>''')

e("C2", "免責聲明全文（<details> 折疊，佔一行高度，不擠壓固定的 iframe 高度）",
  '''    </form>
  </section>''',
  '''    </form>
    <details class="q" id="disclaimer">
      <summary>免責聲明</summary>
      <p>本計算機只提供估算，並非稅務建議，亦不能取代專業意見。估算依據稅務局於所示課稅年度的規定，只計入認可慈善捐款的扣稅，並未計算其他扣除、免稅額或稅務寬減；實際可扣除金額及應繳稅款以稅務局的評定為準。本計算機不會收集或儲存任何資料；您在本表格自願提供的姓名及電郵，只用作發出扣稅收據。</p>
    </details>
  </section>''')

e("C2", "點擊免責聲明連結時同時展開折疊內容，否則連結指向一段看不見的文字",
  '''  ["#rname","#rmail"].forEach(function(sel){ $(sel).addEventListener("input", scheduleHeight); });''',
  '''  ["#rname","#rmail"].forEach(function(sel){ $(sel).addEventListener("input", scheduleHeight); });
  /* the consent-line link must OPEN the collapsed text, not just jump to it */
  var dl_ = $("#disc-link");
  if (dl_) dl_.addEventListener("click", function () {
    var d = $("#disclaimer"); if (d) { d.open = true; scheduleHeight(); }
  });''')

# --------------------------------------------------------------- C6 · JS line
e("C6", "benefit line 由 render() 計算（不改動任何稅務運算，只讀既有的 savedLow/savedHigh）",
  '''    $$(".qr-amount").forEach(function(e){ e.textContent = money(annual); });''',
  '''    /* C6 — "you give this, you get that back". Reads the numbers the engine
       already produced; it computes nothing the figures strip does not show. */
    var bEl = $("#benefit");
    if (bEl) {
      if (annual <= 0) {
        bEl.textContent = "輸入捐款金額後，這裡會顯示您實際付出多少、節省多少稅款。";
      } else if (isRange) {
        bEl.textContent = "您捐 " + money(annual) + "，全數可作認可慈善捐款扣除；估算稅務回饋介乎 "
          + money(savedLow) + " 至 " + money(savedHigh) + "，即每捐 HK$100，實際付出約 HK$"
          + Math.round(100*(1-rHigh)) + " 至 HK$" + Math.round(100*(1-rLow)) + "。";
      } else if (rHigh === 0) {
        bEl.textContent = "您捐 " + money(annual) + "，全數可作認可慈善捐款扣除。以您的入息水平估算，"
          + "無須繳付薪俸稅，因此這筆捐款不會減少稅款。";
      } else if (annual >= CAP_FLAG_FROM) {
        bEl.textContent = "您捐 " + money(annual) + "。可扣除金額受應評稅入息 35% 上限限制，"
          + "超出部分不能扣除；估算稅務回饋最多 " + money(savedHigh) + "。";
      } else {
        bEl.textContent = "您捐 " + money(annual) + "，全數可作認可慈善捐款扣除；估算稅務回饋 "
          + money(savedHigh) + "，即每捐 HK$100，實際付出約 HK$" + Math.round(100*(1-rHigh)) + "。";
      }
    }

    $$(".qr-amount").forEach(function(e){ e.textContent = money(annual); });''')

# ------------------------------------------------------------- C4 · mobile pass
e("C4", "手機斷點：44px 觸控目標、收緊間距、縮小二維碼 —— 全部集中一段 @media，不動桌面量度",
  '''#dbg b{color:#ffd7a8}
</style>''',
  '''#dbg b{color:#ffd7a8}

/* ---------- phones (C4) -----------------------------------------------------
   Two defects were reported on mobile, which is 80–90% of their traffic:
   1. two nested scrollbars. The blocks are embedded at a fixed pixel height,
      so any content taller than that number becomes an inner scrollbar inside
      the page's own scroll. The fix is both halves: reduce the phone content,
      and declare a height that the measurement supports (docs/INTERFACE.md).
   2. fat fingers. Chips were 35px and the segmented control 41px; WCAG 2.5.5
      asks for 44. Everything below is a 44px minimum or a spacing saving.
   Every override lives here so no desktop measurement can move. */
@media (max-width:640px){
  :root{--panel:16px}
  .card + .card{margin-top:10px}
  .field{margin-top:14px}
  .seg label{padding:12px 10px;min-height:44px;display:flex;align-items:center;justify-content:center}
  .chips{gap:8px}
  .chips button{min-height:44px;padding:10px 14px;font-size:var(--t-sm)}
  .bands label{min-height:44px}
  #band-mobile{min-height:44px}
  select#months{min-height:44px}
  .rform .consent{min-height:44px;align-items:center;gap:12px}
  .rform .consent input{width:22px;height:22px;margin:0;flex:0 0 auto}
  .figs > div{padding:9px 12px}
  .qr-fig img{max-width:104px}
  .benefit{font-size:var(--t-sm)}
  details.q summary{min-height:44px}
}
</style>''')

# ---------------------------------------------- C4 · hide dead control in part
e("C4", "?part=calc 內「查看結果」是死連結（區塊本身不滾動），移除它省下約 70px 固定高度",
  '''body[data-part="input"] #goto-result,
body[data-part="result"] #goto-result,
body[data-part="input"] #upd{display:none}''',
  '''body[data-part="input"] #goto-result,
body[data-part="result"] #goto-result,
body[data-part="calc"] #goto-result,
body[data-part="calc"] #upd,
body[data-part="input"] #upd{display:none}''')

# ------------------------------------------------- C4 · pay block height trim
e("C4", "?part=calc 內「查看結果」是死連結（區塊本身不滾動）；外部 div 帶 inline display:flex，須連容器一併隱藏",
  '''    <div class="field" style="display:flex;gap:12px;align-items:center;flex-wrap:wrap">
      <a class="btn" href="#result" id="goto-result" style="width:auto;text-decoration:none">查看結果 →</a>''',
  '''    <div class="field" id="goto-row" style="display:flex;gap:12px;align-items:center;flex-wrap:wrap">
      <a class="btn" href="#result" id="goto-result" style="width:auto;text-decoration:none">查看結果 →</a>''')

e("C4", "同上：把整個「查看結果」列在單一區塊 embed 內隱藏，省下固定高度",
  '''body[data-part="input"] #goto-result,
body[data-part="result"] #goto-result,
body[data-part="calc"] #goto-result,
body[data-part="calc"] #upd,
body[data-part="input"] #upd{display:none}''',
  '''body[data-part="input"] #goto-row,
body[data-part="result"] #goto-row,
body[data-part="calc"] #goto-row{display:none!important}''')

e("C4", "最窄的 320px 機種仍需再省約 20px，否則付款區在 1,040px 內溢出 12px",
  '''  .benefit{font-size:var(--t-sm)}
  details.q summary{min-height:44px}
}''',
  '''  .benefit{font-size:var(--t-sm)}
  details.q summary{min-height:44px}
}
/* the narrowest phones still overflow by ~12px: buy the room back from
   padding and the QR image, never from a sentence */
@media (max-width:400px){
  .card{padding:14px}
  .qr-grid{gap:10px}
  .qr-fig{padding:9px}
  .qr-fig img{max-width:96px}
}''')

e("C4", "同意書的 label 本身也補到 44px，令可點範圍與整列一致",
  '''  .rform .consent input{width:22px;height:22px;margin:0;flex:0 0 auto}''',
  '''  .rform .consent input{width:22px;height:22px;margin:0;flex:0 0 auto}
  .rform .consent label{min-height:44px;display:flex;align-items:center}''')

e("C4", "付款區在 328px 寬時內容 1,051px，超出客戶設定的 1,040px；收短說明段",
  '<p class="note" style="margin:0 0 14px">PayMe 及 AlipayHK 以二維碼於您自己的 App 內完成；信用卡則會帶您前往護瞳行動現有的捐款頁。正式上線時，二維碼將換成客戶提供的商戶碼。</p>',
  '<p class="note" style="margin:0 0 14px">PayMe 及 AlipayHK 以二維碼於您自己的 App 內完成；信用卡則前往護瞳行動現有的捐款頁。正式上線時會換成客戶提供的商戶碼。</p>')

# ------------------------------------------- C6/C7 · cap-bound wording (copy only)
# Measured defect, not a copy preference: for a HK$250,000 gift at HK$500,000
# assessable income the cap limits the deduction to HK$175,000, so the true
# saving is HK$29,150 — but the widget prints the uncapped HK$42,500 and labels
# it 「最多」 ("at most"). That is an overstatement of the maximum, the same class
# of error as implying a 35% cash saving. The arithmetic is left exactly as it
# is; only the label and the sentence change, so the figure is framed as an
# upper bound instead of a claim.
e("C6", "「（最多）」把未扣上限的數字講成上限值；改為「（未扣上限）」",
  '$("#saved-label").textContent = "預計節省稅款" + (annual >= CAP_FLAG_FROM ? "（最多）" : "");',
  '$("#saved-label").textContent = "預計節省稅款" + (annual >= CAP_FLAG_FROM ? "（未扣上限）" : "");')

e("C6", "benefit line 在上限情況下不可講「最多」；改為「會低於」這個真確的上界",
  '''      } else if (annual >= CAP_FLAG_FROM) {
        bEl.textContent = "您捐 " + money(annual) + "。可扣除金額受應評稅入息 35% 上限限制，"
          + "超出部分不能扣除；估算稅務回饋最多 " + money(savedHigh) + "。";''',
  '''      } else if (annual >= CAP_FLAG_FROM) {
        bEl.textContent = "您捐 " + money(annual) + "。可扣除金額受應評稅入息 35% 上限限制，"
          + "超出部分不能扣除；估算稅務回饋會低於 " + money(savedHigh) + "。";''')

e("C6", "上限說明講清楚實際稅款會低於上列數字，避免讀者以為該數字已計上限",
  '''? "扣稅上限為應評稅入息的 35%（全年合計）。此金額較大，最終可扣除額可能受 35% 上限限制。"''',
  '''? "扣稅上限為應評稅入息的 35%（全年合計）。此金額較大：超出上限的捐款不能扣除，"
        + "實際節省的稅款會低於上列數字。"''')

# ------------------------------------- C4/C2 · fixes found by looking at the shots
e("C4", "display:flex 會令 <summary> 的原生三角標記消失，折疊問答因此看起來像一行粗體字（screenshot 覆核發現）",
  'p.fine.scope{font-size:var(--t-cap);color:#6a6a74}',
  '''p.fine.scope{font-size:var(--t-cap);color:#6a6a74}
/* display:flex on <summary> suppresses the native disclosure triangle in
   Blink/WebKit, which left a collapsed FAQ with no visible affordance. Draw it. */
details.q summary{list-style:none}
details.q summary::-webkit-details-marker{display:none}
details.q summary::before{content:"\\25B8";color:var(--muted);flex:0 0 auto}
details.q[open] summary::before{content:"\\25BE"}''')

e("C2", "scope line 已放在結果卡內，頁尾那句重複；頁尾保留法務免責與公式",
  '<p class="fine" style="max-width:70ch">* 本計算機只估算<strong>薪俸稅</strong>下的捐款扣稅，並非稅務建議。實際可扣除金額以稅務局的評定為準。',
  '<p class="fine" style="max-width:70ch">* 實際可扣除金額以稅務局的評定為準。')

# ------------------------------------- C1 · leftovers a residue scan caught
# After the pass, a grep for 嘅/咗/喺/冇/慳/睇/撳/嗰/唔/呢個/咁 still found four
# hits: the static caption (overwritten by render() but visible before boot and
# if the script fails), the submit button, and one BANDS label.
e("C1", "靜態預設字幕仍有口語（render() 會覆寫，但 JS 未跑時就是這句）",
  '<p class="caption" id="net-caption">呢個先係真正離開您戶口嘅金額。</p>',
  '<p class="caption" id="net-caption">這是實際由您支付的金額。</p>')

e("C1", "「留低資料」→「留下資料」（與標題「只需留下姓名及電郵」一致，且不像「提交」那樣公文化）",
  '<button class="btn" type="submit" id="rsubmit">留低資料</button>',
  '<button class="btn" type="submit" id="rsubmit">留下資料</button>')

e("C1", "BANDS 內的「唔知道」標籤同步書面化",
  'unknown:{rate:null,low:.02,high:.17,range:true,label:"唔知道"},',
  'unknown:{rate:null,low:.02,high:.17,range:true,label:"不確定"},')

e("C2", "免責聲明補上範圍排除句：不涵蓋利潤稅、個人入息課稅、夫婦合併評稅（法務會問這一句）",
  '只計入認可慈善捐款的扣稅，並未計算其他扣除、免稅額或稅務寬減；實際可扣除金額及應繳稅款以稅務局的評定為準。',
  '只計入認可慈善捐款的扣稅，並未計算其他扣除、免稅額或稅務寬減；亦不涵蓋利潤稅、個人入息課稅或夫婦合併評稅。實際可扣除金額及應繳稅款以稅務局的評定為準。')

e("C4", "折疊內容展開時要重新報高度，否則支援 auto-height 的 host 不會跟隨（固定高度 host 不受影響）",
  "if (dl_) dl_.addEventListener(\"click\", function () {",
  """$$(\"details.q\").forEach(function(d){
    d.addEventListener(\"toggle\", function(){ scheduleHeight(); });
  });
  if (dl_) dl_.addEventListener(\"click\", function () {""")


def main():
    with open(SRC, encoding="utf-8") as f:
        s = f.read()
    orig = s
    applied = []
    for item in E:
        c = s.count(item["old"])
        if c != item["n"]:
            print(f"ABORT  expected {item['n']} of {item['old'][:60]!r}, found {c}")
            sys.exit(1)
        s = s.replace(item["old"], item["new"])
        applied.append(item)
    if s == orig:
        print("ABORT  no change")
        sys.exit(1)
    with open(SRC, "w", encoding="utf-8") as f:
        f.write(s)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(applied, f, ensure_ascii=False, indent=1)
    print(f"applied {len(applied)} replacements -> {len(orig)} -> {len(s)} bytes")
    print(f"change list -> {OUT}")


if __name__ == "__main__":
    main()
