# Setup guide — GA4 + GTM for the FHF tax-calculator blocks

**Who this is for:** whoever sets this up under **2SK's own Google account** (not the client's).
**Time:** 35–45 minutes, once. No code, no publish on the client side.
**Why we own it:** we have view-only access to the client's GA/GTM, and the bridge tag would have to run on their page. We can't touch it, so the container runs inside our block instead, and we grant them viewer access to our property.

Read §11 before you start — it explains what this configuration can and cannot measure, and it changes how the numbers get reported.

---

## 0 · Before you start

| You need | Notes |
|---|---|
| A Google account **outside the client's org** | Use `2skdigitals@`. If the account is inside a Fred Hollows/Zoom/partner org, consent screens will block you — as they already did with the client's OAuth client |
| Admin on the GA4 account you create | You're creating a new one, so you are the admin |
| Admin on the GTM account you create | Same |
| The four block URLs | `…/embed/?part=input` · `result` · `pay` · `receipt` |

Two things you do **not** need: the client's GTM container, or any change to hollows.org.

---

## 1 · Create the GA4 property

1. Go to **analytics.google.com** and sign in as `2skdigitals@`.
2. Bottom-left **Admin** (gear icon).
3. In the **Account** column: **Create → Account**.
   - Account name: `2SK Solutions`
   - Tick the data-sharing boxes (harmless, and it enables benchmarking later)
   - Next.
4. **Create property**:
   - Property name: `FHF Tax Calculator POC`
   - Reporting time zone: **(GMT+08:00) Hong Kong Time**
   - Currency: **Hong Kong Dollar (HKD)**
   - Next → industry **Other**, business size **Small** → Next.
   - Business objectives: pick **Examine user behaviour** (any choice works; it only pre-fills reports) → **Create**.
5. **Data collection → Web**:
   - Website URL: `https://2skdigitals.github.io/fhf-taxcalc-poc/`
   - Stream name: `POC blocks`
   - **Create stream**.
6. On the stream details panel, copy the **Measurement ID**: `G-XXXXXXXXXX`. Write it down — you need it in §5 and §6.

> Skip the "Install with Google tag" panel. GTM will install it, in §5.

---

## 2 · Create six custom dimensions

GA4 records event parameters whether or not the dimension exists — but **without it you cannot read them in reports**. Do this *before* the first traffic, or values land as `(not set)`.

**Admin → Custom definitions → Custom dimensions → Create custom dimension**, six times:

| Dimension name | Scope | Event parameter |
|---|---|---|
| Rail | Event | `rail` |
| Device state | Event | `state` |
| Donation type | Event | `donation_type` |
| Income band | Event | `band` |
| Cap state | Event | `cap_state` |
| Host page | Event | `host_page` |

Spelling matters — these are the exact keys the widget sends. Dimensions take up to 24 h to appear in reports; collection starts immediately.

---

## 3 · Create the GTM container

1. Go to **tagmanager.google.com**, same account.
2. **Create Account**:
   - Account name: `2SK Solutions`
   - Country: **Hong Kong**
   - Share data with Google: tick → Continue.
3. **Container setup**:
   - Name: `fhf-taxcalc-poc`
   - Target platform: **Web**
   - **Create** → accept the terms.
4. Copy the **Container ID**: `GTM-XXXXXXX`.

> Do **not** paste the two `<script>` snippets GTM offers into anything. Our block loads the container itself (§7).

---

## 4 · Six data-layer variables

**Variables → New → Data Layer Variable**, six times. Name them exactly, and set *Data Layer Variable Name* to the parameter:

| Variable name | Data Layer Variable Name |
|---|---|
| `DLV - rail` | `rail` |
| `DLV - state` | `state` |
| `DLV - donation_type` | `donation_type` |
| `DLV - band` | `band` |
| `DLV - cap_state` | `cap_state` |
| `DLV - host_page` | `host_page` |

Leave *Data Layer Version* on **2**.

---

