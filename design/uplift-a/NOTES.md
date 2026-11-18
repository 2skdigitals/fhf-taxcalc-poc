# Uplift A — "warm brand editorial"

Fred Hollows HK donation tax calculator · `?part=calc` · one file, no new requests.
Built from `HEAD:embed/index.html` (commit `2f1ba91`), which is also the baseline every
number below is measured against.

---

## 1 · The design read

The client said "just a bunch of black text", and the screenshot agrees with them. Opened at
390 and 1280 the block had **no colour at all** — not one pixel of brand orange or navy in the
calculator or the result. What was actually wrong, in order of damage:

1. **One surface for everything.** Input, controls, ladder and result all sat on the same
   ground, separated only by 1px rules at 12% alpha. Nothing told the eye where the question
   ended and the answer began. The section rule between them was invisible in practice.
2. **Three competing headings and no hero.** "Your gift" (24–32px), "What it costs you"
   (24–32px) and the figure (40–56px) were within 1.7× of each other, and all three were the
   same near-black. The number a donor came for lost the argument to two labels.
3. **Controls that were trying not to be controls.** Quick amounts were bare text separated
   by inset hairlines; one-off/monthly were document tabs with an underline; the income ladder
   was a 9-row hairline spreadsheet whose last rung spanned both columns and left a 200px
   hole. Each was tasteful on its own and collectively they read as a form from a spec
   document rather than a gift page.
4. **Numbers that did not line up.** The three supporting figures were equal thirds with
   vertical rules between them, so "−HK$182 to −HK$221" nearly touched its divider and no two
   values shared an edge.
5. **No emphasis tier.** Every secondary line was the same grey, so nothing in the block could
   be skimmed; you had to read it.

Type, rhythm and restraint were already good. The uplift does not replace them — it gives them
a surface to sit on and a colour system to speak with.

---

## 2 · The three decisions that carry the uplift

**① Two shallow surfaces, no shadow.**
The result becomes a full-bleed warm band (`--tint #FBF3EA`, a 1.10:1 tone step from white)
and the controls sit in a recessed well (`--well #F5F1EA`). The ladder becomes a white card
with a hairline. That is the whole material system: **white ground / recessed well / warm
band**, three tone steps, zero shadows, zero gradients. The band bleeds edge to edge with
`box-shadow:0 0 0 100vmax` + `clip-path:inset(0 -100vmax)` so it is a section, not a card, and
it cannot produce a horizontal scrollbar (measured: `scrollWidth == clientWidth` at every
width from 320 to 1280).

**② The figure is the hero, and the numbers share one column.**
The "you pay" figure goes to `clamp(3rem, 9.4vw, 4.25rem)` (48→68px) in **navy**, with the
currency mark cap-aligned at `.34em` instead of set on the baseline (at 48px a baseline "HK$"
reads as a footnote). Below it the three supporting figures stop being a three-column strip and
become a **receipt**: label left, value right, every right edge on one numeric column, one rule
per row. The saving is the only coloured number in the block.

**③ One control language, and orange earns its place.**
Quick amounts are filled pills; one-off/monthly is a real segmented track; both mark selection
the same way — **navy fill, white type** (18.82:1). The income ladder is a card, and its
selected rung is marked by a warm row, a 3px orange left rule and an orange radio. Selection in
a *control* is navy; the active *row* and the money in the result are orange. That split is why
the block reads as a sequence of choices feeding one answer rather than a pile of widgets.

A fourth, quieter move: the sequence marker. The direction asked for "Step 1 / Step 2"
eyebrows. Copy is frozen and no such string exists in either table, so the eyebrow is a
**numeral set in CSS** (`#s1h::before{content:"1"}`), in orange, at cap-size beside the heading.
It carries the order, translates into nothing (both languages use the same digits), adds no
copy, and disappears when its section is the only one in the frame (`?part=input`,
`?part=result`). One caveat to know before an a11y review: generated content is exposed by some
screen readers, so the heading may be announced as "one, Your gift". It is an ordinal, it is
true, and it stays silent in VoiceOver/NVDA in practice — but if that is unacceptable the fix is
the copy table, not the CSS.

---

## 3 · Contrast, measured (not estimated)

