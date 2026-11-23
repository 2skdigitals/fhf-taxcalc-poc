# Fred Hollows HK — security review: calculator + receipt flow

2SK Solutions · 23 Nov 2026 · for Kevin / client decision

## The short version

**Nothing the donor types leaves the browser.** In all 1,780 lines of `embed/index.html` no `fetch`, `XHR`, `sendBeacon`, pixel or URL parameter carries a field value. The submit handler (1669) intercepts, validates and thanks, then fires two events carrying `{method, has_reference}` and `{donation_type, state}` (1689–1690) — no name, email, reference or amount. No cookies, no storage: line 1668, *"this build keeps the form in page memory only."*

**Correction to the brief: there is no receipt-screenshot upload.** No `type="file"` exists in this build or any of 18 archived versions. The form is four fields — name, email, payment reference, consent (710–772). The riskiest part of the proposed flow isn't in the code, and shouldn't be.

Two fixes are needed before production, neither in the calculator: the listener has **no origin check** (1312), and GitHub Pages **cannot serve** the `frame-ancestors` header promised at `docs/INTERFACE.md:335`. The real decision is the backend: **ClickUp must not become the record store for Hong Kong donor PII.**

---

## 1 · What exists today

**Safe:** no field-value egress; no input-reachable XSS — the three `innerHTML` sinks are i18n strings from a fixed dictionary (1129), `fmt()` of a number (1395), and a `?debug=1` overlay (1335); no persistence or credentials; one `console.log` gated on `cfg.debug` (1229).

**Unsafe:**

1. **Listener trusts any origin (1312–1345), and outbound `postMessage(msg,"*")` (1219) goes to any parent.** No `e.origin`/`e.source` check, so any framing page can set height, scroll target, language — and `fhf-consent`, flipping `cfg.consent` with no donor action. Low impact now; consent-integrity once the form posts.
2. **No framing control on GitHub Pages.** Any site can embed it and clickjack the submit. `frame-ancestors` must be a response header on the production host — `<meta>` is ignored for it.
3. **`window.__fhfPoc.state()` (1773)** exposes amount, band and exact income to any script in the frame. Remove with the debug overlay.
4. **Autofill** `autocomplete="name"`/`"email"` (714, 719) is right; no credential capture (no password fields); kiosk devices leak the previous user's details. **GTM in-frame** is a subprocessor question, not a leak — Google sees `document.referrer` and `location.href` (1752–1758).

---

## 2 · Threat model — browser → Function → ClickUp

**Assets:** name, email, payment reference (a financial identifier), attachment, and their linkage — a matchable donation record. **Actors:** non-donor, 2SK staff, client staff, subprocessors (Microsoft, ClickUp + 31, Google), attacker.

| # | Threat | Control |
|---|---|---|
| 1 | **Spam/flood** on an unauthenticated endpoint buries real donors | 4 KB cap; 5/hr, 20/day per IP; honeypot + minimum time-to-submit; no auto-reply. No CAPTCHA unless abuse appears. |
| 2 | **Enumeration/IDOR** of other donors | No donor-facing read endpoint in v1. If needed: 128-bit token by email, single record, rate-limited. |
| 3 | **ClickUp token blast radius** | A personal token is *workspace*-scoped, not list-scoped — it reads every list the seat sees. Key Vault, seat on one folder, quarterly rotation. |
| 4 | **Attachment** malware/size/type | Accept none. If forced: 5 MB cap, magic-byte check, re-encode, isolated blob, Defender scan, never served from the app origin. |
| 5 | **PII into logs** | No App Insights request-body capture; redact name/email/ref; prove by submitting a known value and grepping logs. |
| 6 | **Formula injection** in the IRD export | XLSX not CSV; escape leading `= + - @`; reference as text. |
| 7 | **Fraudulent claim** — self-reporting another's reference | The form creates a *claim*, not a receipt: `unmatched → matched → issued`, only against settled payment. |
| 8 | **PDPO access/correction/erasure failure** | Key = email + reference hash; DSR runbook on a 40-day clock; deletion must reach backups. |

---

## 3 · ClickUp verdict

**No — it must not hold donor PII.** A collaboration tool with a US-defaulted, 50-subprocessor data path and no erasure you can prove.

