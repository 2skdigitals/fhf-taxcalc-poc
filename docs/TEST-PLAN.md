# Test plan — FHF tax calculator iframe POC

**Goal:** prove the Optimizely iframe component can carry the calculator and the payment surface, and record exactly which configuration the build must target.

**Time:** 5 minutes per configuration. **Evidence:** the `Copy test report` JSON from the bench.

---

## 1 · The three URLs

| Purpose | URL |
|---|---|
| The four fixed-height blocks | `https://2skdigitals.github.io/fhf-taxcalc-poc/embed/?part=input` (then `result`, `pay`, `receipt`) |
| Test bench — configuration matrix + verdicts | `https://2skdigitals.github.io/fhf-taxcalc-poc/harness/` |
| Page-context preview (mock Optimizely page) | `https://2skdigitals.github.io/fhf-taxcalc-poc/preview/` |

The component requires a height, so the experience is four blocks, each sized to a measured number (INTERFACE §2). Nothing is production. QR codes are test codes that resolve to a POC page, not merchant codes.

---

## 2 · The pass

Work in **their Optimizely staging**, not on the bench alone. The bench tells you what the widget does; staging tells you what *their component* does to it.

### Step 1 — the four blocks render at their declared heights
`input` 1000 · `result` 750 · `pay` 1100 · `receipt` 600. Confirm each renders and that **no internal scrollbar** appears. If one clips, record the width — we adjust the block, not the number.

**Fail signature:** blank box, or "refused to connect" → a header/CSP problem on their side (INTERFACE §2).

### Step 3 — interaction
- Type an amount, switch 單次 → 每月. The months control must appear and the total must recalculate.
- Press 唔知道 — the result must show a **range**, not a single number.
- Type a large gift (e.g. 175,000) — the label must switch to 「（最多）」/「（最少）」.
- Submit the receipt form empty — field errors must appear **without** the iframe growing a scrollbar.

### Step 4 — payment
- Press the **credit-card** tile. It must **leave the iframe** and land on `hollows.org/zh-Hant-HK/donate/`. If the page loads *inside* the frame, `target="_top"` is being sandboxed away — record it.
- Press **測試叫起 PayMe**. Read the message under the buttons. Either outcome is a finding:
  - page stays and says the browser did not handle the scheme → deep links are unusable in this configuration, QR is the only mobile path;
  - the app opens (or the browser asks) → deep link works here.
- Scan the QR with a phone. It must resolve to the scan page and show which rail it was.

### Step 5 — receipt capture
Fill name + email, tick consent, submit. The bench's **Checks** panel must turn `email_capture` to PASS.

### Step 6 — measurement
Paste the **staging** GTM container ID into the bench, press **Load GTM**, re-run steps 3–5. Open GTM Preview or the GA4 DebugView: the eight events must appear with the parameters in INTERFACE §5 and **no amounts**.

If the container has no listener tag yet, the events will only show in the bench's dataLayer — that is expected; the listener tag is the one thing GTM still needs (INTERFACE §5).

### Step 7 — devices
iPhone Safari **and** Android Chrome, on the real component. iOS decides the payment path.

---

## 3 · Record sheet

| # | Question | Answer |
|---|---|---|
| 1 | Does it render in the component? | |
| 2 | Height mode available | auto / fixed (which) |
| 3 | Smallest unclipped height — desktop | ___ px |
| 4 | Smallest unclipped height — mobile | ___ px |
| 5 | Card tile leaves the frame? | yes / no |
| 6 | Wallet app-open | works / blocked / asks |
| 7 | QR scans correctly? | yes / no |
| 8 | Receipt capture fires `email_capture`? | yes / no |
| 9 | `sandbox` attribute the component sets | none / ___ |
| 10 | `allow` attribute the component sets | none / ___ |
| 11 | Events reach dataLayer / GA4? | yes / no / partial |
| 12 | iOS Safari result | |
| 13 | Anything visually wrong at their width | |

---

## 4 · What each failure means for the build

| Finding | Consequence |
|---|---|
| Renders only with `sandbox` lacking `allow-top-navigation-by-user-activation` | Card rail and wallet links are dead. Either the component is changed, or we accept QR-only and say so in writing |
| Fixed height only, and the smallest safe height is very tall (e.g. > 1800px) | The page will have a large blank region on short content. Consider splitting the widget into two embeds (calculator / payment) — costs an extra integration step |
| No auto-height | Internal scrollbar on phones; the payment panel can end up below the fold of the frame. Acceptable but measurably worse — log it as a known limitation, not a surprise |
| GTM listener tag refused | Measurement goes dark. The six-proxy success model has no instrument. **Do not launch without a decision** |
| Deep links blocked everywhere | Mobile donors must save the QR image and use the wallet's in-app scanner. Copy must say that, and it is the version we ship |
| CSP blocks our origin | Their header change, their ticket, their timeline — start it now |

---

## 5 · Automated checks (already passing)

`python3 qa/poc_test.py https://2skdigitals.github.io/fhf-taxcalc-poc`

23 assertions: the six verified tax examples, the range behaviour, the cap flag, monthly arithmetic, the message contract, height convergence, no horizontal overflow at 390/1100 px, receipt validation, the honesty invariant (no amount/income/rate in any payload), the app-open observable, and the bench itself.

Last run: **23 passed, 0 failed** — local and against the live URL.
