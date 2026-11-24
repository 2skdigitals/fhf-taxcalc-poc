# Payment block — Option B, and the QR that had to be bigger (24 Nov 2026)

`qa/apply_pay_optionb_20261124.py` · `qa/shot_pay_desktop_20261124.py` · `docs/INTERFACE.md` §2, §6

## What was decided

Kevin picked **Option B — "size by function"** from `design/pay-desktop/options.html` (render:
`design/pay-desktop/option-B.png`) and asked for a bigger code. Option C was rejected: no
"Recommended" kicker, no sales line, no new client-facing copy in this pass.

## What shipped

**Desktop (≥720px)** — two tiles in a 760px pair, `1.35fr / 1fr`, 24px apart:

| Tile | Holds |
|---|---|
| AlipayHK (wide) | the QR (190px), the name, `Scan with your phone`, and the receipt note with its `?` |
| Credit card (compact) | the glyph, the name, and `On the Foundation's donation page` on a ruled foot line |

Both tiles are **click-anywhere through a stretched link**: the tile is a `<div>`, its own `<a>`
paints the surface with `::after` (`inset:0; z-index:1`), and the receipt note sits at `z-index:2`
so the `?` is a real button — visible, clickable and in the tab order (AlipayHK tile → `?` → card
tile). A `<button>` inside an `<a>` is invalid HTML and breaks keyboard order; this is the pattern
that avoids it.

**Phone (<720px)** — untouched, by construction *and* by measurement. The tiles collapse to the one
thing a phone needs from them, the receipt note, which keeps its exact place between the two rails.

## The QR

`assets/logos/alipayhk.png` is 450×350 with the code at only **212×212** — 29% of the pixels, with
119px of white on each side. At the block's 190px ceiling that rendered a **~90px** code, which
`cv2.QRCodeDetector` does not read at any scale.

`assets/logos/alipayhk-qr.png` is the tight crop: **264×264**, the same code plus the spec's
4-module quiet zone, 212 bytes larger than the original. Rendered at 190px it puts a **~152px**
code on screen. It is not re-coloured, re-compressed or re-cropped further.

Measured decode, from a screenshot of the rendered element (not the file):

| Width | Rendered | Decodes |
|---|---|---|
| 720 / 768 | 160×160 | yes (2× upscale) |
| 900 / 1024 / 1440 | 190×190 | yes (2× upscale) |

Same result in both languages; the decoded payload is the live endpoint
`https://render.alipay.hk/p/s/hkwallet/landing?…` that the tile links to. `qa/poc_test.py` now
asserts this at runtime, because "renders" was never the requirement — "scans" was.

## Mobile is provably unchanged

`?part=pay` pixel-diffed, HEAD versus this build, at **13 widths from 320px to 719px in both
languages** (320, 328, 360, 390, 414, 430, 480, 540, 568, 600, 640, 700, 719):

```
zh-HK 320px identical    en 320px identical
zh-HK 328px identical    en 328px identical
… 13/13 identical both languages — 0 differing pixels in every capture
```

Deterministic capture (fixed viewport, `deviceScaleFactor 1`, animations off, lazy images forced
eager, fonts settled), so a diff would mean a layout change rather than a timer.

## Heights

The pair is **shorter** than the two cards plus the separate receipt row it replaces, and the peak
was already at 320px on a phone, which this pass does not touch.

| Block | 320 | 390 | 768 | 1024 | 1440 |
|---|---|---|---|---|---|
| `?part=pay` zh | 628 | 566 | 641 → **568** | 649 → **613** | 649 → **613** |
| `?part=pay` en | 739 | 656 | 669 → **596** | 677 → **641** | 677 → **641** |
| `?part=all` zh | 2121 | 1917 | 2159 → **2086** | 2191 → **2156** | 2191 → **2156** |
| `?part=all` en | 2482 | 2244 | 2268 → **2194** | 2269 → **2234** | 2269 → **2234** |

**Declared heights do not change**: `?part=pay` **690 / 800**, `?part=all` **2225 / 2550**, all with
more slack than before (pay 62 / 61px at the peak). There is no CMS edit in this pass, and the
numbers must stay thousands-separator-free when they are quoted.

## The receipt panel moved

It opened **upward** from 720px because the note used to be the last thing in the block. Inside the
tile the note sits ~300px down a 640px frame, so there is no room above it: the panel now opens
**downward from the note**, 420px wide, `max-height: clamp(240px, 100vh − 340px, 380px)`, its own
scroll. `qa/probe_panel_fit.py`, 12 widths × 2 languages:

```
zh 768   panel top 274  bottom 624  right 651   frame 690 / 768   OK
zh 1024  panel top 300  bottom 650  right 689   frame 690 / 1024  OK
zh 1440  panel top 300  bottom 650  right 769   frame 690 / 1440  OK
en 768   panel top 302  bottom 682  right 651   frame 800 / 768   OK
en 1024  panel top 328  bottom 708  right 689   frame 800 / 1024  OK
en 1440  panel top 328  bottom 708  right 769   frame 800 / 1440  OK
```

Inside the frame on all four sides in every case; the six crops scroll inside the panel, the
disclaimer and the block height never move (`?part=pay` scrollHeight is identical open and closed).

## Gates

| Gate | Result |
|---|---|
| `qa/poc_test.py` | 101 passed, 0 failed (two structural checks rewritten for the pair, three added: tile asymmetry, tight crop ≥160px, **rendered QR decodes**) |
| `qa/lang_parity.py` | 18 passed, 0 failed |
| `qa/test_tax_engine.py` | 6/6 |
| `qa/verify_six_examples.py` (zh, en) | 6/6 each |
| `qa/design_gate.py --base …` | 0 failures |
| `qa/sweep_heights.py` (zh, en) | no overflow, peaks unchanged |
| `qa/probe_panel_fit.py` | panel inside the frame at all 12 widths |
| pixel diff, 390px + 12 more | 0 differing pixels |

`qa/lang_parity.py` gained two small pieces of honesty while passing: snapshots are compared with
whitespace collapsed (a moved node changes indentation, not copy), and a failed baseline diff is
re-checked as a **word bag** — a re-order with identical copy is reported as a note, while any
added, cut or reworded string still fails. That pass produced 63 re-ordered fields, 0 copy changes.

## Live

Deployed to `main` (`1a5e78d`) and verified from
`https://2skdigitals.github.io/fhf-taxcalc-poc/embed/`:

- **HTTP 200**, and the served bytes are **byte-identical** to `embed/index.html`
  (`sha256 f224443990725794…`, 119,135 bytes) — `qa/verify_live.py`, 28/28.
- **The QR decodes from the live page**: 168 chars, `https://render.alipay.hk/p/s/hkw…`, captured from
  the rendered `.tile-qr` at 768 and 1440px in both languages.
- **`?part=pay` reports its declared height** — `documentElement.scrollHeight` 690 zh / 800 en at 390,
  768 and 1440px, i.e. exactly the number in the CMS.
- **The six receipt crops load** (41.9 KB together) and the tooltip opens with both flows in both
  languages at 390 and 1440px.
- `qa/poc_test.py` against the live base: **101 passed, 0 failed**.

Live shots: `shots/pay-desktop-20261124/LIVE-{zh-HK,en}-{768,1440}[-panel].png`.

A stale gate was found and fixed on the way: `qa/verify_live.py` still matched the receipt crops by
their full URL, so the `?v=20261124b` cache keys added in `aa8f09b` made five of its checks fail on a
correct deploy. It now compares the asset path (commit `d366790`).
