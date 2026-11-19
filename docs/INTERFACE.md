# Iframe contract — FHF tax calculator widget

Version **1.1.0** · POC · 2SK Solutions

Everything the host page (Optimizely CMS) must do, and everything the widget promises.
If a line here is wrong, the build is wrong — this document is the boundary between the two teams.

---

## 1 · What the widget is

| It is | It is not |
|---|---|
| The interactive calculator (amount, band, months → estimate) | The page hero, promo banner, FAQ or any editorial copy |
| The three payment rails + QR display | A payment processor (the money moves inside PayMe / AlipayHK) |
| The receipt-request capture form | The receipt generator / CRM (that is the backend, Phase 1) |
| A postMessage event source for the host's GTM | An analytics implementation of its own |

The host page owns: page copy, SEO, schema, GTM container, consent, navigation, footer, and the CMS iframe component itself.

---

## 2 · The component requires a height — so the page ships as four blocks

Measured by `qa/sweep_heights.py` at **22 widths from 320px to 1440px**, per language, taking the peak and adding 45–70px of slack. **Set the number for the language you are embedding** and every block fits at every width, with no internal scrollbar.

| # | Block | URL | Height · zh-HK | Height · en | Content peak zh-HK | Content peak en |
|---|---|---|---|---|---|---|
| 1 | Calculator + result | `/embed/?part=calc` | **1840px** | **1880px** | 1782 (at 944px, monthly) | 1823 (at 320px, monthly) |
| 1a | Calculator only | `/embed/?part=input` | **1190px** | **1190px** | 1137 (at 944px, monthly) | 1137 (at 944px, monthly) |
| 1b | Result only | `/embed/?part=result` | **860px** | **860px** | 808 (at 944px) | 808 (at 944px) |
| 2 | Payment | `/embed/?part=pay` | **550px** | **550px** | 502 (at 320px) | 502 (at 320px) |
| 3 | Receipt | `/embed/?part=receipt` | **780px** | **890px** | 724 (at 320px) | 830 (at 320px) |

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
| Calculator + result · zh-HK | 1650 | 1450 |
| Calculator + result · en | 2000 | 1500 |
| Payment · zh-HK | 1040 | 900 |
| Payment · en | 1210 | 900 |
| Receipt · en | 1030 | 790 |

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

Every message carries `source:"fhf-taxcalc"`, `v:"1.1.0"` and `lang:"zh-HK"|"en"`. **Filter on `source` — this is the whole contract.**

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
- **The receipt and disclaimer text is legally reviewed per language.** The Chinese and English versions are structurally identical (same elements, same placement, same collapsed `<details>`) so one legal review covers both shapes; the wording is `docs/disclaimer-draft.md`.

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
| **PayMe** | static merchant QR, donor scans or saves the image, enters the amount in the app | Works. QR is an `<img>`; long-press save works on iOS/Android inside a frame |
| **AlipayHK** | same | Works |
| **Credit card** | `<a href="https://www.hollows.org/zh-Hant-HK/donate/" target="_top">` | **Must leave the frame.** With no `sandbox`, `target="_top"` always works. With `sandbox`, it needs `allow-top-navigation-by-user-activation` |
| Wallet **app open** (deep link) | `payme://`, `alipays://` | **Unreliable inside any iframe.** iOS Safari blocks custom schemes from a subframe; Chrome needs a user gesture and often a top-level navigation. This is why the QR is the primary path, not the deep link |

The widget posts a `deeplink` message **before** attempting navigation, because a successful app-open destroys the page that would have reported it. Absence of the follow-up `result` message is the success signal.

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
