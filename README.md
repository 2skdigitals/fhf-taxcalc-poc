# FHF HK — donation tax calculator · iframe POC

Proof of concept. Answers one question before build:
**can the client's Optimizely iframe component carry the interactive calculator and the QR payment surface?**

| Path | What it is |
|---|---|
| `/embed/` | the widget — the thing that goes in the CMS iframe component |
| `/harness/` | test bench: auto vs fixed height, sandbox, allow, width, GTM, live message log, pass/fail, copy report |
| `/preview/` | the widget inside a mock Optimizely page (hero + FAQ marked as client-built) |
| `/scan.html` | where the POC test QR resolves |
| `docs/INTERFACE.md` | the iframe contract (postMessage API + required attributes) |
| `docs/TEST-PLAN.md` | the five-minute test pass to run inside their staging |
| `qa/poc_test.py` | 23 automated checks (`python3 qa/poc_test.py <base-url>`) |

Not production. QR codes are test codes, not merchant codes. No donor data leaves the page.