Every text pair in the calc block, computed from the final tokens:

| pair | ratio | verdict |
|---|---|---|
| ink #232323 on white / tint / well | 15.72 / 14.30 / 13.96 | AA |
| ink-2 #4E4E58 on white / tint / well | 8.22 / 7.48 / 7.30 | AA |
| muted #6B6B74 on white / tint / well | 5.28 / 4.80 / 4.69 | AA |
| navy #01014E on white / tint / well | 18.82 / 17.13 / 16.72 | AA |
| white on navy (selected pill, chip) | 18.82 | AA |
| orange-ink #AE4E0E on white / tint / well | 5.39 / 4.91 / 4.79 | AA |
| on-action #0A0909 on orange #E97824 (the CTA) | 6.80 | AA |
| navy on orange | 6.43 | AA |
| radio ring #8A8A99 on white / tint | 3.40 / 3.09 | AA non-text (3:1) |

**The finding that shaped the palette:** brand orange `#E97824` measures **2.93:1 on white and
2.66:1 on the tint**. It fails AA at every size, including the 3:1 large-text floor — so the
brand orange literally cannot carry type in this block. It survives as the CTA fill only
(dark ink on it: 6.80). Everything orange that must be *read* — the numerals, the saving, the
selected rung's rule, the chevrons — uses `--orange-ink #AE4E0E`, the same hue taken dark
enough to pass (4.79–5.39 on all three surfaces). White on orange is also 2.93 and is not
used anywhere.

Also fixed while measuring: the unselected radio ring was `#9A9AA8` = **2.78:1**, under the
3:1 non-text floor; it is now `#8A8A99` = 3.40. And `--muted` moves from `#76767F` (4.50 on
white, a hair over the line) / HEAD's `#6E6E77` (4.59 on the new tint) to `#6B6B74`
(5.28 white / 4.80 tint / 4.69 well) so 13px grey is safe on all three surfaces.

Two pairs deliberately below 4.5: `--tint` and `--well` against white are 1.10 and 1.13 — they
are surface tone steps, not information boundaries, and nothing is conveyed by them alone.

---

## 4 · What I deliberately refused to do

- **No invented copy.** Not one string was added, cut or reworded, and no label explains a
  visual. Proof, not assertion: `document.body.innerText` in `?part=calc` is **line-for-line
  identical to HEAD in both languages** (51 lines, en and zh-HK), and the combined text of the
  whole block is unchanged byte for byte.
- **No "Step 1" / "Step 2" words.** They do not exist in the copy table, so the visual is a
  numeral, not a label. If the client wants the literal words, that is a copy-table addition
  for them to approve, not something this round may invent.
- **No webfont.** The system stack is what the Foundation's own page uses; swapping in a display
  face would be a new external request and would change the zh-HK face. Hierarchy was bought
  with scale, weight and colour instead of a typeface.
- **No gradients, glass, emoji, icon sets, or shadows at rest.** The one `box-shadow` in the
  file is the full-bleed technique, clipped to a hard edge on both sides — it is a background
  paint, not a shadow you can see. The one gradient in the original file (the two 6px slivers
  faking a select chevron) is replaced with an inline SVG data URI.
- **No dark mode, no motion beyond state feedback.** 160ms colour transitions on controls;
  nothing moves layout. `prefers-reduced-motion` is honoured.
- **No touching the payment or receipt blocks.** Proven: `?part=pay` and `?part=receipt`
  render to **0.0px height delta against HEAD at all eight widths** in both languages. The
  shared `h2` rule, the frame padding and the button restyle are all scoped to
  `#calculator` / `#result` / `body[data-part="calc|input|result"]`.
- **No widening of the 40rem column.** I tried it (45rem for calc parts would have let the
  ladder keep 13.5px type) and rejected it: prose is capped at `--measure` 34rem, so a wider
  column would have left the right third of every paragraph empty and the data would have
  drifted away from the text. The column stays 40rem; the ladder pays for it in type size
  (below).
- **No shrinking of statutory content to fit height.** The band note, the 35% cap line, the
  assumption line, the scope line and the legal footnote are all still there at their own size.

---

## 5 · Measurements

