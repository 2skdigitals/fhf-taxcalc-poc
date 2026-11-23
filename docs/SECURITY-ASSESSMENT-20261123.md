# FHF HK tax calculator — security assessment

Widget: `embed/index.html`, 1,780 lines. Deployed copy verified byte-identical to
local (`shasum -a 256` → `5aa40244…5427` for both, https://2skdigitals.github.io/fhf-taxcalc-poc/embed/index.html).
Assessment only — no file in `embed/` was modified.

---

## Part A — the widget as it stands

### A1. Input handling

| Field | Line | type / autocomplete / maxlength / pattern | Validated against | What happens to the value |
|---|---|---|---|---|
| `#gift` donation | 570 | `text`, `inputmode=numeric`, `autocomplete=off`, **no maxlength, no pattern** | `digits()` at 1144 — strips non-digits, clamps to 0–99,999,999 | `st.amount`; formatted back into the input (1530); used only in arithmetic |
| `#exact` income | 613 | `text`, `inputmode=numeric`, `autocomplete=off`, no maxlength/pattern | same `digits()` clamp | `st.exact`; arithmetic only; **never transmitted** (comment 1556–1558) |
| `mode` radio | 563–564 | `radio`, enumerated values | value whitelist by markup | `st.mode`; pushed to analytics as `once`/`monthly` |
| `band` radio + `#band-mobile` | 582–594 | radios / `select`, enumerated | enumerated options; `BANDS[st.band]` lookup | `st.band`; **not** transmitted — event sends the literal string `"band"` (1513) |
| `#rname` | 714 | `text`, `autocomplete=name`, no maxlength/pattern/required | `trim().length >= 2` (1678) | length check only, then discarded |
| `#rmail` | 719 | `type=email`, `autocomplete=email`, no maxlength/pattern/required | regex `^[^\s@]+@[^\s@]+\.[^\s@]{2,}$` (1679) | regex only, then discarded |
| `#rref` | 731 | `text`, `autocomplete=off`, no maxlength/pattern | `trim()`, whitespace collapse `/\s+/g→" "`, length 4–40 (1676, 1680) | length + emptiness only; `has_reference: yes/no` transmitted (1689) |
| `#consent` | 766 | `checkbox`, no `required` (form is `novalidate`, 710) | `.checked` (1681) | gate only; never stored or transmitted |

Form has **`novalidate`, no `action`, no `method`, no `enctype`** (verified in browser:
`{"novalidate":true,"action":null,"method":null,"enctype":null}`). `preventDefault()` at 1670,
and the handler never assigns any field value to a sink.

**Does any user-controlled string reach `innerHTML`, an attribute, a URL, or `postMessage`?**

No, in every case:

- `1129` `innerHTML = t(key)` — `t()` (1113–1119) resolves **only** against the static `I18N`
  dictionary. On a miss it returns the key itself (1116), which came from a developer-authored
  `data-i18n-html` attribute. No runtime value is ever passed as the second argument at any
  call site of `applyLang`.
- `1335` debug height readout — `"<b>" + V + "</b> h=" + lastH` (version string + integer).
- `1395` net figure — `fmt(annual)` where annual derives from `digits()`; `fmt` is
  `Math.round(n).toLocaleString("en-US")` (1141) ⇒ digits and separators only.
- Attributes: `placeholder`/`aria-label`/`alt` (1130–1132) are set from the same static dictionary.
- URLs: no field value reaches `href`, `src`, `location`, or `window.open`. The only
  dynamic URL is `gs.src` (1764), built from a regex-constrained GTM id (see A2).

**Stored or DOM XSS from a field: not reachable.** The sink set is three `innerHTML`
assignments, all fed from compile-time constants or clamped integers. There is no
`eval`, `new Function`, `document.write`, `insertAdjacentHTML`, `outerHTML`, or `setAttribute`
with a user value. I could not construct a path from any input to a parser call.

Residual notes, not XSS:
- Fields persist in the DOM after the "successful" submit (verified: values still readable),
  so PII survives in the frame until navigation, and back/forward-cache restore can repopulate it.
- `autocomplete=name` / `autocomplete=email` invite the **browser** to store the donor's name and
  email in its autofill store — the page stores nothing, but "entered data is not stored"
  is not literally true end-to-end; the user agent stores it.
- No `maxlength`: a 1 MB paste into `#rname` is accepted and held in the DOM (validation only
  checks the lower bound). No memory-exhaustion consequence at one field, but there is no cap.

### A2. postMessage surface

Two directions, both unguarded.

**Outbound — `post()` at 1216–1220 sends with `targetOrigin = "*"`** (1219). Everything the widget
says about itself (height, language, every analytics event, `v`, `contract`) is readable by
whatever page holds the frame reference. `ORIGINS = null` at 1214 with the comment
*"null = accept any parent for the POC; production pins an allowlist"* — the pin was never installed.

**Inbound — listener at 1312–1331 has no `e.origin` check and no `e.source` check.**

| Message | Effect | Attacker capability |
|---|---|---|
| `{type:"fhf-ping"}` | replies `pong` with height (1329) | confirms the frame is alive; leaks height only |
| `{type:"fhf-config", config:{height}}` | sets `data-fit`, forces a height push (1316–1320) | controls frame sizing behaviour; probe confirmed `fixed:true` echo |
| `{type:"fhf-config", config:{reveal:<id>}}` | `document.getElementById(id).scrollIntoView()` (1321–1324) | scrolls the frame to any element — e.g. the payment QR — useful to stage a clickjacking overlay |
| `{type:"fhf-config", config:{lang}}` | `setLang()` → rewrites every string live (1327, 1124–1136) | lets a third party change the language of a page the donor believes is the charity's |
| `{type:"fhf-consent", marketing:bool}` | `cfg.consent = !!d.marketing` (1330) | **sets marketing consent on the donor's behalf** |

Empirically confirmed from `http://127.0.0.1:8799` (a different origin from `2skdigitals.github.io`):
the parent page posted `fhf-ping` and received `{"type":"pong","height":900,...}`; it posted
`fhf-config {height:"500"}` and received `{"type":"resize","fixed":true,...}`. The widget acts on
instructions from any origin.

**The consent finding is worse than "no origin check".** `cfg.consent` is assigned at 1330 and
**read nowhere else in the file** (full-file grep for `consent` returns only CSS, markup, i18n
strings, and that one assignment). So:
1. The widget has no consent gate at all — every analytics path (`track`, `dataLayer`) fires
   unconditionally.
2. Any page can nonetheless *set* the consent flag, so whenever someone wires it up, a hostile
   framer will be able to grant consent for a donor.

The same channel carries `fhf-consent` and `fhf-config`; there is no authentication, no nonce,
and no origin allowlist on either.

**Severity of the message surface alone: Medium.** No script execution, no data exfiltration —
but it is a live control channel into a donation widget, and it silently includes a consent-grant
primitive.

### A3. The `?gtm=` parameter — the finding that matters

```
1269  gtm: qs.get("gtm") || "parent",          // "parent" | "in" | "off" | "GTM-XXXXXXX"
1278  var GTM_LOAD_ID = /^GTM-[A-Z0-9]{5,}$/i.test(cfg.gtm) ? cfg.gtm.toUpperCase() : "";
1764  gs.src = "https://www.googletagmanager.com/gtm.js?id=" + encodeURIComponent(GTM_LOAD_ID);
```

The only check is the *shape* of the string. Any GTM container id in the URL is loaded and
executed **inside the widget's origin**. Verified:

```
GET .../embed/?part=receipt&gtm=GTM-ATTACK1
→ performance.getEntriesByType('resource')
  ["https://www.googletagmanager.com/gtm.js?id=GTM-ATTACK1"]
→ document.querySelectorAll('script[src]')
  ["https://www.googletagmanager.com/gtm.js?id=GTM-ATTACK1"]
```

GTM containers accept Custom HTML tags, i.e. arbitrary JavaScript. And this widget hands that
script the donor's data directly:

```
817   var st = {amount:100, band:"r17", mode:"once", exact:0};
1772  window.__fhfPoc = {..., state:function(){return st;}, ...}
```

Live check after typing HK$20,000 and income HK$900,000:

```
window.__fhfPoc.state() → {"amount":20000,"band":"r17","mode":"once","exact":900000}
```

So a container loaded from an attacker-supplied query parameter can read **the receipt form's
name/email/reference as they are typed, plus the donor's exact income and gift amount**, and
exfiltrate them to any endpoint. The frame looks and behaves exactly like the real widget.

This is a one-click weaponisation: `https://2skdigitals.github.io/fhf-taxcalc-poc/embed/?part=receipt&gtm=GTM-<attacker>`
in a link or an email, or framed on a look-alike page, is a working PII harvester on a URL that
carries the charity's own widget. **High now; Critical the day it is embedded in production**,
because the parameter would then travel with the charity's own links.

The same route gives script access to `window.__pocEvents` and `window.__fhfTax` (1776).

### A4. Delivery headers

`curl -sSI https://2skdigitals.github.io/fhf-taxcalc-poc/embed/` — full header set returned:

```
HTTP/2 200
server: GitHub.com
content-type: text/html; charset=utf-8
access-control-allow-origin: *
strict-transport-security: max-age=31556952
cache-control: max-age=600
```

| Control | Widget page (GitHub Pages) | Host page (`hollows.org/zh-Hant-HK/`) |
|---|---|---|
| CSP | **absent** | **absent** |
| X-Frame-Options | **absent** | absent |
| CSP `frame-ancestors` | **absent** | absent |
| Referrer-Policy | absent (browser default `strict-origin-when-cross-origin`) | absent |
| Permissions-Policy | **absent** | **absent** |
| HSTS | present, `max-age=31556952` | present, `max-age=2592000` |
| X-Content-Type-Options | absent | absent |
| `sandbox` on the embed iframe | **n/a — no live embed exists yet** | — |

Host page confirmed served by Cloudflare in front of an Azure app
(`server: cloudflare`, `request-context: appId=cid-v1:…`).

**Structural finding, not a TODO.** GitHub Pages cannot set response headers
(custom headers, CORS and security headers are unsupported — GitHub community discussion #54257
and #157852, still open). And `frame-ancestors` is one of the directives the HTML spec requires
user agents to **ignore** inside `<meta>` (MDN, CSP `frame-ancestors`: *"This directive is not
supported in the `<meta>` element"*). Therefore:

- The widget **cannot** declare an origin allowlist for framing while it is hosted on GitHub Pages.
  Any site can frame it, forever, and no amount of editing `index.html` changes that.
- The only remaining lever is the embedder: `sandbox` and `allow` on the host's `<iframe>`.
  A `sandbox="allow-scripts allow-forms allow-same-origin"` still permits the GTM injection,
  because the script runs same-origin inside the frame. `sandbox` without `allow-same-origin`
  breaks storage-backed GTM and the QR assets; it is a blunt instrument, not a fix.
- Pinning `e.origin` (violates nothing, costs 3 lines) is the actual fix for A2 and removes the
  consent spoof. It does **not** fix A3.

Note `access-control-allow-origin: *` — harmless here (public page, no credentials) but it does
mean any site may `fetch()` the widget's HTML.

### A5. Third-party dependency surface

Requests the page makes on load (verified via `performance.getEntriesByType('resource')` on the
live URL — **2 entries** on `?part=receipt`):

| # | Origin | What | Line |
|---|---|---|---|
| 1 | `2skdigitals.github.io` | `assets/help/alipay-step-2.jpg` | 751 |
| 2 | `2skdigitals.github.io` | `assets/help/alipay-step-3.jpg` | 757 |
| 3 | `2skdigitals.github.io` | `assets/logos/alipayhk.png` (QR, on `?part=pay`/`all`) | 670 |
| 4 | `www.googletagmanager.com` | GTM, **only if `?gtm=` is supplied** | 1764 |

So **one initial third-party origin (Google) and only when a query parameter asks for it**; zero by
default, because `cfg.gtm` defaults to `"parent"` (1269). No web fonts (the stack is system fonts,
line 65). No CDN, no icon font, no analytics script otherwise.

Not requests, but outside the charity's control on click: `render.alipay.hk` deeplink (690),
`www.hollows.org` (674, 695), `www.ird.gov.hk` (788). All `rel="noopener"`, one `noreferrer` (788).

For the legal team: **one processor to accept (Google) if analytics is enabled — and it is the one
that is unauthenticated by URL, which is A3.** Otherwise the third-party surface is zero.

### A6. Disclaimer vs code

`786  <li data-i18n-html="rc.disc.2">Does not collect, record, or store entered data.</li>`

| Clause | Verdict | Evidence |
|---|---|---|
| "Does not **collect**" | **True of the widget, with one caveat.** No `fetch`/XHR/`sendBeacon`/`Image`/`WebSocket` anywhere in the file. Submit handler (1669–1693) sends nothing: verified — after filling and submitting, resource entries stayed at exactly the two help images, `document.cookie` was `""`, and the only outputs were two local events. Caveat: `autocomplete=name`/`email` lets the *browser* collect; and if `?gtm=` is present, a third-party script in the frame can collect everything. | 1670–1693, 714, 719 |
| "Does not **record**" | **True in the page.** Nothing is written to storage — no `localStorage`, `sessionStorage`, `document.cookie`, `indexedDB` (grep returns no hits at all). | whole-file grep |
| "Does not **store**" | **True of persistence, false of memory.** Values remain in the live DOM after submit (`Chan Tai Man` / `donor@example.com` / `2026111800123` all still readable), so they exist in the frame's memory and in browser autofill until navigation. | 1694, verified |
| *(not stated, and material)* "we will match your payment and issue the tax receipt" | **False.** Nothing leaves the browser. The donor is shown `多謝您。我們會先核對付款，核對後發出扣稅收據。` ("We will match your payment first, then issue the tax receipt"), the button changes to `已收到` / **"Received"** and is disabled (1684–1691). No record exists anywhere for the charity to act on. | 1684–1691, 1103–1104 |

The disclaimer's three clauses are defensible. The **success message is the defect**: the widget
tells a donor their receipt claim was received when it was discarded. That is a data-loss and
consumer-representation problem sitting inside a privacy assessment, and it is the most likely
thing to cause a real-world incident before any attacker does.

### A7. Findings table

| # | Finding | Severity | Exploitability | Fix (concrete) |
|---|---|---|---|---|
| 1 | `?gtm=` loads an arbitrary container id inside the widget origin (1278, 1764); that script reads form PII and `__fhfPoc.state()` income (817, 1772) | **High** (Critical once live in prod) | One click on a crafted link, or one hostile frame. No auth, no user warning | Delete the `gtm` query parameter entirely. Bake the container id in as a constant (`var GTM_LOAD_ID = "GTM-M7QJ9DZK"`). A URL param must never select executable code |
| 2 | Success message claims receipt received; nothing is sent or stored (1684–1691) | **High** (integrity/goodwill, not CWE) | Trivial — every donor hits it | Until an endpoint exists, replace with a real instruction (e-mail address / donate-page link) and drop `已收到`. Never ship this text against no backend |
| 3 | `postMessage` inbound has no origin/source check (1312–1331) | **Medium** | Any page that frames the widget | `var ALLOWED=["https://www.hollows.org"]; if (ALLOWED.indexOf(e.origin)<0 \|\| e.source!==window.parent) return;` at 1313 |
| 4 | `fhf-consent` sets marketing consent from any origin, and `cfg.consent` is never read (1330) | **Medium** (latent — becomes High if wired) | Any framing page, today | Origin-pin per #3, and do not accept consent over postMessage; gate GTM load on a first-party consent UI |
| 5 | No CSP, no `frame-ancestors`, no XFO; GitHub Pages cannot set headers and `<meta>` cannot carry `frame-ancestors` | **Medium** (structural, enabler of #1/#3/#4) | Any site may frame | Move off GitHub Pages to Cloudflare Pages or Netlify and set `Content-Security-Policy: frame-ancestors https://www.hollows.org; default-src 'self'; script-src 'self' https://www.googletagmanager.com` |
| 6 | `post()` uses `targetOrigin="*"` (1219) | **Low** | Passive — leaks height/lang/events to any framer | Send to the pinned origin; while un-pinned, send nothing but `resize` |
| 7 | `ORIGINS = null` with a comment promising a production allowlist (1214) | **Low** (documentation debt that became a bug) | — | Delete the variable; enforce inline |
| 8 | No `maxlength` on `#rname`/`#rmail` (714, 719); `autocomplete=name/email` on PII fields | **Low** | Local only | `maxlength="100"` / `maxlength="254"`; keep autocomplete (donor convenience) but say so in the privacy notice |
| 9 | `?debug=1` renders an in-page event log (1281, 1335) | **Low** (info disclosure of analytics shape) | Guessing the param | Strip on build or gate behind a host-message flag |
| 10 | `window.__fhfPoc` / `window.__fhfTax` / `window.__pocEvents` exported globally (1234, 1772–1776) | **Low** — High *in combination with* #1 | With #1: reads income | Remove `state()` from the public object in production; keep a debug build |
| 11 | Three `innerHTML` sinks (1129, 1335, 1395) | **Informational** — no XSS reachable | — | Leave; if the i18n table ever becomes remote, switch 1129 to `textContent` + explicit allow-list of the 5 legal strings that contain `<a>` |
| 12 | `target="_top"` on payment links (674, 690, 695) | **Informational** | User-activated only | Leave; correct as-is |

No invented CVEs; nothing here maps to a published CVE, and none is claimed.

---

## Part B — threat model for the receipt endpoint that does not exist

The data class: donor full name, e-mail, transaction reference, donation amount, implied
assessment-year aggregate. Under the PDPO that is personal data; the transaction reference is a
financial identifier. Volume is low (hundreds to low thousands per year), which is what makes
cheap architectures viable — and also means the dominant cost is **human process**, not compute.

### B1. Comparison

| | (i) Azure Function App + private store + ClickUp push | (ii) Cloudflare Worker + D1 + R2 | (iii) ClickUp as system of record |
|---|---|---|---|
| **Data residency (HK donor PII)** | Function/Storage/SQL in **East Asia = Hong Kong** (Microsoft's region list: East Asia → physical location Hong Kong, 3 AZs, paired with Southeast Asia). **But the ClickUp push lands a second copy in Singapore (Enterprise) or one of five AWS regions incl. US (non-Enterprise)** — so the end-to-end answer is HK + SG/US | No HK guarantee below Enterprise. Cloudflare offers jurisdiction restrictions / Data Localization Suite on Enterprise only. D1 primary region is set by hint (APAC, not HK). R2 stores objects in the region chosen at bucket creation. **Assume "APAC, not HK" and mark as verify with Cloudflare** | **Singapore** for HK customers on Enterprise (ClickUp's own hosting article lists Hong Kong among countries auto-hosted at the Singapore data center); otherwise Oregon/Ohio/Sydney/Singapore/Dublin, no control without Enterprise. Integrations and workspace avatars sit **outside** the chosen region; login/notes/reminders are global |
| **Processor** | Microsoft (Azure) under the Microsoft Products and Services DPA; **plus ClickUp as a second processor** with its own DPA and subprocessor list | Cloudflare alone under its DPA — **one processor** | ClickUp under its DPA; subprocessors include AI features |
| **Encryption** | Storage SSE AES-256 by default; TLS 1.2+ enforced; secrets in Key Vault (HSM-backed keys optional) | TLS 1.3 at edge; encryption at rest (verify current wording in their DPA); R2 encrypted at rest | TLS 1.2+, AES-256 at rest, AWS KMS (ClickUp public statements) |
| **Access model — is "admin" a real role?** | **Yes, and it is the strongest part of this option**: Entra ID groups, managed identity from Function → SQL/storage (no stored connection string with a password), Azure RBAC on the resource group, private endpoint so the DB has no public IP | **Yes — Cloudflare Access (Zero Trust)** in front of an /admin route; identity from the charity's IdP; free tier covers small teams. Per-route policy, not per-seat | **"Admin" is a licence seat plus a role.** There is no row- or field-level security: anyone with access to the Receipts list sees every donor row in it. Field-level PII redaction is not a ClickUp feature |
| **Audit trail** | Azure Monitor / Log Analytics + SQL auditing; you define retention | Workers Logpush / Access logs (paid tiers); your own append-only table | Workspace audit logs are **Enterprise and Max plans only**, owner-only by default, and **retain 60 days**. Task-level history is not an access log |
| **Retention & deletion** | Real `DELETE`, provable, scheduled; you own the clock | Real `DELETE`; D1 rows and R2 objects removed on command | Manual. Deleting a task is not a purge — it persists in trash/backups; no deletion certificate; 60-day audit horizon |
| **Backup / restore** | Azure SQL automated backups, PITR 7–35 days depending on tier | **D1 Time Travel: 30-day point-in-time restore** on the paid plan; R2 versioning | Plan-dependent; workspace export is manual. Restoring a single deleted task is a support request in practice |
| **Breach notification path** | Microsoft notifies under DPA → charity assesses → PCPD + data subjects. **Two processors means two notification chains and two clocks** | Single processor → one notification chain | ClickUp → charity. But detection is weak: no access log below Enterprise, so "we think someone opened the list" is unprovable |
| **Realistic monthly cost (USD)** | Functions compute ≈ **$0** at this volume (1M executions + 400k GB-s free/mo). Real bill is the estate: Azure SQL Basic ~$5, Storage ~$1–2, Key Vault ~$1–3, Log Analytics ~$5–15, private endpoint ~$7/endpoint. **$15–60/mo (≈HK$120–470)**, more with a support plan (~$29/mo Developer) or App Insights retention. **Not pennies — the database and the observability are the cost, not the function** | Workers Paid **$5** minimum + D1 (5 GB included, 25bn rows read/mo) + R2 $0.015/GB. **$5–8/mo (≈HK$40–65)** — the HK$60 estimate holds | Per-seat: Business-tier list pricing is order **$12–19/user/mo**; Enterprise custom (required for HK→Singapore hosting, audit logs, SSO). Cheap in licence dollars, expensive in risk |

### B2. The three failure modes most likely in practice

**1. Duplicate receipts — the one with a tax consequence.** Three independent routes to the same
outcome: a retry storm (client or Function retries a 500 that actually committed), a double-click
on a slow submit, and two family members claiming the same gift with the same transaction
reference. Every route ends with **two receipts issued for one gift**, which is an IRD problem,
not an IT one. The design must key on `UNIQUE(transaction_reference, amount)` with a
`pending → matched → issued` state machine, and the endpoint must be idempotent on a
client-generated key. This is also why "the same transaction ID submitted twice" cannot be
solved in the UI — the donor is allowed to be confused; the record layer is not.

**2. PII in the PM tool's search index, and guest over-exposure.** In option (iii) — and in the
ClickUp leg of option (i) if it carries real fields — a donor's name and e-mail sit in a task
title/description that ClickUp's search indexes across the whole workspace, is reachable by
ClickUp AI features, and is visible to anyone holding a guest invitation to that Space. The
failure is not exotic: it is one well-meaning staff member inviting a volunteer "just to the
receipts folder", and the volunteer can now read 3,000 donors. It is also silent — no alert fires.

**3. An unauthenticated function URL found by a scanner.** Azure Functions require a key **only**
if `authLevel` is not `anonymous`; a template or a quick `func new` leaves `anonymous` and the
`*.azurewebsites.net` hostname is enumerable. The consequence is not data theft (there is nothing
to read on a write-only endpoint) — it is **queue poisoning**: forged receipt claims, ClickUp API
quota burn, and a task list full of fake donors that a real staff member then has to triage against
bank records. Mitigation is function-key *plus* WAF rate limiting *plus* a shared-secret HMAC and
a per-IP cap, and a custom domain so the default hostname is not the public one.

Also real, ranked below those three: receipt screenshots uploaded as attachments (an image of a
bank record inside a PM tool, unredacted, downloadable by any workspace member — plain reject);
webhook replay (ClickUp webhooks **are** HMAC-SHA256 signed via `X-Signature`, so authenticity is
covered — but the payload carries no timestamp or nonce, so a captured delivery can be replayed
indefinitely; the consumer must keep a `webhook_id + history_item id` dedupe table).

### B3. What an HK charity privacy reviewer would do

**Reject outright**
- ClickUp as the system of record for donor PII (option iii). No HK region, no field-level
  access control, audit logs only on the top two plans and only 60 days, PII inside a shared
  search index. There is no defensible answer to "who accessed donor X's record last March?"
- Any design with no stated retention period and no deletion mechanism — the PDPO expects data
  to be kept no longer than necessary, and "we'll clean it up" is not a mechanism.
- An `authLevel: anonymous` endpoint, or a public blob container.
- Receipt screenshots as PM-tool attachments.
- Cross-border transfer with no documented assessment. Note s.33 of the PDPO has never commenced,
  so there is no statutory cross-border prohibition — but PCPD's guidance still expects a privacy
  impact assessment and contractual safeguards, and a charity's funders ask for it.

**Accept with conditions**
- **PII stays in one private store in Hong Kong; the PM tool carries only an opaque claim id.**
  Task title = `FHF-2026-000123`, custom fields = status, amount band, assigned officer. Staff
  click through to an authenticated lookup for the name and e-mail. This single decision makes
  options (i) and (ii) compliant and kills failure mode 2. It is also the cheapest change to make.
- Azure **East Asia** with Key Vault + managed identity + private endpoint, ClickUp receiving ids
  only, two DPAs on file, 24-month retention with a scheduled purge job, and a written
  breach-notification runbook naming PCPD and the 72-hour internal clock.
- Cloudflare with Access in front of `/admin`, D1 Time Travel enabled (30 days), a documented
  "APAC, not HK" residency caveat accepted by the client in writing, and the same retention job.

---

## Recommendation

**Build option (ii), Cloudflare Worker + D1 + R2, with the ClickUp list holding opaque claim ids
only — and do not ship the receipt form until that exists.**

The reasoning that decides it, in order:

1. **The endpoint is the smallest part of the risk; the PM tool is the largest.** Whichever compute
   you pick, the compliance question is decided by whether donor PII enters ClickUp. Once that
   answer is "no, ids only", options (i) and (ii) become architecturally equivalent on the point
   the privacy reviewer cares about — and then the tiebreak is cost, role model and backup.
2. **On that tiebreak Cloudflare wins on all three.** One processor instead of two notification
   chains. `$5–8/mo` against `$15–60/mo` — and the Azure figure is not the Function, it is the SQL
   database, Key Vault, Log Analytics and a private endpoint, i.e. a fixed estate you now operate
   forever. Cloudflare Access gives a genuine role-based admin surface without buying seats.
3. **D1 Time Travel (30-day PITR) and R2 versioning are the backup story you would otherwise have
   to build.** For a receipt ledger that is the difference between a restore and an incident.
4. **Honest costs of the choice:** no HK residency guarantee below Enterprise (disclose it, get it
   in writing), and you own the application — validation, idempotency, dedupe, retention purge.
   Azure's advantage is real if the charity already runs Entra ID and wants the Microsoft DPA and
   an HK region end-to-end; that is a legitimate reason to pick (i), and it is a business reason,
   not a security one.

**Before any of that, two things in the widget are shipping defects independent of the endpoint:**

- kill `?gtm=` (A3) — it is a PII harvester in a URL, and it is three lines to remove;
- kill the "Received" confirmation (A6/#2) — it currently tells donors a claim was filed that
  never left their browser.

Both should be fixed in this round regardless of which backend is chosen.
