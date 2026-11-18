# FHF HK — donation tax calculator · iframe POC

Proof of concept. Answers one question before build:
**can the client's Optimizely iframe component carry the interactive calculator and the QR payment surface?**

| Path | What it is |
|---|---|
| `/embed/` | the widget — the thing that goes in the CMS iframe component. `?lang=en` for the English build |
| `/harness/` | test bench: auto vs fixed height, sandbox, allow, width, GTM, live message log, pass/fail, copy report |
| `/preview/` | the widget inside a mock Optimizely page (hero + FAQ marked as client-built) |
| `/scan.html` | where the POC test QR resolves |
| `docs/INTERFACE.md` | the iframe contract (postMessage API, per-language heights, required attributes) |
| `docs/TEST-PLAN.md` | the five-minute test pass to run inside their staging |
| `docs/EN-BUILD-20261115.md` | the English build: string inventory, per-language heights, verification |
| `qa/poc_test.py` | 57 automated checks, Chinese build (`python3 qa/poc_test.py <base-url>`) |
| `qa/lang_parity.py` | 12 checks: Chinese byte-parity, English gate, language switch, payloads both languages |

Not production. QR codes are test codes, not merchant codes. No donor data leaves the page.