`?part=calc` — true content height (bottom of the last visible element, not `body` min-height;
the collapsed `<details>` panels are excluded from the measurement so they cannot inflate it):

| width | HEAD en | A en | Δ | HEAD zh | A zh | Δ |
|---|---|---|---|---|---|---|
| 320 | 1358.6 | **1424.0** | +65.4 | 1337.8 | 1399.2 | +61.4 |
| 360 | 1358.6 | 1420.0 | +61.4 | 1317.7 | 1379.0 | +61.3 |
| 390 | 1272.2 | 1332.7 | +60.5 | 1252.1 | 1338.1 | +86.0 |
| 414 | 1272.2 | 1332.7 | +60.5 | 1252.1 | 1312.6 | +60.5 |
| 568 | 1200.1 | 1323.7 | +123.6 | 1200.1 | 1323.7 | +123.6 |
| 768 | 1404.8 | 1537.4 | +132.6 | 1404.8 | 1537.4 | +132.6 |
| 944 | 1446.9 | 1574.3 | +127.4 | 1446.9 | 1574.3 | +127.4 |
| 1280 | 1446.9 | **1588.6** | +141.7 | 1446.9 | **1588.6** | +141.7 |

**Peak = 1588.6px (en and zh-HK, at 944 and 1280). → Declare 1640px.**
(`peak + 50` = 1638.6; 1640 also clears the document's own bottom padding, `scrollHeight`
1615, so no vertical scrollbar appears at the declared height — verified: at 1640 the
`scrollHeight` equals the viewport at all eight widths.)

Where the height went, and why it is worth it: the receipt ledger (+60 at ≥561px, where the
three figures went from one row to three), the band's own padding (+16), the bigger figure
(+12), the 46px card rows (+10), the segmented track (+8). Mobile 320–414 costs only +60, most
of it the band's padding and the card-shaped select.

**Peak varies 265px across breakpoints** (1324 at 568 vs 1589 at 1280) because the ladder is a
9-rung card on desktop and a native select on phones. If the CMS can take a media-query height,
use **1400 below 721px and 1640 above** — that recovers ~240px of dead frame on phones. A
single declared height must be 1640.

Other checks, at all eight widths, both languages:

- horizontal overflow: **none** (`scrollWidth == clientWidth` everywhere, incl. 320);
- CJK characters in English: **0**;
- interactive targets: every button, link, select, summary and row label ≥44px
  (the only sub-44 boxes are the two `flabel` captions, which are labels for their own
  54px inputs, not standalone targets);
- requests on load: **1** (the document) — no fonts, no CDN, no libraries, identical to HEAD;
- tax engine between `FHF_TAX_ENGINE_START/END`:
  `sha256 a8b17d3a…ae945`, **byte-identical to HEAD**;
- copy table (`var I18N = {` … `var L = "zh-HK"`): **byte-identical to HEAD**.

Screenshots in `shots/`, captured at the declared 1640px, 2× device pixel ratio, full frame:

| file | bytes | pixels |
|---|---|---|
| `calc-390-en.png` | 233,754 | 780×3280 |
| `calc-390-zh-HK.png` | 258,554 | 780×3280 |
| `calc-1280-en.png` | 335,504 | 2560×3280 |
| `calc-1280-zh-HK.png` | 361,890 | 2560×3280 |

`shots/before/` holds the same four frames of `HEAD` for comparison.

---

## 6 · Merge: every selector touched

Nothing in `<body>` changed. The whole diff is **three things**: the `:root` token block, one
appended CSS block, and one JS function plus its call.

### Tokens (`:root`)

| token | value | status |
|---|---|---|
| `--orange-ink` | `#AE4E0E` | **new** — the only orange legal as text |
| `--tint` | `#FBF3EA` | **new** — the result band |
| `--well` | `#F5F1EA` | **new** — recessed control surfaces |
| `--well-2` | `#EDE6DA` | **new** — control hover |
| `--muted` | `#6B6B74` (was `#76767F` in my snapshot; HEAD has `#6E6E77`) | changed — 5.28 on white, 4.80 on tint |

Everything else in `:root` is untouched.

### The appended block