- **Residency:** AWS Oregon/Ohio by default; a Hong Kong **Enterprise** tenant lands in **Singapore**. Region choice is Enterprise-only; integrations, avatars, login data, Notes and Reminders stay outside it.
- **Subprocessors:** 31 platform processors, ~50 total, effectively all US — Snowflake, Segment, Datadog, Amplitude, Sentry, plus OpenAI/Anthropic/Google.
- **PDPO:** s.33 isn't in force, so Singapore/US is lawful — but DPP1 requires naming transferee classes *at collection*.
- **Least privilege:** roles are workspace/folder/list level, not field level. One invite exposes every column.
- **Audit and erasure:** per-task activity feed only, no queryable "who read this"; delete → Trash (~30 days) → purge plus backups you don't control, so no defensible "deleted" statement.
- **Export:** works well — the risk being an uncontrolled PII copy on a laptop.

**Acceptable use:** the work item only — opaque ID, status, date, campaign, ref **last 4**, owner. Never name, email, full reference, attachment, amount or income.

---

## 4 · Azure Function verdict

Right primitive, over-specified.

- **Shape:** one HTTP trigger, one write, one notification. Hundreds per campaign is nothing; consumption plan is correct. Cold start is irrelevant — return `202`, work async.
- **Simpler primitive first:** if client IT confirms a CRM endpoint, **there is no server to build**. Otherwise Function + Table Storage.
- **Region:** `eastasia` is **physically Hong Kong** (paired with `southeastasia`). The strongest residency answer.
- **Secrets:** managed identity; ClickUp token (if any) via `@Microsoft.KeyVault(...)`; nothing in code or the widget.
- **App Insights:** no request bodies; explicit scrub for name/email/ref — telemetry is where PII lands by accident.
- **WAF:** APIM and Front Door are wrong at this size (>US$100/mo before use). Function-level limits, pinned CORS, budget alert.

---

## 5 · Recommended architecture

```
Donor browser (iframe; analytics carry no PII)
   │  POST /api/receipt — JSON ≤4 KB, no file
   ▼
Azure Function (eastasia / Hong Kong)
   ├─ managed identity → Key Vault
   ├─ validate · rate limit · honeypot
   ├─ write ──► Client CRM (preferred) or Azure Table Storage (2SK, DPA, HK)
   └─ append ─► ClickUp task: opaque ID + status, no PII
```

| May live in ClickUp | May never live in ClickUp |
|---|---|
| Opaque ticket ID | Donor name |
| Status: unmatched / matched / issued | Email address |
| Date, campaign, language | Full payment reference |
| Reference **last 4** | Receipt image or attachment |
| Finance owner | Amount, income band, tax figure |

**Minimum controls before one real record is written:** origin + source validation, with `fhf-consent` rejected from unvalidated parents · a real `frame-ancestors` header · CORS allowlist, payload cap, per-IP limit, honeypot · no upload endpoint in v1 · managed identity + Key Vault, zero secrets in code · telemetry redaction proven by test · an in-widget PDPO notice naming purpose, transferee classes, retention and contact · a DSR runbook with a 40-day clock · purge unmatched claims at 90 days · a pre-launch pass for injection, enumeration, replay, rate-limit and oversized payload.

**The client must agree in writing:** data user vs processor · that records transit Singapore/US if ClickUp is in the path · retention and who owns deletion · that the form creates a claim, not a receipt · whether Google sits in the analytics path · that no uploads are accepted unless they own the malware burden.

---

## 6 · Estimate

| Work | MD |
|---|---|
| Widget hardening — origin checks, debug surface, privacy notice | 1–2 |
| Backend — Function, storage/CRM write, MI + Key Vault, validation, rate limit | 4–6 |
| Finance export + matching workflow | 1–2 |
| PDPO pack — notice, DPA review, retention, DSR runbook (PM) | 1.5–2.5 |
| QA + security test pass + UAT | 1.5–2.5 |

**11–16 MD · HK$22,900–33,500** (technical 8–11 MD @ 2,043; PM/QA 3–5 MD @ 2,200). Estimate only, for Kevin to reprice; excludes subscriptions and any client-built CRM integration.
