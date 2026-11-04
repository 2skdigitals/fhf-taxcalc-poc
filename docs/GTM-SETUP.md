# GTM setup — 12 minutes, one container

**What this produces:** the POC's eight events landing in GA4 from inside the iframe, with the container owned by whoever serves the page.

Two paths. **B is faster** once someone has a browser session open — and it is the only one available while our Google account is not signed in.

---

## A · Path 1 — use the client's existing container (recommended for the POC)

Their page already loads **`GTM-P3Q6PF55`**. Nothing new is created; we add one tag and eight GA4 events.

1. **Admin → Container → Import Container** (or just create manually per §C).
2. In the bench (`/harness/`), paste `GTM-P3Q6PF55` into the GTM field and press **Load GTM**.
3. Until the listener tag below is published, the bench's **dataLayer** panel still proves the widget is posting correctly — that is the actual POC assertion. GA4 delivery is the confirmation.

**Do not** add this to `GTM-NMN949KQ` (the retired eye-care.today container). It no longer serves any live page.

---

## B · Path 2 — create our own container + GA4 property

Requires a signed-in Google session (2skdigitals@). Click-path, no shortcuts:

1. `tagmanager.google.com` → **Create Account** → name `2SK Solutions` → country Hong Kong → **Continue**.
2. Container name `FHF Tax Calculator POC` → target platform **Web** → **Create** → accept the terms.
3. Copy the container ID (`GTM-XXXXXXX`).
4. `analytics.google.com` → **Admin → Create → Property** → name `FHF Tax Calculator POC` → timezone Hong Kong, currency HKD → **Next** → industry *Non-profit*, business size *Small* → **Create** → platform **Web** → stream URL `https://2skdigitals.github.io/fhf-taxcalc-poc/` → **Create stream**.
5. Copy the **Measurement ID** (`G-XXXXXXXXXX`).

---

## C · The four things that go in the container

### C1 · Custom HTML tag — the bridge (fires on All Pages)

Tag name: `FHF — widget bridge` · Trigger: **All Pages**

```html
<script>
window.dataLayer = window.dataLayer || [];
window.addEventListener("message", function (e) {
  var d = e.data;
  if (!d || d.source !== "fhf-taxcalc") return;
  if (d.type === "deeplink") {
    dataLayer.push({event:"fhf_deeplink_test", rail:d.rail, phase:d.phase, blocked:!!d.blocked});
    return;
  }
  if (d.type !== "event") return;
  dataLayer.push(Object.assign({event:d.name}, d.params || {}));
});
</script>
```

This is the **only** thing that makes iframe analytics work. Without it the widget is silent to GTM — by design: the widget never loads a container of its own.

### C2 · Data Layer Variables (five)

| Variable name | Data Layer Variable name |
|---|---|
| `DLV - band` | `band` |
| `DLV - donation_type` | `donation_type` |
| `DLV - rail` | `rail` |
| `DLV - state` | `state` |
| `DLV - cap_state` | `cap_state` |

### C3 · Trigger — one Custom Event covers all eight

Trigger name `CE — FHF widget events` · Event name matches RegEx:

```
^(calc_started|calc_result_shown|qr_view|rail_click|email_capture|receipt_request|receipt_fulfilled|donation_self_report)$
```

### C4 · GA4 tags

- `GA4 — config` : Google Tag, Measurement ID `G-XXXXXXXXXX`, trigger **Initialization – All Pages**.
- `GA4 — FHF widget event` : GA4 Event tag, **Event Name = `{{Event}}`**, parameters `band`, `donation_type`, `rail`, `state`, `cap_state` mapped from the DLVs, trigger `CE — FHF widget events`.

`{{Event}}` is a built-in variable — do not create a DLV for it, that is the mistake this setup usually hits.

---

## D · Verify before saying it works

1. **Preview** mode on the host page → load the widget → type an amount.
2. `calc_started` and `calc_result_shown` must appear as fired events on the Custom Event trigger.
3. Open any event → the parameter list must contain **no amount, no income, no rate**. If it does, the widget has a bug — stop.
4. GA4 → **Admin → DebugView** → the same events, same parameters.
5. Realtime should show the events within ~60 s of publish.

**Fail signatures:** events fire in Preview but never reach GA4 → the Measurement ID is wrong, or the config tag's trigger is not Initialization. Nothing fires at all → the bridge tag is not on All Pages, or the iframe is cross-origin with a `sandbox` that strips `allow-scripts`.

---

## E · What is still missing after this

| Item | Owner |
|---|---|
| The four **real** events in production (`receipt_fulfilled`, `donation_self_report` server-side) | our backend, Phase 1 |
| Consent state → `fhf-consent` message | whoever adds a CMP to hollows.org |
| GA4 custom dimensions for `rail`, `state`, `donation_type`, `band` | GA4 admin, one minute, needed or the parameters are unusable in reports |