Delimited by `/* UPLIFT-A:START */` … `/* UPLIFT-A:END */` at the end of `<style>`. It overrides
the sheet above it, so it must stay last. Selectors it adds or re-states:

**Sequence marker**
`#s1h::before`, `#s2h::before`, `#s2h::before` (content override),
`body[data-part="input"] #s1h::before`, `body[data-part="result"] #s2h::before`

**Heading (scoped)**
`#calculator h2`, `#result h2`

**Frame**
`#calculator`, `body[data-part="calc"] .wrap`, `body[data-part="input"] .wrap`,
`body[data-part="result"] .wrap`

**Segmented control**
`.seg`, `.seg label`, `.seg label:has(input:checked)`, `.seg label:has(input:checked)::after`,
`.seg label:has(input:focus-visible)`, `@media(hover:hover)and(pointer:fine) .seg label:hover`,
`.seg label:has(input:checked):hover`

**Amount + chips**
`.field`, `.amt`, `.amt .pre`, `.amt input`, `.quick`, `.quick .qlab`, `.quick button`,
`.quick button + button`, `.quick button[aria-pressed="true"]`,
`@media(hover)… .quick button:hover`, `.quick button[aria-pressed="true"]:hover`,
`@media(max-width:400px) .quick`, `@media(max-width:400px) .quick button`

**Income ladder**
`.bands`, `.bands label`, `.bands label:last-child`, `.bands label:has(input:checked)`,
`.bands input`, `.bands input:focus-visible`, `.bands input:checked`, `.bands .r`,
`.bands label:has(input:checked) .r`, `@media(hover)… .bands label:hover`,
`.bands label:has(input:checked):hover`, `@media(min-width:721px) .bands`,
`@media(min-width:721px) .bands label`,
`@media(min-width:721px) .bands label:not(:last-child):nth-child(odd)`

**Selects**
`select.band-select`, `select.band-select:focus`, `select#months:focus`,
`select#months,select.band-select` (chevron data URI), `select#months`, `select#months:focus`

**Result band + figure**
`#result`, `#result .net-label`, `#result .net`, `#result .net .cur`, `#result .net.is-range`,
`#result .hint`

**Receipt ledger**
`#result .figs`, `#result .figs > div`, `#result .figs > div:last-child`, `#result .figs dt`,
`#result .figs dd`, `#result .figs dd.is-range`, `#saved`

**Statement / notes**
`#result .benefit`, `#result .assump`, `#result .assump + .assump`, `#result .scope`

**Disclosures**
`details.q`, `details.q summary`, `details.q summary::before`, `details.q summary:hover`,
`#result details.q`, `#disclaimer summary`

**Action**
`#calculator .gotoline`, `#calculator .btn`, `#calculator .btn:active`

**Interaction**
`:focus-visible`, `::selection`, `@media(prefers-reduced-motion:reduce)` (the three controls)

### JS (outside the engine, outside the copy table)

```js
function syncChips(amount, months){ … }   // sets aria-pressed on [data-amt] and [data-mo]
syncChips(once, months);                  // one call at the end of render()
```

It writes an attribute and nothing else: no copy, no figure, no state the engine reads. It is
what lets a quick pick read as "on" while the field holds its value. Remove those two lines and
the chips simply never show a selected state; nothing else changes.

---

## 7 · Defects found, not fixed (outside this round's scope)

1. **Two sentences run together in the monthly caption.** `render()` concatenates
   `d.cap.monthly` and `d.cap.range` with no separator, so the caption reads
   `HK$1,300 a month × 6 months = HK$7,800 for the year.Both ends of your range.` Present in
   HEAD, both languages. It is a one-character fix in the render path, but it edits a string's
   rendering, so I left it for the copy round rather than silently changing frozen copy.
2. **`?part=input` and `?part=result` leave ~300px of empty frame** at the declared height,
   because one height serves every part. Same in HEAD; worth a per-part height in the CMS
   config.
3. **The 35%-cap and accounting wording** in `#assumption` / `#cap` still uses the same
   `--ink-2` as the statement above it in HEAD; I moved them to `--ink-2` deliberately so the
   statement keeps the only full-ink line. If the client wants the statutory lines to read at
   equal weight, that is a copy-hierarchy decision, not a style one.
