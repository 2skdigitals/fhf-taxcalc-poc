# Design review — content hierarchy, vertical rhythm, alignment, type. 23 Nov 2026

Kevin: *"the page works but it does not yet read as a designed document."* This is the measured
review behind that sentence, and the corrections it justified. **Correction, not restyle**: no new
colour, face, shadow, gradient or decorative element, and **not one character of copy changed**.

Applied by `qa/apply_design_review_20261123.py` (30 edits, each asserted to occur exactly once,
re-runnable from `embed/index.html.bak-pre-rhythm-20261123`; `.bak*` is git-ignored, so a fresh clone
restores it from git history).

Method: every number below was read out of the rendered document with `getComputedStyle` and
`getBoundingClientRect` at **390 / 768 / 1440 in both languages**, on `?part=all` (the one-link
arrangement) and on `?part=calc|pay|receipt`. Nothing here is eyeballed.

---

## 1 · Findings

| # | What | Where | Measured (before) | Why it is wrong | Severity |
|---|---|---|---|---|---|
| F1 | A heading sat **flush against the block above it** | `#calculator > .card` → the `2 · …` heading | **0px above, 16px below** | The only inversion in the document. The heading grouped with block 1 and its own card read as unrelated — this is why the page read as a caption stack rather than a document. | **blocker** |
| F2 | Fourteen different gap values, no ratio | whole document | `0 2 6 8 10 12 14 16 18 20 22 26 36` | Fourteen values for four real relationships. Nothing repeats, so nothing groups. | should-fix |
| F3 | Section boundary equal to a sub-gap | `section.panel + section.panel` | **26px** at 390px, vs `.faq` internal gap **26px** | At phone width the step between blocks was the same distance as the gap between a list and its footnote. | should-fix |
| F4 | One measure for two type sizes | `--measure: 34rem` on `.hint` / `.note` / `.assump` / `.fine` | 544px: **84–103ch** at 13px, **64ch** at 17px | The 13px notes ran to 103ch — 1.4× the readable maximum — while the lede sat at 64ch. A fixed px measure cannot serve both sizes. | should-fix |
| F5 | The consent line had no measure at all | `.rform .consent` | **832px ≈ 128ch** | Longest line on the page, and it is the legal sentence a donor has to actually read. | should-fix |
| F6 | Rates under the caption floor | `.bands .r` | **11px** vs the 13px band label | The rest of the system's smallest step is 12px; 11px is a size that exists nowhere else. | should-fix |
| F7 | Form rows at two different rhythms | `.rform > p.fine`, `.rform > p.hint` | **36px** from the consent, **28px** under the button, every other row **20px** | Inside a grid the gap and a child margin **add**. The caveat on the consent was further from it than the submit button was. | should-fix |
| F8 | Legal footer attached to the form | `.wrap > p.fine` | **14px** under the receipt block | Three pixels more than a paragraph-to-caption gap: it read as the receipt form's last line, not the document's close. | should-fix |
| F9 | Hover state pointed at a colour that does not exist | `.swap:hover{color:var(--orange-ink)}` | `--orange-ink` **defined nowhere** | Invalid at computed-value time, so the control had **no hover state at all**. | polish |
| F10 | Payment tiles: **verified correct** | `.paygrid` | left 304 / 580 · top 1821 both · inner box 190×148 both · caption top 1980 both | They *do* align at top, bottom and caption baseline, and the caption blocks are the same width. No defect. | — |
| F11 | Two 190px tiles in 244px columns | `.paygrid` | declared gap **32px**, visible gap **86px** | 54px of dead track in each column. The pair reads further apart than the 32px gutter used between every other pair of things. | judgement |
| F12 | The amount field outranks its heading | `.amt input` vs `h2` | **32px/700** navy vs **28px/700** navy | Deliberate — the gift is the subject of block 1 — and it works. Listed so it is not "fixed" later by mistake. | no change |
| F13 | Monthly caption is one 75-character sentence | `#net-caption` | **79ch** on one line; constrained to 68ch it breaks into two lines of **~37ch** | Over the 72ch rule either way. The honest fix is a shorter sentence, which is a copy change. | judgement |

### Left edges, measured at 1440px

