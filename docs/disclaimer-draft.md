# 免責聲明 — 兩個放置方案（中英對照）

> ## ⚠️ DRAFT — FOR CLIENT LEGAL REVIEW
> 本文件為草稿，未經法律審閱。中文為香港書面語（Traditional Chinese, Hong Kong），英文為對照譯本。**兩個方案的內文完全相同，只有位置不同。** 請 Denise 與其法務選定一個方案，我們再落實到 widget。
>
> This is a **draft, not legal advice**. Both placements carry identical wording; only the position differs. Please have the client's legal team approve one option and the wording before it ships.

---

## 背景 / Background

The widget estimates the salaries-tax saving of a donation. Three statements are required by the honesty rules that govern this build, and all three are in the text below:

1. **It is an estimate only** — the real figure is whatever the IRD assesses.
2. **It models one thing** — salaries tax for an individual, for the stated year of assessment; not profits tax, not personal assessment, not joint assessment.
3. **It collects nothing** — the calculator itself stores no data. Only the optional receipt form takes a name and an email, and only to issue a receipt.

The second point matters commercially as well as legally: the widget answers 「這筆捐款幫我節省多少稅」, not 「我的稅單是多少」. Saying so protects the answer rather than weakening it.

---

## 方案 A — 同意書下方直接顯示（inline）

**Placement:** the full text, always visible, immediately under the consent checkbox, above the submit button.

**Variant A adds ~90px at phone width**, which takes the receipt block's declared height from 650px to 740px. If the client prefers A, the height in `docs/INTERFACE.md` §2 must change with it.

### 中文（香港）

> **免責聲明**
>
> 本計算機只提供估算，並非稅務建議，亦不能取代會計師、稅務顧問或稅務局的意見。估算依據香港稅務局於所示課稅年度的《稅務條例》及薪俸稅規定，只計入認可慈善捐款的扣稅，並未計算其他扣除、免稅額、稅務寬減或稅務優惠；實際可扣除金額及應繳稅款，以稅務局的評定為準。本計算機只模擬個人在薪俸稅下的情況，不涵蓋利潤稅、個人入息課稅或夫婦合併評稅。
>
> 本計算機不會收集或儲存任何資料。您在本表格自願提供的姓名及電郵，只用作發出扣稅收據，並依《個人資料（私隱）條例》處理。

### English

> **Disclaimer**
>
> This calculator provides an estimate only. It is not tax advice, and it does not replace the opinion of an accountant, a tax adviser or the Inland Revenue Department (IRD). The estimate applies the Inland Revenue Ordinance and the salaries tax rules of the Inland Revenue Department for the year of assessment shown, and takes account of the approved charitable donation deduction only. It does not account for any other deduction, allowance, reduction or concession. The amount actually deductible, and the tax actually payable, are determined by the IRD. This calculator models an individual's salaries tax only. It does not cover profits tax, personal assessment, or joint assessment of a married couple.
>
> This calculator does not collect or store any data. The name and email address you choose to provide in this form are used solely to issue a tax-deductible donation receipt, and are handled in accordance with the Personal Data (Privacy) Ordinance.

---

## 方案 B — 收據區底部折疊，同意書下一條連結（collapsed）✅ **目前實作**

**Placement:** a single link under the consent line — 「使用本計算機及提交資料前，請先閱讀免責聲明。」 — pointing at a collapsed `<details>` block at the foot of the receipt block. Clicking the link opens the block as well as jumping to it.

**Variant B costs one 44px row** and does not change any declared height. It is what is in `embed/index.html` now.

### 中文（香港）

> **免責聲明**
>
> 本計算機只提供估算，並非稅務建議，亦不能取代會計師、稅務顧問或稅務局的意見。估算依據香港稅務局於所示課稅年度的《稅務條例》及薪俸稅規定，只計入認可慈善捐款的扣稅，並未計算其他扣除、免稅額、稅務寬減或稅務優惠；實際可扣除金額及應繳稅款，以稅務局的評定為準。本計算機只模擬個人在薪俸稅下的情況，不涵蓋利潤稅、個人入息課稅或夫婦合併評稅。
>
> 本計算機不會收集或儲存任何資料。您在本表格自願提供的姓名及電郵，只用作發出扣稅收據，並依《個人資料（私隱）條例》處理。

### English

> **Disclaimer**
>
> This calculator provides an estimate only. It is not tax advice, and it does not replace the opinion of an accountant, a tax adviser or the Inland Revenue Department (IRD). The estimate applies the Inland Revenue Ordinance and the salaries tax rules of the Inland Revenue Department for the year of assessment shown, and takes account of the approved charitable donation deduction only. It does not account for any other deduction, allowance, reduction or concession. The amount actually deductible, and the tax actually payable, are determined by the IRD. This calculator models an individual's salaries tax only. It does not cover profits tax, personal assessment, or joint assessment of a married couple.
>
> This calculator does not collect or store any data. The name and email address you choose to provide in this form are used solely to issue a tax-deductible donation receipt, and are handled in accordance with the Personal Data (Privacy) Ordinance.

---

## 目前 widget 內的實際文字（方案 B）

收據區同意書下方：

> 使用本計算機及提交資料前，請先閱讀免責聲明。

收據區底部折疊標題與內容：

> **免責聲明**
>
> 本計算機只提供估算，並非稅務建議，亦不能取代專業意見。估算依據稅務局於所示課稅年度的規定，只計入認可慈善捐款的扣稅，並未計算其他扣除、免稅額或稅務寬減；實際可扣除金額及應繳稅款以稅務局的評定為準。本計算機不會收集或儲存任何資料；您在本表格自願提供的姓名及電郵，只用作發出扣稅收據。

兩者差異：widget 版本較短，省略了「不涵蓋利潤稅、個人入息課稅或夫婦合併評稅」一句，因為結果區已有一句 scope line 講明只模擬個人薪俸稅。**若法務要求，把上表較長的版本整段替換即可，不影響任何高度以外的東西。**

---

## 另外一句，放在數字旁邊（已實作）

法務文字放在收據區，但讀者看數字的地方也要有界線。結果卡底部有一句：

> 本計算機只估算個人在薪俸稅下的捐款扣稅，並非稅務建議。

English: *This calculator estimates the salaries tax deduction on a donation for an individual only. It is not tax advice.*

---

## 要法務決定的三件事

| # | 問題 | 建議 |
|---|---|---|
| 1 | 方案 A 還是 B？ | **B** — 不改變高度、不打斷捐款流程，連結仍在同意書旁；A 需把收據區高度由 650 改為 740 |
| 2 | 是否要在免責聲明內點名機構的 s.88 註冊地位？ | 建議**不要**在 widget 內引用，因為我們未獲提供其註冊編號與法定描述；如要，由客戶提供原文，我們照抄 |
| 3 | 是否需要獨立私隱聲明（PDPO）而非只在免責聲明內一句？ | 他們的 CMS 頁面完全沒有隱私聲明（skill §10a 已核實），所以**這一句是整個 iframe 內唯一的 PDPO 陳述**；若法務要求完整 notice，需另開一段，約 +120px |

---

## 英文版的注意事項（C3）

If an English page is approved, this disclaimer must ship in `/en-HK/` too. The English above is written to be acceptable to Global review as-is, but it is a **translation of the Hong Kong wording**, not a separate legal document — the client's legal team should confirm that one version governs.

`DRAFT — FOR CLIENT LEGAL REVIEW · 2026-11-15`