## 5 · One trigger

**Triggers → New → Trigger Configuration → Custom Event**

- Trigger name: `CE — FHF widget events`
- This trigger fires on: **Some Custom Events**
- Event name: **matches RegEx** (use the dropdown, not "equals")
- Value:

```
^(calc_started|calc_result_shown|qr_view|rail_click|email_capture|receipt_request|receipt_fulfilled|donation_self_report)$
```

- **Save**.

One trigger for all eight events. Do not create eight.

---

## 6 · Two tags

### 6a · Google Tag (the GA4 configuration)

**Tags → New → Tag Configuration → Google Analytics → Google Tag**

- Tag name: `GA4 — config`
- Tag ID: `G-XXXXXXXXXX` (from §1)
- **Configuration settings → Fields to set → Add row**:
  - Field name: `page_location`
  - Value: `{{DLV - host_page}}`
- Triggering: **Initialization – All Pages**

Why the field override matters: the Google Tag is running *inside our iframe*, so GA4 would otherwise record every hit as `2skdigitals.github.io/…`. This makes the reports show the real hollows.org page (taken from `document.referrer` inside the frame).

- **Save**.

### 6b · GA4 Event (the eight events)

**Tags → New → Tag Configuration → Google Analytics → Google Analytics: GA4 Event**

- Tag name: `GA4 — FHF widget event`
- Measurement ID: `G-XXXXXXXXXX`
- Event Name: type `{{` and choose the built-in **Event** variable → `{{Event}}`
- **Event Parameters → Add row**, five times:

| Parameter name | Value |
|---|---|
| `rail` | `{{DLV - rail}}` |
| `state` | `{{DLV - state}}` |
| `donation_type` | `{{DLV - donation_type}}` |
| `band` | `{{DLV - band}}` |
| `cap_state` | `{{DLV - cap_state}}` |

- Triggering: **CE — FHF widget events** (from §5)
- **Save**.

> `{{Event}}` is a built-in variable. Do not create a data-layer variable for it — that's the mistake this setup most often hits.

---

## 7 · Publish, then wire the four blocks

1. Top right **Submit → Publish Version** → name it `POC v1` → **Publish**.
2. Add `&gtm=GTM-XXXXXXX` to each block URL:

| Block | URL | Height |
|---|---|---|
| Calculator | `…/embed/?part=input&gtm=GTM-XXXXXXX` | 1000 |
| Result | `…/embed/?part=result&gtm=GTM-XXXXXXX` | 750 |
| Payment | `…/embed/?part=pay&gtm=GTM-XXXXXXX` | 1100 |
| Receipt | `…/embed/?part=receipt&gtm=GTM-XXXXXXX` | 650 |

3. Paste these into the four CMS components. That is the entire client-side change — **none of it is on their page's code**, only in the iframe `src` field of the component they already built.

---

## 8 · Verify (15 minutes)

Work in this order — each step isolates one layer.

**8.1 · The block itself.** Open `…/embed/?part=input&debug=1&gtm=GTM-XXXXXXX` directly.
Open DevTools → Console. Type an amount. You must see `[fhf-taxcalc] calc_started {…}` and `calc_result_shown`. If not, the problem is the widget, not GA.

**8.2 · dataLayer.** In the same console: `window.dataLayer`. Expect `fhf_init` (with `host_page`), `gtm.js`, then your events. If `fhf_init` is missing, the container never loaded — check the ID.

