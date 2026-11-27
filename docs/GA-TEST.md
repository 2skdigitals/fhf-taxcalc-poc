# Testing GA4 / event tracking from the iframe

**The rule that governs everything here:** an iframe is a separate document. GA4 and GTM inside the host page **cannot see** anything happening inside our block. The widget posts messages; the host page has to push them into `dataLayer`. If that one tag is missing, measurement is dark — the page still works, nothing is recorded.

There is no clever alternative (no cookie sharing, no `gtag` cross-frame call, no GTM in the iframe). One bridge tag, on the host page, on All Pages.

---

## Status — 27 Nov 2026 (the media agency's report)

The agency reports **purchase tracking working, view tracking still to be verified.** That pairing is
normal and it does not mean the widget is broken: a donation *purchase* is a conversion they own end to
end (the payment lands on their side), while a *view* only exists if the bridge tag is firing AND the GA4
event is configured on their side. Two different owners, two different failure points.

Before anyone debugs the iframe, settle **which event "view" means** — the answer decides the next step:

| If "view" means… | Where it lives | How to confirm in 2 minutes |
|---|---|---|
| the campaign page being seen (`page_view`) | their GTM, not us | GA4 Realtime with the page open — a `page_view` row appears |
| the calculator result being shown (`calc_result_shown`) | our widget → their bridge tag | our `/events/` page must show it; then their GTM Preview on the live page |
| the QR panel being seen (`qr_view`) | our widget → their bridge tag | scroll block 3 with GTM Preview open |

- **If `page_view` is the one missing**, GTM/GA4 is misconfigured on their side and nothing in this repo
  can change it — it is their container, their tag.
- **If `calc_result_shown` / `qr_view` is missing**, run `qa/poc_test.py` first: it proves the widget emits
  all eight events. If our side is clean, the bridge tag is missing or firing on the wrong container
  (check `curl -sL <page> | grep -oE 'GTM-[A-Z0-9]+'` — a container id arriving in an email is a claim,
  not the page's state).
- **What to ask them for:** the event name they call "view", the GA4 property it should land in, and one
  screenshot of GA4 DebugView or GTM Preview with the page open. Without those three, "needs verification"
  cannot be closed from our side.

---

## Level 0 — what the widget actually sends

Exactly eight events, coarse-band only:

| Event | Params |
|---|---|
| `calc_started` | `page_location` |
| `calc_result_shown` | `band`, `donation_type`, `cap_state` |
| `qr_view` | `rail`, `state` |
| `rail_click` | `rail`, `state` |
| `email_capture` | `donation_type`, `state` |
| `receipt_request` | `method`, `has_reference` |
| `receipt_fulfilled` | `method` — backend, not the widget |
| `donation_self_report` | `rail`, `state` |

**Hard invariant:** no amount, no income, no marginal rate in any payload. `band` is a coarse label (`band` / `unknown`), never a number. If you ever see a figure in GTM Preview, that is a defect — stop.

---

## Level 1 — no tickets, 2 minutes: our verification page

`https://2skdigitals.github.io/fhf-taxcalc-poc/events/`

This page is a working host: it runs the exact bridge tag and shows every event with its payload. Scroll through the four blocks, type an amount, press a rail, submit the receipt form — the right-hand panel fills up.

- **Pass:** `calc_started` → `calc_result_shown` on the first keystroke, `qr_view` when block 3 enters the viewport, `rail_click` on each rail, `email_capture` + `receipt_request` on a valid submit, and the **Honesty check** reads `clean`.
- This proves the contract and the widget. It does **not** prove their container is wired.

---

## Level 2 — their live page, no GTM change: browser console

On `hollows.org/en-HK/campaigns/2024/tax-deduction/`, open DevTools → Console, paste:

```js
window.addEventListener("message", e => {
  if (e.data && e.data.source === "fhf-taxcalc") console.log("[fhf]", e.data.type, e.data);
});
```

Then interact with the block. You should see `ready`, `resize`, then `event` messages with `name` and `params`.

- **Pass:** events appear while the page itself has no tag — this proves the widget posts **from inside their component**, across origins, with their markup.
- **Fail (nothing at all):** the frame is sandboxed without `allow-scripts`, or a different URL is embedded.
- This is the cheapest way to settle "does the iframe talk to our page?" without touching GTM.

*(Tip: to see the widget's own side, add `?debug=1` to the block URL in the component — it logs every event to its own console and shows a small overlay.)*

---

## Level 3 — GTM Preview: prove the tag

Add **one** Custom HTML tag to their **staging** container, fired on **All Pages**:

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

Then create the trigger and tags (full click-path in `GTM-SETUP.md`):

1. Trigger **Custom Event**, name matches RegEx:
   `^(calc_started|calc_result_shown|qr_view|rail_click|email_capture|receipt_request|receipt_fulfilled|donation_self_report)$`
2. **GA4 Configuration** tag (their Measurement ID) on *Initialization – All Pages*.
3. **GA4 Event** tag: Event Name `{{Event}}`, parameters from Data Layer Variables `band`, `donation_type`, `rail`, `state`, `cap_state`.

Open **Preview**, load the page, interact.

- **Pass:** `calc_started` and `calc_result_shown` appear **as fired tags** on the Custom Event trigger, with the parameter table populated and no amounts.
- **Fail (Preview sees nothing):** the bridge tag is not on All Pages, or the page has a CSP blocking inline scripts (their site does not today).
- **Fail (event fires, GA4 tag does not):** the trigger name regex does not match — check the exact spelling, `calc_result_shown` not `calc_result`).

---

## Level 4 — GA4 DebugView: prove delivery

Publish to staging → open **GA4 → Admin → DebugView** → load the page → interact.

- Events appear within ~60 seconds with their parameters.
- Create the custom dimensions first (`rail`, `state`, `donation_type`, `band`, `cap_state`) or the parameters are recorded but unreadable in reports.

---

## What each level proves

| Level | Proves | Cost |
|---|---|---|
| 1 · Our events page | the widget posts the right events with the right payloads | 2 min, no access |
| 2 · Console on their page | it posts from inside **their** component, cross-origin, with their markup | 2 min, no ticket |
| 3 · GTM Preview | the bridge tag works and the triggers fire | one tag + publish to staging |
| 4 · GA4 DebugView | the data lands in the property correctly | one more publish |

---

## The failures worth knowing before you debug

| Symptom | Cause |
|---|---|
| Nothing in `dataLayer`, events visible in console | bridge tag missing, or not on All Pages |
| Events fire in Preview but never in GA4 | Measurement ID wrong, or the config tag is not on *Initialization* |
| Only `qr_view` and `rail_click` arrive, never `calc_*` | the calculator block was never touched — those two are scroll-driven |
| Duplicate events (each one twice) | the tag was added twice — once in the container and once hardcoded in the template |
| Values like `band=unknown` on every row | correct. The donor did not pick a bracket; that is the honest state, not a bug |
| A number appears in a payload | **defect.** Stop and report it; the invariant is enforced by test, so it means a build regression |
