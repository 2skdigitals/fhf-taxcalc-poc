# Iframe contract — FHF tax calculator widget

Version **1.0.0** · POC · 2SK Solutions

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

Measured on the live widget at ten widths from 320px to 1440px. **Set exactly these numbers** and every block fits at every width, with no internal scrollbar.

| # | Block | URL | Height to set | Content range (320–1440px) |
|---|---|---|---|---|
| 1 | Calculator | `/embed/?part=input` | **1000px** | 800 – 990 |
| 2 | Result | `/embed/?part=result` | **750px** | 400 – 727 |
| 3 | Payment | `/embed/?part=pay` | **1100px** | 849 – 1068 |
| 4 | Receipt | `/embed/?part=receipt` | **600px** | 400 – 543 |

Why four blocks rather than one tall frame: with a mandatory height, one embed means either a 3,700px block (absurd) or an internal scrollbar inside a 900px box — and a nested scroll container on a phone is where QR donations die. Four short blocks let the **page** scroll, which every donor already knows how to do. `qa/poc_test.py` asserts each block stays inside its declared height at 390px and 1440px, so the table cannot silently drift.

Each block is **stateless**. The QR is amountless and the payment copy does not print the donor's figure, so nothing has to travel between frames — no relay script, no donor amount crossing an origin boundary.

**If the component can take a different height per breakpoint**, or accepts a CSS value instead of an integer (`min(1100px, 95vh)`), say so: that removes the remaining vertical slack on desktop (input 951px of content in a 1000px box) and we will hand you a two-number set instead.

### Required iframe attributes

```html
<iframe
  id="fhf-part-1"
  src="https://<host>/embed/?part=input"
  title="慈善捐款扣稅計算機"
  scrolling="no"
  style="width:100%;border:0;height:1000px"
  loading="lazy"></iframe>
```

### Must not be set

| Attribute / value | Why it breaks |
|---|---|
| `sandbox` without `allow-top-navigation-by-user-activation` | The credit-card rail and the wallet app-open cannot leave the frame — §6 |
| `sandbox` without `allow-scripts` | The calculator does not run at all |
| `allow` missing `payment` | Future payment surfaces are blocked by Permissions Policy |
| `X-Frame-Options: DENY/SAMEORIGIN` on **our** response | Nothing renders (we send no XFO; do not add one) |
| `CSP: frame-ancestors` not including `hollows.org` | Same as above — must list `https://www.hollows.org` and the staging hostname |
| `height` fixed without `scrolling="auto"` | Content clips silently on mobile |
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
| `ready` | `{height, contract:1, v}` | once, on boot |
| `resize` | `{height, fixed:boolean}` | whenever the content height changes (deduped ≥1px) |
| `event` | `{name, params}` | the eight analytics events, §5 |
| `deeplink` | `{rail, phase:"attempt"\|"result", blocked, reason?}` | wallet app-open test |
| `pong` | `{height}` | reply to `fhf-ping` |

Every message carries `source:"fhf-taxcalc"` and `v:"1.0.0"`. **Filter on `source` — this is the whole contract.**

### Host → widget

| `type` | Payload | Effect |
|---|---|---|
| `fhf-config` | `{config:{height:"auto"\|number, reveal:"#id"}}` | switch height mode at runtime; scroll to a step |
| `fhf-consent` | `{marketing:boolean}` | stored, applied to any future non-essential call |
| `fhf-ping` | `{}` | health/height probe |

The widget never assumes a parent exists. Framed or standalone, it behaves identically.

---

## 5 · Measurement — exactly eight events, coarse-band only

The widget does **not** load GTM. It posts events; the host pushes them into its own container (`GTM-P3Q6PF55` on hollows.org). One container, one consent model, one GA4 property.

| Event | Params |
|---|---|
| `calc_started` | `page_location` |
| `calc_result_shown` | `band` (`band`/`unknown`), `donation_type`, `cap_state` |
| `qr_view` | `rail`, `state` (`desktop`/`mobile`) |
| `rail_click` | `rail`, `state` |
| `email_capture` | `donation_type`, `state` |
| `receipt_request` | `method`, `has_reference` |
| `receipt_fulfilled` | `method` — backend, not the widget |
| `donation_self_report` | `rail`, `state` |

**Hard invariant:** no amount, no income, no marginal rate ever appears in a payload. `band` is a coarse bucket label, never a number. An automated test fails the build if `amount`, `income`, `rate` or a gift value appears — `qa/poc_test.py` asserts it.

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
