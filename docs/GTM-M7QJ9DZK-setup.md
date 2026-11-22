# GTM-M7QJ9DZK — wiring the calculator's events

**Container:** `GTM-M7QJ9DZK` (given by the client, 23 Nov 2026)
**Widget:** `https://2skdigitals.github.io/fhf-taxcalc-poc/embed/`

---

## Recommendation: the container goes on the page, not inside the frame

The widget is built to post its events out to the host page and let the host's container carry them. That is
deliberate, and loading GTM **inside** the iframe would cost three things:

| If GTM loads inside the iframe | Consequence |
|---|---|
| Consent | The host's CMP governs the page, not the frame. A container inside the frame fires outside that consent model — and the client's legal position depends on one model, not two. |
| Attribution | A hit fired from a cross-origin iframe reports the **iframe's URL** as `page_location`. Every event would land on `2skdigitals.github.io`, not on the campaign page, and would split the session from the page that earned it. |
| Duplication | The page will also load GTM-M7QJ9DZK. Two containers, two `dataLayer`s, one event reported twice — the classic double-count that is found six weeks later in a board deck. |

So: paste the client's standard GTM snippet on **the page that hosts the iframe**, and add the one Custom HTML
tag below. The widget needs no change and the eight events flow into GTM-M7QJ9DZK as normal events.

**If the page cannot carry GTM** (no access to the Optimizely template), say so — the widget can host the
container itself behind an explicit switch, guarded so it never double-fires. It is a fallback, not the
preferred arrangement.

---

## What to add in GTM-M7QJ9DZK

### 1 · One Custom HTML tag — fired on All Pages

```html
<script>
window.dataLayer = window.dataLayer || [];
window.addEventListener("message", function (e) {
  var d = e.data;
  if (!d || d.source !== "fhf-taxcalc") return;          // the whole contract
  if (d.type === "resize" || d.type === "ready" || d.type === "pong") return;
  if (d.type === "deeplink") {
    dataLayer.push({event:"fhf_deeplink_test", rail:d.rail, phase:d.phase, blocked:!!d.blocked});
    return;
  }
  if (d.type === "event") dataLayer.push(Object.assign({event:d.name}, d.params || {}));
});
</script>
```

### 2 · One GA4 Configuration tag — fired on All Pages

Point it at the property the client's reporting uses, and enable **Send to server container** only if they run one.

### 3 · One GA4 Event tag — fired on the Custom Event trigger

Trigger: **Custom Event**, event name matches regex:

```
^(calc_started|calc_result_shown|qr_view|rail_click|email_capture|receipt_request|receipt_fulfilled|donation_self_report)$
```

Event name: `{{Event}}`. Parameters mapping:

| Widget sends | GA4 parameter | Example |
|---|---|---|
| `band` | `band` | `band` or `unknown` — **a label, never a number** |
| `donation_type` | `donation_type` | `one-off` / `monthly` |
| `exact` | `exact` | `yes` / `no` |
| `cap_state` | `cap_state` | `under` / `capped` |
| `rail` | `rail` | `alipay` / `card` |
| `state` | `state` | `desktop` / `mobile` |
| `method` | `method` | `email` / `post` |
| `has_reference` | `has_reference` | `yes` / `no` |
| `lang` | `lang` | `zh-HK` / `en` |

### 4 · GA4 custom dimensions (Event scope)

Register these in GA4 or the parameters arrive but cannot be reported on:
`band`, `donation_type`, `exact`, `cap_state`, `rail`, `state`, `method`, `has_reference`, `lang`.
`lang` is the newest — without it the Chinese and English builds are indistinguishable and read as `(not set)`.

---

## The eight events

| Event | Fires when |
|---|---|
| `calc_started` | first interaction with the calculator |
| `calc_result_shown` | a result is rendered |
| `qr_view` | the payment panel enters the viewport |
| `rail_click` | a payment rail's link or button is clicked |
| `email_capture` | the donor submits an email |
| `receipt_request` | a receipt is requested |
| `receipt_fulfilled` | a receipt was issued (server-side) |
| `donation_self_report` | the donor indicates they have paid |

---

## QA checklist before it goes live

1. **GTM Preview** on the campaign page, iframe loaded → `calc_started` appears once, not twice.
2. Change the gift amount → `calc_result_shown` fires per result, `band` populated, no numeric income.
3. Open the payment panel → `qr_view`; click AlipayHK → `rail_click` with `rail=alipay`.
4. Submit a receipt request → `receipt_request` with `has_reference`.
5. Switch to English and repeat step 2 → `lang=en` on the event.
6. In GA4 DebugView, confirm `page_location` is the **campaign page**, not `2skdigitals.github.io`.
7. Search the outgoing payload for any amount or rate — there must be none. This is a contractual rule, and a
   build test already fails on it inside the widget.

---

## What the widget does not need

No GTM snippet, no `gtag.js`, no container ID in the embed. The iframe stays a passive page that describes
what happened; the host decides what to do with it.