Only **two** left edges exist, and every element belongs to one of them. No 1–8px drift anywhere:

| Edge | x | What sits on it |
|---|---|---|
| the column | **304** | section headings, step numerals, ledes, hints, notes, the result panel, the payment grid, the receipt form and its labels, both footers |
| inside a surface | **327** | card content (304 + 22 padding + 1 border): segmented control, field labels, amount box, hint, band ladder |
| | **334** | result-panel content (304 + 30 padding): the figure, its caption, the ledger |

The column itself is `.wrap` at **272 → 1168**, i.e. **896px** with 32px gutters, as specified.

### Type scale, measured at 1440px

`12 · 13 · 15 · 17 · 19 · 21 · 28 · 40` plus the 32px amount field (22px at 390). Every step is a
token except `.figs dd`'s phone override (19px), which is a deliberate responsive reduction.
Hierarchy is carried on **two or three axes** at every level — e.g. field label 13/600/dark ink vs
hint 13/400/muted (weight **and** colour); ledger label 13/400/navy-2 vs figure 21/600/white (size,
weight **and** colour); eyebrow 13/600/uppercase/tracked/muted vs its summary 15/500/navy (four
axes). No level is distinguished by one axis alone.

CJK leading is identical to Latin at every step (body 1.6, lede 1.5, hint 1.55, h2 1.14) — the
Chinese is not tighter than the English anywhere. The one place Chinese is shorter is the payment
lede (1 line vs 2) and the consent (1 vs 2), which are correct reflows, not holes.

---

## 2 · What changed (before → after)

| Fix | Before | After | Why |
|---|---|---|---|
| **F1** the inversion | `.step{margin:0 0 16px}` only | `.card + .step{margin-top:24px}` | 24px above, 16px below: the heading now binds to its own card at 1.5× the distance it holds from the block above. **Verified in the DOM: above 24 / below 16, both languages, 390 → 1440.** |
| **F2** the scale | 14 ad hoc values | `--s2:8 --s3:12 --s4:16 --s5:20 --s6:24 --s7:32` on every block gap | Four tiers: caption-under-figure 8, paragraph-to-paragraph 12, unit-to-unit 16–20, block-to-block 32–36. Optical values *inside* one surface (a caption 6px under its own figure) were left alone — a scale governs the rhythm between blocks, not the kerning of a panel. |
| **F3** the boundary | `clamp(26px,4.4vw,36px)` | `clamp(32px,4.4vw,36px)` | 32px floor at phone width, so the section step is always larger than the 24px largest internal gap. Desktop is unchanged at 36px. |
| **F4** the measure | `--measure:34rem` = 544px always | `--measure:34em` | The var is substituted where it is used, so it resolves against each element's own size: **68ch at 13px, 17px and 19px alike.** The 103ch note is now 68ch; the 64ch lede is 68ch. |
| **F5** the consent | no `max-width` | `max-width:var(--measure)` | 832px → 442px: two lines of 68ch in English, one line in Chinese. |
| **F6** the rates | 11px | `var(--t-eyebrow)` = 12px | Back on the smallest step the system already uses. |
| **F7** the form rhythm | 20 / 36 / 28 | 20 / 20 / 20 | `.rform > *{margin-top:0}` — the grid gap governs, nothing doubles it. |
| **F8** the footer | 14px | 24px | The document's legal line stands off the last block by more than a paragraph stands off its own caption. |
| **F9** the dead hover | `color:var(--orange-ink)` (invalid) | `text-decoration-thickness:2px` | A hover cue with no colour change: `--orange-h` on white is **3.6:1 at 15px**, so binding the intended colour would have introduced an AA failure. The cue is weight, not colour. |

Two supporting tokenisations: the band label moves from a literal `.8125rem` onto `var(--t-cap)`,
and `.min-note`'s padding from `14px` to `16px`.

---

## 3 · Heights (contractual)

**Every declared height is unchanged** — `calc 1800 · input 1040 · result 890 · pay 580 ·
receipt 810 (zh) / 910 (en) · all 2880 / 2990`. No CMS edit is required.

