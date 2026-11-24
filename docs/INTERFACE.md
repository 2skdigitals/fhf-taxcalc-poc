# Iframe contract — FHF tax calculator widget

Version **1.4.0** · POC · 2SK Solutions

Everything the host page (Optimizely CMS) must do, and everything the widget promises.
If a line here is wrong, the build is wrong — this document is the boundary between the two teams.

---

## 1 · What the widget is

| It is | It is not |
|---|---|
| The interactive calculator (amount, band, months → estimate) | The page hero, promo banner, FAQ or any editorial copy |
| The payment rails (AlipayHK QR + credit card) | A payment processor (the money moves inside AlipayHK, or on the Foundation's own card page) |
| The receipt-request capture form — **phase 2, returns with PayMe** | The receipt generator / CRM (that is the backend, Phase 1) |
| A postMessage event source for the host's GTM | An analytics implementation of its own |

The host page owns: page copy, SEO, schema, GTM container, consent, navigation, footer, and the CMS iframe component itself.

---

## 2 · The component requires a height — so the page ships as four blocks

> **Phase 1 ships three of them.** Section 5 (the receipt form) is switched off — it returns with PayMe — so
> `?part=receipt` is a 60px empty placeholder today. The split itself is unchanged; one block is simply empty.

Measured by `qa/sweep_heights.py` at **22 widths from 320px to 1440px**, per language, taking the peak and adding 45–70px of slack. **Set the number for the language you are embedding** and every block fits at every width, with no internal scrollbar.

**Write the height as a bare integer — `height=2550`, never `height=2,550`.** An unquoted attribute with a thousands separator parses as `3` in every browser: the frame collapses and the block disappears while the frames beside it keep working. It happened on the live page on 23 Nov.

| # | Block | URL | Height · zh-HK | Height · en | Content peak zh-HK | Content peak en |
|---|---|---|---|---|---|---|
| 0 | **One link (calculator → result → payment)** | `/embed/?part=all` (also the bare `/embed/`) | **2225px** | **2550px** | 2160 (at 944px, monthly) | 2482 (at 320px, monthly) |
| 1 | Calculator + result | `/embed/?part=calc` | **1720px** | **2030px** | 1656 (at 320px, monthly) | 1962 (at 320px, monthly) |
| 1a | Calculator only | `/embed/?part=input` | **1050px** | **1180px** | 987 (at 900px, monthly) | 1113 (at 320px, monthly) |
| 1b | Result only | `/embed/?part=result` | **980px** | **1190px** | 913 (at 320px) | 1129 (at 320px) |
| 2 | Payment | `/embed/?part=pay` | **690px** | **800px** | 628 (at 320px) | 739 (at 320px) |
| 3 | Receipt — **empty frame in phase 1** | `/embed/?part=receipt` | **60px** | **60px** | renders nothing | renders nothing |

**Quoted at the five widths the client asked for (content height, px) — re-measured 24 Nov 2026**

| Block | 320 | 390 | 768 | 1024 | 1440 |
|---|---|---|---|---|---|
| `?part=input` · zh | 942 | 818 | 976 | 987 | 987 |
| `?part=input` · en | 1113 | 997 | 1029 | 1006 | 1006 |
| `?part=result` · zh | 913 | 781 | 808 | 822 | 822 |
| `?part=result` · en | 1129 | 971 | 808 | 822 | 822 |
| `?part=pay` · zh | 628 | 566 | 568 | 613 | 613 |
| `?part=pay` · en | 739 | 656 | 596 | 641 | 641 |
| `?part=receipt` · zh | 60 | 60 | 60 | 60 | 60 |
| `?part=receipt` · en | 60 | 60 | 60 | 60 | 60 |
| `?part=calc` · zh | 1656 | 1452 | 1615 | 1639 | 1639 |
| `?part=calc` · en | 1962 | 1751 | 1695 | 1689 | 1689 |
| `?part=all` · zh | 2121 | 1917 | 2086 | 2156 | 2156 |
| `?part=all` · en | 2482 | 2244 | 2194 | 2234 | 2234 |

> **Revised 24 Nov 2026 (Option B payment pair, `qa/apply_pay_optionb_20261124.py`).** Kevin chose **Option B,
> "size by function"** from `design/pay-desktop/options.html` and asked for a bigger code. The desktop payment
> block is now two tiles at **≥720px**: a wide AlipayHK tile (QR + name + sub-line + the receipt note with its
> `?`) and a compact credit-card tile (glyph, name, destination on a ruled foot line). Both carry widths of
> **1.35fr / 1fr** inside a 760px pair; both are click-anywhere through a **stretched link** (the tile is a
> `<div>`, its own `<a>` paints the surface with `::after`, and the note sits above that overlay so the button
> stays real and keyboard-reachable). **Below 720px nothing changed at all** — the tiles collapse to the receipt
> note alone, which keeps its position between the two rails; the 390px block is **pixel-identical**, verified by
> diffing HEAD against this build at **13 widths from 320 to 719px in both languages (0 differing pixels)**.
>
> **The QR is the tight crop, `assets/logos/alipayhk-qr.png` (264×264).** The published card is 450×350 with the
> code at 212×212 inside 119px of white a side, so at the block's 190px ceiling the code rendered at ~90px and
> **would not decode**. The crop is the same code plus the spec's 4-module quiet zone; rendered at 190px it puts
> a ~152px code on screen, and `qa/poc_test.py` now screenshots the rendered element and decodes it with
> `cv2.QRCodeDetector` at 720/768/900/1024/1440px in both languages — every width decodes to
> `https://render.alipay.hk/…`. Phone rails still carry no QR by design.
>
> **No declared height changes.** The pair is shorter than the two cards plus the separate receipt row it
> replaces, and the peak is at 320px on a phone, which this pass does not touch: `?part=pay` stays **690 / 800**
> and `?part=all` stays **2225 / 2550**, both with more slack than before. Content moved at the desktop widths
> only — `?part=pay` **641 → 568** zh / **669 → 596** en at 768px, **649 → 613** / **677 → 641** at 1024 and
> 1440px; `?part=all` **2159 → 2086** / **2268 → 2194** at 768px and **2191 → 2156** / **2269 → 2234** at 1024px
> and above. The quoted table above is reissued accordingly; **the numbers the client pastes into the CMS do not
> change**, so there is no CMS edit in this pass.
>
> One behaviour moved with the trigger: the receipt panel used to open **upward** from 720px because the note was
> the last thing in the block. Inside the tile the note sits ~300px down a 640px frame, and there is no room
> above it, so the panel now opens **downward from the note**, 420px wide, capped at
> `clamp(240px, 100vh − 340px, 380px)`. `qa/probe_panel_fit.py` was re-run at 12 widths in both languages: the
> panel stays inside the frame on all four sides at every one, and the steps still scroll inside the panel.

> **Re-measured 24 Nov 2026** alongside the two-flow AlipayHK tooltip. The tooltip changes nothing here — it is
> absolutely positioned and starts `hidden`, and an A/B against the pre-change file reports **0px** difference at
> every width — but the re-measure exposed two rows that were already stale: `?part=pay` at ≥768px is **649 / 677**,
> not 618 / 646, because the 23 Nov "payment pair wider" pass (`5eff3b8`) widened the QR pair without reissuing the
> quotes, and `?part=all` carries the same +31px. **Every declared height still covers its real peak** (pay 690/800,
> all 2225/2550), so nothing the client pastes into the CMS changes.

> **Revised 23 Nov 2026 (phase 1 + the AlipayHK receipt route, `qa/apply_phase1_alipay_20261123.py`).**
> Phase 1 ships **AlipayHK and the credit card only**, so section 5 — the receipt-request form, which exists to
> claim a **PayMe** receipt — is switched off behind one constant (`PHASE1`) and renders nothing. It is hidden,
> never deleted: flipping that constant brings the section, its form, its popover and `?part=receipt` back with no
> other edit. Three consequences for this table:
> - **`?part=receipt` is now an EMPTY frame.** A CMS component may still point at it, and a frame must never
>   render a form that cannot submit — so the block renders nothing and reports the viewport, i.e. **60px**.
>   Delete the component if it is still on the page; the URL stays valid.
> - **`?part=all` ends after "How you give".** The receipt block leaves the one-link arrangement:
>   **2790 → 2225px** zh-HK, **3260 → 2550px** en (peaks 2724 → **2160** at 944px monthly / 3194 → **2482**
>   at 320px monthly).
> - **The payment block gains the AlipayHK receipt line** — one sentence plus the same disclosure the
>   payment-reference field uses, carrying five client screencaps (cropped to remove the transaction reference,
>   resized to 400px, 27 KB for all five). Peak 585 → **628** zh-HK, 696 → **739** en, so **pay 640 → 690px**
>   and **750 → 800px**. The panel is bounded by the space the payment frame leaves: full width below the
>   trigger on a phone, opening upward from 720px where the trigger sits low — measured at 12 widths in both
>   languages, it never leaves the frame, and the steps scroll inside the panel.
> **The disclaimer is unchanged and still closes every block that carries content.** It was already outside the
> panels (page level), so hiding section 5 does not touch it; only the empty `?part=receipt` frame suppresses it,
> because that frame renders nothing at all. Calc / input / result are unchanged (**1720 / 1050 / 980** zh-HK,
> **2030 / 1180 / 1190** en): same disclaimer, same content.
> **This is a client-side CMS edit** — the six heights they were given are superseded by these six.
> **The IRD link is unchanged and stays per language:** disclaimer item 4 is `https://www.ird.gov.hk/eng/welcome.htm`
> in English and `https://www.ird.gov.hk/chi/welcome.htm` in Chinese (the client supplied both pages). A shared
> `/chi/` URL was considered for one turn and withdrawn, because the client's English page exists.
> `qa/lang_parity.py` now asserts the two hrefs **differ** per language, so neither can be "tidied" into one.

> **Revised 24 Nov 2026 (the AlipayHK tooltip now teaches both flows, `qa/apply_alipay_two_options_20261124.py`).**
> The client reviewed the receipt tooltip and sent **two** routes, so the panel leads with the one it was missing:
> **Option 1 — tick 「需要收據」 while giving** (2 steps, the form opens under the amount) and **Option 2 — claim it
> afterwards from the donation records** (4 steps). Six 320×529 crops (67 KB) replace the five 400px ones. It is
> still ONE dialog with the same `.helpbtn`/`.helppop` contract, 420px width, its own max-height and its upward
> opening from 720px; no tabs, no second popover, no new event, colour, type size or shadow.
> **Nothing in the height table moves**: the panel is absolutely positioned and starts `hidden`, so opening it
> never grows the block (asserted by `qa/poc_test.py`) and the measured peaks are identical to the 23 Nov issue —
> `pay` stays **690 / 800** and every other block is untouched. The 23 Nov note above describes the five-crop,
> single-flow version it supersedes.

> **Revised 23 Nov 2026 (disclaimer as a numbered list, `qa/apply_disc_list_20261123.py`).**
> The collapsed `<details class="q disc-global">` at the foot of the widget becomes an always-visible
> `<h3>` + `<ol>` of five `<li>`, in both languages, with the IRD website linked from item 4. The block
> is fine print (13px, full column) and it now always occupies ~130–190px more than the 48px summary
> row did, so **every block that carries it grew and every declared height is reissued**:
> calc 1610 → **1720** zh / 1770 → **2030** en, input 950 → **1050** / 1020 → **1180**,
> result 800 → **980** / 935 → **1190**, pay 545 → **640** / 585 → **750**,
> receipt 820 → **990** / 925 → **1185**, all 2665 → **2790** / 3000 → **3260**.
> Peaks moved with them: calc 1546 → **1656** / 1703 → **1962**, input 894 → **987** / 952 → **1113**,
> result 737 → **913** / 869 → **1129**, pay 490 → **585** / 518 → **696**,
> receipt 752 → **928** / 860 → **1119**, all 2599 → **2724** / 2935 → **3194**.
> English grew more than Chinese (1962 vs 1656 on `?part=calc`) because the English list wraps to more
> lines at phone widths; **the two columns are not interchangeable.** The peak also moved to 320px in
> almost every block, so a desktop-only sweep no longer finds it.
> **This is a client-side CMS edit**: the six heights they have already been given are superseded.
> The link inside item 4 is `https://www.ird.gov.hk/eng/welcome.htm` in English and
> `/chi/welcome.htm` in Chinese — the client supplied the `/chi/` URL, but sending an English reader to
> a Chinese page is a defect; say the word and it goes back to one URL.
> **Confirmed 23 Nov 2026:** the client supplied the English page, so the pairing stays LANGUAGE-APPROPRIATE —
> English to `/eng/welcome.htm`, Chinese to `/chi/welcome.htm`. (A shared `/chi/` URL was floated for one
> turn and withdrawn.) `qa/lang_parity.py` asserts the two hrefs differ per language, not just that one exists.

> **Revised 23 Nov 2026 (client call, `qa/apply_client_call_20261123.py`) — DEFAULTS, WIDTH and TYPE.**
> Three changes from Kevin's call with the Foundation, none of them copy: (1) the calculator opens on
> **HK$100** (the field's floor, was 1,300) and the exact-income field opens on **HK$145,000** (the single
> person's basic allowance, was empty) — a starting value, never a clamp, and opening the exact swap adopts
> it so the visible field and the engine cannot disagree; (2) the column goes **896 → 1280px**, the width
> their own `div.c-dynamic-iframe` gets inside `div.container` at a 1440 viewport, so panels and cards fill
> the same column their other components fill while running text stays on the 34em measure; (3) type moves
> to the Foundation's 18px/1.56 — body **17 → 18**, block heading **28 → 32**, lede 19 → 20, sm 15 → 16,
> ledger 21 → 22, display 68 → 72, with the 13px notes and 12px eyebrow untouched.
> **Every declared height is reissued** (they are contract numbers, and both the wider column and the larger
> type move the peak): zh-HK calc **1720 → 1610**, input **1000 → 950**, result **890 → 800**, pay **580 → 545**,
> receipt **810 → 820**, all **2615 → 2665**; en calc **1720 → 1770**, input **1000 → 1020**, result
> **890 → 935**, pay **580 → 585**, receipt **910 → 925**, all **2905 → 3000**. Peaks zh-HK 1513 → **1546**,
> 882 → **894**, 737 → **737**, 479 → **490**, 746 → **752**, 2546 → **2599**; en 1652 → **1703**,
> 932 → **952**, 820 → **869**, 505 → **518**, 852 → **860**, 2835 → **2935**. Note that `?part=calc` and
> `?part=all` in Chinese peak at 944px now, not 900px: the wider column shortened the copy faster than the
> larger type lengthened it, so the desktop is no longer the tall end. The legal block takes the 34em measure
> again — at 1,216px of content it would have run ~180 characters a line at 13px — while keeping its fine-print
> size. No horizontal scroll at 390px, measured.

> **Revised 23 Nov 2026 (client copy pass, `qa/apply_client_copy_20261123.py`).** Kevin's
> section-by-section copy sheet, applied verbatim in both languages: Section 1 and 2 headers
> replaced, the four quick-amount chips **removed**, the `哪些捐款才可扣稅 / What counts as a
> deductible gift` disclosure **removed**, the band hint and the band remark rewritten (the remark is
> now 12px — a note, not body copy), the CTA reworded, and Section 3 restructured around the
> donation itself (`您的全額捐款 / Your donation` carries the amount, the ledger row that repeated it
> is gone, `節省稅款` → `預計慈善捐款扣稅額`, the benefit sentence recomputed from the donor's own
> gift, the assumption now a numbered three-line block that restores the salaries-tax-only scope,
> and the spouse FAQ removed). Section 5 gained the transaction-ID popover beside the payment
> reference. **Three declared heights are reissued**, because ~290px left the calculator:
> **calc 1800 → 1720 · input 1040 → 1000 · all 2880/2990 → 2615/2905**; result 890, pay 580 and
> receipt 810/910 are unchanged. Peaks: calc 1770 → **1513** zh / 1790 → **1652** en, input
> 1004 → **882** / 1004 → **932**, result 843 → **737** / 843 → **820**, all 2803 → **2546** /
> 2936 → **2835**; pay 479/505 and receipt 746/852 did not move at all. **The popover is bounded by the
> space left below it** (`clamp(240px, 100vh − 512px, 560px)`) so its bottom always lands inside the
> declared frame — measured fitting at 320/390/414/568/768/1280/1440 in both languages, with the three
> steps scrolling inside the panel instead of scrolling the host's fixed box.
>
> **Revised 23 Nov 2026 (design review pass, `qa/apply_design_review_20261123.py`).** Rhythm and type
> correction only — no colour, face, shadow, gradient, decoration or copy change. The `2 · your
> assessable income` heading had been sitting **0px** under the card above it and 16px above its own
> card; block gaps were 0/2/6/8/10/12/14/16/18/20/22/26/36 and now sit on one 4px scale; `--measure`
> was a fixed 544px and is now `34em`, which resolves to 68ch at every type size. **Every declared
> height is unchanged** — 1800 / 1040 / 890 / 580 / 810 / 910 / 2880 / 2990 — and every block still
> fits at all 22 widths. Content peaks rose by 2–58px to absorb the corrected spacing: `?part=calc`
> 1722 → 1770 (zh) / 1742 → **1790** (en), `?part=input` 974 → 1004, `?part=result` 833 → 843,
> `?part=pay` 477 → 479 / 503 → 505, `?part=all` 2765 → 2803 / 2878 → 2936. **`?part=receipt` is
> unchanged at 746 / 852**: the extra space between form rows was exactly cancelled by removing the
> per-child margins that were doubling the form's own grid gap. **Watch `?part=calc` in English**: it
> now sits 10px under its 1800px declaration (it was 58), the slimmest margin in the document. It
> fits, measured, at every width — but the next copy addition to that block should reissue it to 1830
> rather than assume the old headroom. Full findings, measurements and open questions:
> `docs/DESIGN-REVIEW-20261123.md`.

> **Revised 21 Nov 2026 (PayMe dropped, `qa/apply_payme_removal_20261121.py`).** The payment block
> keeps **AlipayHK and the credit card**; PayMe's QR tile, mobile row, both string-table entries, its
> CSS rule and its rail value are gone. The desktop grid went from three columns to two equal ones,
> and the card tile lost the generic `.card` panel it used to sit in, so the QR and the card are now
> the same 190×148 box plus caption. Content peaks fell: **payment 523 → 477 (zh) / 503 (en)**, and
> **`?part=all` 2,811 → 2,765 (zh) / 2,927 → 2,878 (en)**. **Declared heights are unchanged** —
> 580 / 2880 / 2990 still cover the content with 77–112px of slack, so no CMS edit is needed and
> nothing can clip. The 20 Nov revision note below stays as the record of that pass.

> **Revised 20 Nov 2026 (client comment pass 2, `docs/CLIENT-COMMENTS-2-2026120.md`).** White ground,
> 56rem desktop column, the HK$100 floor, the months control removed (monthly is now a fixed 12 months),
> a positive saving figure and the client's own disclaimer. Every block moved, so **every number in §2 is
> reissued**: calc 1920 → 1800, input 1120 → 1040, result 920 → 890, pay 600 → 580, receipt 780 → 810
> (zh) / 890 → 910 (en). `?part=all` is new and is also the default for a bare `/embed/` URL: the whole
> journey is **2,811px zh / 2,927px en** at its tallest reachable state, which fits a single iframe. It is
> still a tall frame on a phone, so the four-block split stays the recommended production arrangement.


> **Added 15 Nov 2026 (EN build, `docs/EN-BUILD-20261115.md`).** The two languages are one file — `/embed/?part=pay&lang=en` — with one engine and two string tables. **The English block is taller at every width we measured**, and the phone is where it costs most: English copy runs ~35% more lines at 320px, because the column is ~288px and a sentence that fits one line in Chinese wraps to two. Peak Δ en−zh: calc **+347px**, input **+105** (its Chinese peak is at 1200px, not 320px), result **+172**, pay **+174**, receipt **+101**; at 1280px the same blocks are still +21…+83px. **Do not assume English is shorter anywhere — measure it.** If the English page reuses the Chinese heights, every block gets the inner scrollbar they reported on mobile.
>
> **Revised 15 Nov 2026 (tax engine fix, `docs/TAXFIX-20261115.md`).** The corrected engine renders a band's saving as a **range** (the band's floor and ceiling), and the calculator gained one collapsed exact-income row. Measured before → after: **`?part=calc` 1,499 → 1,590px**, **`?part=input` 767 → 832px**, **`?part=result` 706 → 732px**. The table above carries 60–70px of slack on each, in line with the original derivation.
>
> **Revised 15 Nov 2026 (client meeting C4).** The previous table said input 1000 / result 750 / pay 1100 / receipt 650 and carried **no number for `?part=calc`**. Two blocks were overflowing the numbers in use:
> Measured at 320px, before → after that revision: **`?part=pay` 1,068px → 970px** (it was 28px taller than the 1,040px frame in use), and **`?part=calc` 1,394px → 1,499px** — 374px taller than a 1,020px frame before the new C2/C6 copy, and ~480px taller now. An iframe whose content is taller than its declared height grows its *own* scrollbar inside the page's scroll; that is the double scrollbar reported on mobile. It was never a rendering bug — a fixed height plus taller content can only produce one.
>
> **If the client embeds `?part=calc` for the calculator step, 1,020px cannot work.** Either set 1,650px (zh-HK) / 2,000px (en), or split it into `?part=input` + `?part=result`, which is the arrangement the four-block design was built for and which gives a shorter first block.

Why more than one block rather than one tall frame: with a mandatory height, one embed means either a 3,700px block (absurd) or an internal scrollbar inside a 900px box — and a nested scroll container on a phone is where QR donations die. Separate blocks let the **page** scroll, which every donor already knows how to do. `qa/poc_test.py` asserts each block stays inside its declared height at 328, 568, 944 and 1280px, so the table cannot silently drift.

Each block is **stateless**. The QR is amountless and the payment copy does not print the donor's figure, so nothing has to travel between frames — no relay script, no donor amount crossing an origin boundary.

**If the component can take a different height per breakpoint**, or accepts a CSS value instead of an integer (`min(1100px, 95vh)`), say so: this pair removes the remaining vertical slack on desktop, where one number for all widths leaves ~200px of white space at the foot of the calc block:

| Block | Mobile (frame ≤480px) | Tablet/desktop (≥568px) |
|---|---|---|
| Calculator + result · zh-HK | 1656 | 1639 |
| Calculator + result · en | 1962 | 1748 |
| Payment · zh-HK | 628 | 618 |
| Payment · en | 739 | 675 |
| All in one · zh-HK | 2121 | 2160 |
| All in one · en | 2482 | 2317 |
| Receipt · both | 60 | 60 |

(the English receipt block peaks at 468px above 568px, so a breakpoint pair gives it back 260px of dead space — the largest single win of the two-language build)

### Required iframe attributes

```html
<iframe
  id="fhf-part-1"
  src="https://<host>/embed/?part=input&lang=en"
  title="Donation tax calculator"
  scrolling="no"
  style="width:100%;border:0;height:1000px"
  loading="lazy"></iframe>
```

For the Chinese page the same block is `?part=input` (or `&lang=zh-HK`) with `title="慈善捐款扣稅計算機"` and `height:900px`. **The height is not interchangeable between the two** — see the table in §2.

### Must not be set

| Attribute / value | Why it breaks |
|---|---|
| `sandbox` without `allow-top-navigation-by-user-activation` | The credit-card rail and the wallet app-open cannot leave the frame — §6 |
| `sandbox` without `allow-scripts` | The calculator does not run at all |
| `allow` missing `payment` | Future payment surfaces are blocked by Permissions Policy |
| `X-Frame-Options: DENY/SAMEORIGIN` on **our** response | Nothing renders (we send no XFO; do not add one) |
| `CSP: frame-ancestors` not including `hollows.org` | Same as above — must list `https://www.hollows.org` and the staging hostname |
| a height **shorter than the table in §2** | The content is taller than the frame. With `scrolling="no"` it is clipped and unreachable; with `scrolling="auto"` the frame grows its own scrollbar inside the page's scroll — the double scrollbar reported on mobile. Use the §2 numbers with `scrolling="no"`. |
| `loading="eager"` on a long page | Delays LCP for no reason |

### If the CMS component sets `sandbox`, it must be exactly

```
allow-scripts allow-same-origin allow-popups allow-top-navigation-by-user-activation allow-forms
```

`allow-popups` covers the IPG Pay card popup; `allow-top-navigation-by-user-activation` covers the wallet deep links. Without the second one, mobile donors see nothing happen and leave.

---

## 3 · Auto-height (optional now — the component requires a number)

The parts are sized by the table in §2. **You do not need any script.** If the component later allows auto-height, this is the only integration code it takes — a seven-line listener that applies the height the widget reports:

```html
<script>
window.addEventListener("message", function (e) {
  if (e.data && e.data.source === "fhf-taxcalc" && e.data.type === "resize") {
    var f = document.getElementById("fhf-part-1");     // ← your iframe id
    if (f && f.contentWindow === e.source) f.style.height = e.data.height + "px";
  }
});
</script>
```

- **Without it:** the widget still works, inside a fixed-height frame with an internal scrollbar. Acceptable fallback, measurably worse.
- **With it:** no internal scrollbar, ever, at any width. Heights are re-posted on input, on mode change, on validation messages, on font load and on window resize.
- The listener checks `e.source` — do not drop that line, it prevents another frame on the page from resizing this one.

---

## 4 · Message contract

### Widget → host

| `type` | Payload | When |
|---|---|---|
| `ready` | `{height, contract:1, v, lang}` | once, on boot |
| `resize` | `{height, fixed:boolean, lang}` | whenever the content height changes (deduped ≥1px) |
| `event` | `{name, params}` — `params.lang` | the eight analytics events, §5 |
| `deeplink` | `{rail, phase:"attempt"\|"result", blocked, reason?}` | wallet app-open test |
| `pong` | `{height, lang}` | reply to `fhf-ping` |

Every message carries `source:"fhf-taxcalc"`, `v:"1.3.0"` and `lang:"zh-HK"|"en"`. **Filter on `source` — this is the whole contract.**

### Host → widget

| `type` | Payload | Effect |
|---|---|---|
| `fhf-config` | `{config:{height:"auto"\|number, reveal:"#id", lang:"zh-HK"\|"en"}}` | switch height mode / scroll to a step / **switch language in place** |
| `fhf-consent` | `{marketing:boolean}` | stored, applied to any future non-essential call |
| `fhf-ping` | `{}` | health/height probe |

The widget never assumes a parent exists. Framed or standalone, it behaves identically.

### Language

One file, one engine, two authored string tables. The language is chosen by `?lang=`, defaulting to `zh-HK`:

| URL | Build |
|---|---|
| `/embed/?part=pay` | Traditional Chinese (HK) — the delivered build |
| `/embed/?part=pay&lang=zh-HK` | identical to the above |
| `/embed/?part=pay&lang=en` | English |

- **`?lang=en` is the only difference between the two builds.** The tax engine, the 35% cap, the exact-income path, the payment rails, the receipt capture and the event payloads are the same bytes — `qa/test_tax_engine.py` fails if a locale string ever appears inside the engine block.
- **Switching language must not re-load the frame.** Send `{type:"fhf-config", config:{lang:"en"}}`; the widget swaps every string in place, sets `<html lang>`, re-renders and re-posts its height. **Never change `iframe.src` to switch language** — `ready → apply() → src → ready` is the infinite-reload loop (see §10 of the project skill).
- **`<html lang>` follows the language** (`zh-Hant-HK` / `en`). A host that hard-codes a `lang` on the frame does not break it, but a screen reader inside the frame reads the widget's own value.
- **Alt text, `aria-label`, `<option>` text and placeholders are translated too** — not just the visible paragraphs. `qa/lang_parity.py` fails on any CJK character left anywhere in the English DOM.
- **The receipt and disclaimer text is legally reviewed per language.** The Chinese and English versions are structurally identical (same elements, same placement, same always-visible `<ol>` of five — the disclaimer is no longer a collapsed disclosure) so one legal review covers both shapes; the client's approved wording is pinned by `qa/lang_parity.py` and the earlier draft lives at `docs/disclaimer-draft.md`.

---

## 5 · Measurement — exactly eight events, coarse-band only

The widget does **not** load GTM. It posts events; the host pushes them into its own container (`GTM-P3Q6PF55` on hollows.org). One container, one consent model, one GA4 property.

| Event | Params |
|---|---|
| `calc_started` | `page_location` |
| `calc_result_shown` | `band` (`band`/`unknown`), `donation_type`, `exact`, `cap_state` |
| `qr_view` | `rail`, `state` (`desktop`/`mobile`) |
| `rail_click` | `rail`, `state` |
| `email_capture` | `donation_type`, `state` |
| `receipt_request` | `method`, `has_reference` |
| `receipt_fulfilled` | `method` — backend, not the widget |
| `donation_self_report` | `rail`, `state` |

Every event additionally carries **`lang` (`zh-HK` | `en`)**, the language of the build that fired it. It is a dimension in the same sense as `band` and `state` — a label, never a value — and it was added because the payload schema already carried dims and the two builds are otherwise indistinguishable in a report. **It needs a 7th GA4 custom dimension (Event scope, name `lang`) or it reads as `(not set)`, which looks like a widget bug** (skill §10h). `ops/provision-ga-gtm.py` carries it.

**Hard invariant:** no amount, no income, no marginal rate ever appears in a payload. `band` is a coarse bucket label, never a number. An automated test fails the build if `amount`, `income`, `rate` or a gift value appears — `qa/poc_test.py` asserts it for Chinese, `qa/lang_parity.py` for both languages.

### The one tag the host adds

A **Custom HTML** tag in GTM, fired on **All Pages**, that pushes what the widget says:

```html
<script>
window.dataLayer = window.dataLayer || [];
window.addEventListener("message", function (e) {
  var d = e.data;
  if (!d || d.source !== "fhf-taxcalc") return;
  if (d.type === "resize" || d.type === "ready" || d.type === "pong") return;
  if (d.type === "deeplink") {
    dataLayer.push({event:"fhf_deeplink_test", rail:d.rail, phase:d.phase, blocked:!!d.blocked});
    return;
  }
  if (d.type === "event") dataLayer.push(Object.assign({event:d.name}, d.params || {}));
});
</script>
```

Then one GA4 Event tag per event name (or a single tag with `{{Event}}` as the event name), plus a GA4 Configuration tag. No other integration exists.

---

## 6 · Payments — what the iframe can and cannot do

| Rail | Mechanism | Iframe behaviour |
|---|---|---|
| **AlipayHK** | static merchant QR, donor scans or saves the image, enters the amount in the app | Works. QR is an `<img>`; long-press save works on iOS/Android inside a frame |
| **Credit card** | `<a href="https://www.hollows.org/zh-Hant-HK/donate/" target="_top">` | **Must leave the frame.** With no `sandbox`, `target="_top"` always works. With `sandbox`, it needs `allow-top-navigation-by-user-activation` |
| Wallet **app open** (deep link) | `alipays://` | **Unreliable inside any iframe.** iOS Safari blocks custom schemes from a subframe; Chrome needs a user gesture and often a top-level navigation. This is why the QR is the primary path, not the deep link |

PayMe was **dropped from the page on 21 Nov 2026** on Kevin's instruction; its
`assets/logos/payme.png` is left on disk, unreferenced, so a revert is one markup block rather than a
re-crop. The two remaining rails are the QR (desktop) and the tap-through row (phone).

**Desktop (≥720px)** is two tiles sized by function (Option B, 24 Nov 2026): the AlipayHK tile is the
wide one and carries the QR, the name, the scan line and the receipt note with its `?`; the credit-card
tile is compact and carries the glyph, the name and the destination on a ruled foot line. Each tile is
**click-anywhere** — the tile itself is a `<div>` and its own `<a>` stretches over it with `::after`,
because the receipt note holds a `<button>` and a button may not be nested inside an `<a>`. The QR is
**`assets/logos/alipayhk-qr.png`**, the tight 264×264 crop (the code plus the spec's 4-module quiet
zone) rendered at 190px; the published 450×350 card put the same code at ~90px, which no scanner reads.
**Phone (<720px)** has no QR at all — a donor cannot scan the screen they are holding — so the same two
destinations are rows, with the receipt note between them.

The widget posts a `deeplink` message **before** attempting navigation (only if a host ever adds a
`data-deeplink` control — the POC bench that used it is stripped), because a successful app-open
destroys the page that would have reported it. Absence of the follow-up `result` message is the
success signal.

---

## 7 · Security, privacy, data

- The widget sets **no cookies, no localStorage, no sessionStorage** on the host's origin. All state is in memory. Third-party storage partitioning (Safari ITP, Chrome) therefore cannot break it.
- Receipt capture in production **POSTs to our endpoint over HTTPS**; the widget holds no persistence. Donor name + email are the only PII, collected with an explicit consent checkbox, under a PDPO notice rendered **inside** the widget (the host site currently has no consent platform, so nothing else supplies it).
- We send `Content-Security-Policy: frame-ancestors https://www.hollows.org https://<staging-host>` and **no** `X-Frame-Options`.
- No client credentials, no merchant secrets, no API keys are ever placed in the widget. Merchant QR images are static public assets.
- If the host later adds a CSP, our origin must be listed in `frame-src` / `child-src`; if the host adds a consent platform, pass the state via `fhf-consent`.

---

## 8 · Failure behaviour

| Failure | What the donor sees |
|---|---|
| Widget JS blocked / 404 | The host's own fallback link to `hollows.org/donate` — the CMS component should include one |
| Host never applies resize | Widget renders in a fixed frame with an internal scrollbar; everything still works |
| GTM listener tag missing | Nothing breaks visually; measurement is dark — **this is a launch gate, not a nice-to-have** |
| Deep link blocked | Inline message: use the QR |

---

## 9 · Browser matrix to sign off

iOS Safari 17/18 · Android Chrome 12x · Samsung Internet · macOS Safari · Chrome · Edge · Firefox — at 390 / 768 / 1024 / 1440 px. The harness covers the last four widths; the two real devices have to be tested by hand, and iOS Safari is the one that decides the payment path.

---

## 10 · Hosting — the one open decision

| Option | What it means | Verdict |
|---|---|---|
| **A. Same-origin path on hollows.org** (reverse proxy or a static app under `/taxcalc/`) | No third-party domain inside the donation page; storage/cookies/ITP irrelevant; no postMessage needed for analytics; no ongoing dependency on us | **Preferred.** Asked of their infra team; the cheapest long-term |
| **B. Our subdomain in the CMS iframe** | Ships fastest, works today (this POC runs this way); needs the CSP line, the listener tag, and a hosting line item for the client | Acceptable |
| **C. A C# block inside Optimizely** | Best fidelity, needs their repo/CI/release cadence | Phase 2, priced separately |