**8.3 · GTM received it.** In GTM, **Preview** → *Tag Assistant* → enter the **block URL** (not the client's page) → connect. Interact. The Custom Event trigger should record `calc_started`, and both tags should show as **Fired**.

**8.4 · GA4 received it.** **GA4 → Admin → DebugView**. Interact with the block again. Events appear within seconds, with their parameters attached.

**8.5 · Realtime.** GA4 → Reports → Realtime. Events show within ~60 s of ordinary traffic.

**8.6 · No amounts, ever.** Open any event in DebugView and check its parameters: `band` must be `band`/`unknown`, never a number. If a figure appears, stop — that is a build regression, and the automated test (`qa/poc_test.py`) would have failed before it shipped.

**8.7 · Our own harness, if you want a second opinion.** `…/fhf-taxcalc-poc/events/` runs the bridge on a page we control and shows every payload with an honesty check.

---

## 9 · Grant the client viewer access

**GA4:** Admin → **Property access management** → blue **+** → *Add users*
- Email: the address they give us (e.g. `hkinfo@hollows.org` plus the marketing lead)
- **Viewer** only. Do not grant Editor or Marketer.
- Untick "Notify new users by email" if you want to tell them yourself.

**GTM:** Admin → **User Management** (container level) → **+** → *Add new user*
- Same addresses
- **Container permissions: Read** — *not* Publish
- Save.

What they can then see: our property's reports and DebugView (read), and our container's configuration (read, no changes). They cannot alter tags or the property.

---

## 10 · Optional: automate it next time

If we want the API route instead of clicking, it needs a Google Cloud project **we** own — the one already in the repo (`fred-hollows-501315`) belongs to the client's org, which is why consent is blocked. New project under `2skdigitals@` → *APIs & Services* → enable **Google Analytics Admin API** and **Tag Manager API** → *OAuth consent screen* (External, Testing, add `2skdigitals@` as a test user) → *Credentials* → **OAuth client ID → Desktop app** → download the JSON to `~/2SK/fred-hollows/credentials/2sk-oauth-client.json`.

Then `ops/google-auth.py` runs against it and `ops/provision-ga-gtm.py` creates everything in this document — property, stream, dimensions, container, variables, trigger, three tags, published version — in about 40 seconds, idempotently.

---

## 11 · What this configuration measures — and what it does not

The container runs inside a third-party iframe. Browsers partition storage for that context (Safari ITP, Chrome's storage partitioning), so GA4's `client_id` fragments per page load.

| Measure | Reliable? |
|---|---|
| Event counts — `qr_view`, `rail_click`, `email_capture`, … | **Yes** |
| Event ratios — `rail_click ÷ calc_result_shown`, `email_capture ÷ qr_view` | **Yes** — both sides come from the same frame |
| Page attribution | **Yes** — via the `page_location` override in §6a |
| Device, geo, referrer | **Yes** |
| Users, sessions, new-vs-returning | **No.** Do not report these |
| Ad-blocked visitors | Missing, as in any GA4 property |

**The six Gate-2 KPIs are event ratios by definition**, so nothing in the success model depends on the unreliable rows. But if anyone asks "how many people used the calculator", the honest answer is "we can count the events, not the people" — until the day we host the page itself, when the container becomes first-party and this caveat disappears.

Two further limits worth saying out loud:

- **QR payments never report back.** GA4 sees the QR view and the rail click; it never sees the money. There is no webhook and no redirect from PayMe/AlipayHK. Any "revenue" number is unmeasurable by design.
- **`receipt_fulfilled` is backend-only.** It fires when ops marks a receipt as issued, not from the browser — it cannot be produced by this setup until Phase 1 ships.

---

## 12 · Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| No events in dataLayer, no console logs | container ID missing from the URL, or mistyped | check `&gtm=GTM-…` in the component's src |
| `fhf_init` present, events absent | the trigger regex doesn't match | compare against §5 exactly, including `^…$` |
| Tags fire in Preview, nothing in DebugView | wrong Measurement ID, or the Google Tag is not on **Initialization** | §6a |
| Every hit shows the embed URL as the page | `page_location` override missing | §6a, Fields to set |
| Dimension columns empty | custom dimension created after data arrived, or a typo in the parameter name | §2; re-collect |
| Each event counted twice | the container was added in two places | remove one |
| `band=unknown` on every row | the donor never picked an income bracket | correct behaviour, not a bug |
| A number appears in a parameter | defect | stop, report it — the test suite enforces the invariant |