| Block | zh peak before → after | en peak before → after | Declared | Slack now (zh / en) |
|---|---|---|---|---|
| `?part=calc` | 1722 → **1770** | 1742 → **1790** | 1800 | 30 / **10** |
| `?part=input` | 974 → **1004** | 974 → **1004** | 1040 | 36 / 36 |
| `?part=result` | 833 → **843** | 833 → **843** | 890 | 47 / 47 |
| `?part=pay` | 477 → **479** | 503 → **505** | 580 | 101 / 75 |
| `?part=receipt` | 746 → **746** | 852 → **852** | 810 / 910 | 64 / 58 |
| `?part=all` | 2765 → **2803** | 2878 → **2936** | 2880 / 2990 | 77 / 54 |

`?part=receipt` did not move at all: +24px of new form spacing was exactly cancelled by removing the
per-child margins that were doubling the grid gap.

**`?part=calc` in English now sits 10px under its 1800px declaration** (it was 58). It fits, measured,
at all 22 widths — but that is the slimmest margin in the document, and the next addition to that
block should reissue it to 1830 rather than assume the old headroom. Recorded in `docs/INTERFACE.md` §2.

---

## 4 · Gates

| Gate | Result |
|---|---|
| `qa/test_tax_engine.py` | **6/6** verified examples exact, 0 failures |
| `qa/verify_six_examples.py` / `--lang en` | **6/6** exact, 0 mismatched, both languages |
| `qa/poc_test.py` | **75 passed, 0 failed** |
| `qa/sweep_heights.py` / `--lang en` | 6 blocks × 22 widths × 3 states, **no overflow**, both languages |
| `qa/lang_parity.py` | **14 passed, 0 failed** (zh rendered strings byte-identical; no CJK in the en build; no amount/rate in any payload) |
| `qa/design_gate.py` | **0 notes, 0 failures** (contrast, height fit, touch targets, assets, disclaimer) |

---

## 5 · Judgement calls left to Kevin

**J1 · The payment pair's gutter.** The two tiles are 190px inside 244px columns, so the visible gap
is **86px** while the declared gutter — used everywhere else — is **32px**.
· *A, fill the columns:* `max-width:100%` on the tile → 244×190 each, gutter 32px for real, captions
stay one line, the two tile bottoms stay level. Costs **+42px** on `?part=pay` (479 → 521 / 505 →
547, still inside 580) and makes the QR 28% larger, which scans better off a laptop screen.
· *B, leave it:* the alignment test passes as it is; nothing is broken, the pair is merely airier than
the rest of the document.
· **Recommendation: A** — it is the one place where the spacing is measurably not what the CSS says.

**J2 · The monthly caption sentence.** `HK$1,300 a month × 12 months = HK$15,600 for the year. Both
ends of your range.` is 75 characters: 79ch on one line, and two 37ch lines if constrained (both
outside the 45–72 window). It is currently left at the panel's measure.
· *A, trim the copy* to about 55 characters, e.g. `HK$1,300 a month — HK$15,600 a year.` → one line at
68ch and −19px off the tightest block.
· *B, leave it.*
· **Recommendation: A**, but it is the client's sentence and this pass changed no copy.

**J3 · `--t-lede`.** The token exists (17→19px) and is applied only to `.benefit`; `.lede` is
17px. Promoting the lede to 19px would give section intros more weight but would collide with the
heading at phone widths (19 + 19 vs a 22px h2).
· **Recommendation: leave it.** The lede is already separated from its hints by size *and* colour.

**J4 · The band ladder at 721–768px.** Nine nowrap rows in two columns; at 768 the widest row is
~293px against a ~293px track. Measured clean at all 22 widths, but a longer band label from the IRD
would crowd it.
· **Recommendation: leave it**, and re-measure if the tax bands are re-cut.

**J5 · The orange rate figure inside the navy panel.** `Tax saved` is orange while `Rate used` is
white, which gives the panel three emphasis levels (the display number, the orange figure, the
ledger). It is the client's own "positive saving" emphasis from the 20 Nov pass.
· **Recommendation: leave it** — it is brand intent, not a defect.

---

## 6 · What was deliberately not touched

Colour tokens, the type family, radii, borders, the navy result panel, the orange action, the 896px
column, the eight analytics events, `?part=` routing, and every string in both languages. The design
language is identical; only the distances and two measures changed.
