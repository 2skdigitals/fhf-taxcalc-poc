# Direction B — "confident contrast"

`design/uplift-b/index.html` — one file, no new requests, tax engine byte-identical,
copy identical to `embed/index.html`. Served on :8771 only.

---

## Design read

The block is a **readout, not a form**: a donor arrives with one question ("what does
this gift actually cost me?") and the page answers it with a number. The previous build
answered with a paragraph of black text at 40px on a white ground, so nothing in the
block said *result*.

So: **one dark object carries the answer.** Everything else is white card, hairline,
and air — the panel only works as an anchor if nothing else competes with it.
Brand orange is the action, the money returned, and the active rung; navy is authority
and the state of "chosen". Two colours, three jobs each, used consistently enough that
the eye learns them by the second screen.

---

## The three decisions

**1 · The navy panel is the result, and it holds the whole result.**
`#net-label`, `#net`, `#net-caption` and the three `.figs` values sit inside one
`#01014E` field. The paid figure is white at `clamp(2.75rem,11vw,4.25rem)`, max 68px;
the tax saved is `#E97824`; donation and rate stay white but subordinate. The three
supporting numbers are a **two-column ledger** (label left, figure right, hairline
between rows, tabular figures) instead of a three-across strip — a strip reads as three
equal facts, a ledger reads as one total with its receipts. The plain-language
`#benefit` line sits *outside* the panel, on the ground, so the panel stays a readout
and not an essay.

**2 · Navy means "chosen"; orange means "value".**
Every selected state is the same fill: the segmented control, the quick-amount pills,
the chosen income rung. Orange never means state — it means money coming back
(`#saved`), the one action (`#goto-result`), and the left rule that marks the active
rung. That rule is why the ladder reads as a table you are *in*, not a list you scan.
It also fixes a contrast fact: `#E97824` as **text on white is 2.93:1** (fails AA), so
orange is never used as type on the light ground — only on navy (6.43:1) or as a fill
under near-black type (6.80:1).

**3 · The block reads as a sequence.**
Filled navy discs with white numerals (26px, `aria-hidden`, generated from CSS-bearing
markup, no new string) sit beside the two step headings, so "give → cost" is legible
before a word is read. Inputs live on white cards with a 1px `rgba(1,1,78,.14)` border
and 18–22px of internal padding; the ladder is a compact card with a hairline grid and
the rates right-aligned in **tabular figures** (system UI with `font-variant-numeric:
tabular-nums`, not a mono face — mono outside code is costume).

**Not done on purpose:** no side-by-side desktop layout. The CMS gives one fixed height;
a two-column arrangement halves the desktop height and leaves a half-empty frame at
1280. The block stays vertical at every width so the declared height stays meaningful.

---

## Measured contrast (rendered values, not guesses)

| Pair | Ratio | Where |
|---|---|---|
| `#FFFFFF` on `#01014E` | **18.82:1** | paid figure, ledger values, panel |
| `#E97824` on `#01014E` | **6.43:1** | tax saved (orange) — passes AA normal text |
| `#C6C8DD` on `#01014E` | **11.39:1** | panel label, caption, ledger labels |
| `#01014E` on `#F3F3F0` | **16.93:1** | headings on the ground |
| `#16161C` on `#F3F3F0` | **16.21:1** | body ink |
| `#3F3F4A` on `#F3F3F0` | **9.35:1** | secondary ink |
| `#6A6A75` on `#F3F3F0` | **4.80:1** | 13px notes (AA, tight) |
| `#6A6A75` on `#FFFFFF` | **5.34:1** | ladder rates, hints on cards |
| `#16161C` on `#F1F1F5` (navy wash) | **15.99:1** | selected rung |
| `#0A0909` on `#E97824` | **6.80:1** | primary button |
| `#E97824` on `#FFFFFF` | 2.93:1 | **not used** — orange is never text on white |
| `#F08A3C` on `#01014E` | 7.53:1 | offered as an alternative; the brand orange already passes |

The brief's fallback (`#F08A3C`) was **not needed**: `#E97824` clears AA on navy by
1.9 points. Checked, not assumed.

---

## Heights · `?part=calc`

Measured with Playwright at `device_scale_factor=1`, viewport height 900, default state
(single gift, "About 17%" band), true bottom of the last visible element
(`details#disclaimer`), plus the wrap's own bottom padding.

| Width | en · last element | en · block | zh-HK · last element | zh-HK · block |
|---|---|---|---|---|
| 320 | 1558.5 | 1572.5 | 1496.8 | 1510.8 |
| 360 | 1517.6 | 1531.6 | 1476.7 | 1490.7 |
| 390 | 1436.2 | 1450.2 | 1416.1 | 1430.1 |
| 414 | 1423.1 | 1437.1 | 1402.9 | 1416.9 |
| 568 | 1467.7 | 1484.7 | 1467.7 | 1484.7 |
| 768 | 1666.0 | 1688.0 | 1666.0 | 1688.0 |
| 944 | 1678.5 | 1700.5 | 1678.5 | 1700.5 |
| 1280 | 1678.5 | 1700.5 | 1678.5 | 1700.5 |

**Peak 1700.5 (en = zh-HK, 944–1280) → declared height 1750px.**

- One number now covers **both languages** — the old build needed 1650 (zh) / 2000 (en).
  Card geometry converged the two.
- The old `?part=calc` height of **1500px will clip this variant**. That is the cost of
  the uplift: bigger figures, cards with real padding, a step marker per block.
- The Monthly branch adds the month field: peak **1912** at 320 en (1898 en@320, 1879
  at 944+). If the frame cannot grow on state change, declare **1962**; if the host
  applies the widget's `resize` message (INTERFACE §3), 1750 is correct.
- At 390 the frame carries ~300px of ground under the last row, at 320 ~178px. That is
  the unavoidable slack of one height covering 320→1280. A breakpoint pair
  (1625 mobile / 1750 desktop) recovers only 125px; not worth splitting for.

---

## What I refused

- **No logo in the block.** The CMS page carries the Foundation's mark; a logo repeated
  inside every iframe part costs 40px of a fixed frame and adds nothing. Brand is carried
  by colour and type.
- **No side-by-side desktop layout** (see decision 3) — it would halve the desktop height
  and leave a half-empty 1750px frame.
- **No monospace font** for the ladder rates. Tabular figures in the UI face do the job;
  mono outside a code block is a generated-page tell.
- **No gradients, glass, drop shadows, emoji, icon tiles, or decorative shapes** — flat
  colour is the whole point of this direction.
- **No new copy.** No "Your result", no "Step 1 of 2" label, no "Estimated" chip. The
  step numerals are `aria-hidden` presentational marks; the ledger headings are the
  existing `s2.gift` / `s2.saved` / `s2.rate` keys.
- **No structural change to `#payment` or `#receipt`.** Their headings therefore carry no
  step disc — the numbered sequence is the calculation itself (1 give, 2 cost). Adding
  3 and 4 is a one-line wrapper each if the client wants the full sequence, but it was
  out of scope by instruction.
- **No touch to the tax engine** (byte-identical, sha below) or to the two `I18N` tables.

---

## Merge inventory

**Whole `<style>` block replaced** — the cleanest mechanical merge is to take the
`<style>` element from this file entire. What changed inside it:

*Note on `--muted`:* the repo's 02:19 commit darkened it to `#6E6E77` for 5.05:1 on
white. This variant paints an **opaque** `#F3F3F0` ground instead of a transparent frame,
where `#6E6E77` measures only **4.54:1** — a hair over AA at 13px. So take this file's
`--muted:#6A6A75` (5.34 on white, **4.80 on the ground**) and not the parent's value; both
are AA on white, only one is safe on the ground.

*New tokens:* `--ground:#F3F3F0` · `--ink:#16161C` · `--ink-2:#3F3F4A` ·
`--muted:#6A6A75` · `--line:rgba(1,1,78,.14)` · `--line-2:rgba(1,1,78,.26)` ·
`--wash:rgba(1,1,78,.055)` · `--on-navy-2:#C6C8DD` · `--hair-inv:rgba(255,255,255,.22)` ·
`--radius:4px` · `--t-h` 1.375→1.75rem · `--t-num:1.3125rem` ·
`--t-display:clamp(2.75rem,11vw,4.25rem)`.

*New selectors (new classes in markup):*

| Selector | Class in markup | Job |
|---|---|---|
| `.step`, `.step-n` | `step`, `step-n` | flex row; 26px navy disc, white numeral |
| `.card` | `card` | white surface, 1px `--line`, 4px radius, 16–22px padding |
| `.card + .card` | — | 14px between stacked cards |
| `.result` | `result` | the navy panel; padding 20–30px |
| `.result .net-label` | — | 15px `--on-navy-2`, was `.net-label` alone |
| `.net .cur` | — | currency mark on navy (`.32em`, `--on-navy-2`) |
| `.figs`, `.figs > div`, `.figs dd`, `#saved`, `#rate` | — | ledger: `1fr auto` rows, 11px vertical, `--hair-inv` rules |
| `.quick-amt`, `.quick-mo` | `quick-amt`, `quick-mo` | narrow-width grids (4-up / 2-up) |
| `.quick button.is-on` | `is-on` (JS) | filled navy pill = current value |
| `.bands label::before` | — | 3px orange left rule on the selected rung |
| `.bands label:has(input:checked)` | — | `--wash` background, ink text |
| `.seg` (rewritten) | — | 2-cell grid, 46px, navy fill when checked |
| `.amt` (rewritten) | — | bordered field, 1px `--line-2`, inset focus ring |
| `select#months`, `select.band-select` (rewritten) | — | bordered 46px select, navy chevrons |

*Removed / superseded:* `.hero{border-top:…}` (the `hero` class stays on the section,
unstyled) · the `.seg` underline-tab rules and `::after` · the `.amt` bottom-underline
rules · the three-across `.figs` strip and its `max-width:560px` overrides · the
`.bands label:last-child{grid-column:1/-1}` two-column rule (replaced by
`grid-auto-flow:column` + `repeat(5,auto)` so rungs read top-to-bottom, not interleaved).

*Retuned:* `body{background:--ground}`, `html{background:--ground}` · `h2` 700/navy ·
`.btn` 52px, radius 3, weight 700 · `details.q summary` 48px · `.bands` rows 44px with
`--line` hairlines · `.result .hint` recoloured for navy.

**Markup (additions only — no id, no `data-i18n`, no text changed):**

1. `<div class="step"><span class="step-n" aria-hidden="true">1|2</span>…<h2>…</div>`
   wrapping the existing `#s1h` / `#s2h` (both untouched otherwise).
2. `#calculator`: the mode fieldset + amount field + `#months-field` wrapped in
   `<div class="card">`; the income fieldset wrapped in a second `<div class="card">`.
3. `#result`: `#net-label`, `#net`, `#net-caption`, `#announce`, `dl.figs` wrapped in
   `<div class="result">`.
4. `class="quick"` → `class="quick quick-amt"` and `class="quick quick-mo"`.
5. `img src="../assets/logos/*.png"` → `src="assets/logos/*.png"` **in this copy only**
   (it sits beside its own `assets/`; the shipped `embed/` path is unchanged).

**JS (2 insertions, both outside the engine block):**

- `function syncChips(){…}` inserted immediately before `/* ---------- events ---------- */`
  — toggles `.is-on` on `[data-amt]` / `[data-mo]` against `st.amount` / `st.months`.
  Presentation only; it reads the state the engine already owns.
- `syncChips();` inserted in `render()`, immediately before `scheduleHeight();`.

---

## Verification log (all run, not asserted)

| Check | Result |
|---|---|
| Tax engine (`FHF_TAX_ENGINE_START`…`END`) | **byte-identical** — sha256 `4d428aa527adf35b…` in both files |
| Copy parity, `#calculator` + `#result`, both languages | **identical textContent** (1587/620 en, 892/337 zh — same counts as `embed/`) |
| English contains CJK | **0 characters** |
| External requests | **none** (1 request: the document itself) |
| Horizontal overflow | `scrollWidth − clientWidth = 0` at 320/360/390/414/568/768/944/1280, both languages |
| Stress: HK$10,000,000 × 12 months, "Not sure" band, exact income | overflow 0 at 320/390/1280; the figure wraps to 2 lines at 320 rather than overflowing |
| Touch targets ≥44px | every input/select/button/link/summary measured at 320/390/1280 — **no effective target under 44px** (radios are 14px dots inside 44px labels; the segmented radios are visually hidden inside 46px cells) |
| Disclaimer | collapsed by default (`details.open === false`), last visible element at the foot |
| Statutory lines | `#assumption`, `#cap`, `.scope`, `foot.legal`, disclaimer body — all present, unchanged |
| Fonts | one family, system stack; no webfont request |

**Project design gate** (`qa/design_gate.py`, run at `--base http://127.0.0.1:8771` with
`calc` declared at 1750): **0 notes, 0 failures** across contrast, fixed-height fit at
9 widths × 2 languages × 5 parts, tap targets, and the collapsed disclaimer.

```
PASS block heading: 16.93:1 (need 3.0) 28px/700
PASS running text: 9.35:1 (need 4.5) 17px/400
PASS hint / note: 5.34:1 (need 4.5) 13px/400
PASS figure: 18.82:1 (need 3.0) 40px/700
PASS figure label: 11.39:1 (need 4.5) 13px/400
PASS primary action: 6.80:1 (need 4.5) 17px/700
PASS disclaimer summary: 16.93:1 (need 4.5) 15px/500
=== design gate [uplift-b]: 0 notes, 0 failures ===
```

With the shipped `DECLARED["calc"] = 1500` the same gate fails section B at every width
(content 1678 > 1500) — that is the height change, not a defect, and it is why the
number in INTERFACE §2 has to move with this variant.

Screenshots in `shots/`: `calc-<w>-<lang>-h1750.png` are the frame exactly as the CMS
would render it; `content-<w>-<lang>.png` are cropped to content for design review.

---

## Known issue found, not fixed (copy frozen)

In the **Monthly** state the caption concatenates two strings with no separator:
`"…= HK$15,600 for the year." + "Both ends of your range."` renders as
`for the year.Both ends`. It is present in `embed/index.html` too, so it is not a
regression from this round — it is a missing `" "` at the concatenation in `render()`
(`d.cap.monthly` + `d.cap.range`), outside the tax engine. Flagging rather than fixing,
because it changes a rendered string and the copy is frozen.
