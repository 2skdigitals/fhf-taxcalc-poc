# Direction B — product-grade fintech · design notes

`index.html` is a self-contained build of the Fred Hollows HK donation-tax calculator, same
`?part=` contract, same tax engine (byte-identical between `FHF_TAX_ENGINE_START` and
`FHF_TAX_ENGINE_END`), same two string tables — restyled and re-worded as a fintech tool a donor
trusts rather than a charity card stack.

---

## 1. The design read

The donor is one person, mid-decision, eight times out of ten on a phone. They have already decided
to give; what they have not decided is **what the gift actually costs them**. So every block answers a
money question in the first thing the eye lands on:

- the order pad answers *"what do I put in?"* with four controls and one visible rate ladder;
- the estimate answers *"what does it cost me?"* with a single figure;
- the rails answer *"how do I pay?"* with three names;
- the receipt form answers *"how do I get the paper?"* with three fields.

The register is a bank's transfer confirmation: a receipt-shaped panel, hairline rules, tabular
figures, a chip for the rate, and the small print one tap away. Nothing on the page is a marketing
surface, so nothing on it is styled like one.

**The idea, in one sentence:** *the deduction is presented as a receipt being written for this donor
— one figure, two line items, the rate as a stamp — and the rate ladder that produces that figure is
always visible beside the input, in two named tiers, so the fall from 17% to 15% is structural rather
than a footnote.*

---

## 2. The three decisions that carry the improvement

### 2.1 The estimate is a receipt panel, not a three-up figure strip

One bordered panel inside the card. Inside it, in reading order: the label with the rate as a chip
(`Rate 14% – 17%`), the figure at `clamp(34px, 9vw, 48px)` in navy with tabular figures, one benefit
line, one source line, **two** hairline-separated line items (donation, tax saved), and the 35% cap
line. Everything that used to compete with the figure — the "this is the amount you actually pay"
caption, the assumptions block, the cap paragraph, the scope sentence — is now one short line, one
44px disclosure row, or the scope fine print at 12px.

Why it carries: the old block had a 36px figure and a three-across strip with three numbers of the
same weight, so nothing was the answer. The strip is now a receipt's line items — 17px, right-aligned,
one right edge — and the figure is the only thing at 48px on the block.

### 2.2 One rate ladder, two tiers, visible at every width

The nine bands are one radio group laid out twice: the seven progressive rungs (including
*Not sure — show a 2%–17% range*) under `Assessable income, before allowances (HK$)`, then a
`Standard rate (replaces the progressive rates)` subhead and the two standard-rate rungs. Labels are
compact (`345k–2.1M`), rates sit in their own right-aligned column (`~17%`, `15%`, `16%`), and the
selected rung is a navy-tinted row with a filled radio and bold label.

Why it carries: the old build had two different controls for one choice — nine radio rows above
720px, a native `<select>` below it — so the ladder was invisible on the phone, where most donors are,
and the 17%→15% drop looked like a bug that a 180-character note had to apologise for. Now the drop
is a labelled tier, the note is two sentences, and there is one control and one source of truth in
the DOM. Two columns from 380px (where the longest label and its rate still fit side by side); a
single column below it, because breaking `145–` / `195k` across lines is worse than the height.

### 2.3 Each block is one job, and the job's control is first

- **Rails**: three 74px tiles, the wallet name at 20px/600 in navy, the destination in 13px, a
  hairline chevron. Above 600px the name gets its own 150px column and the descriptor joins it on the
  line, so a 674px row reads as a list of methods instead of a mostly empty box.
- **Receipt form**: one hairline card, 46px inputs, one 50px orange action with navy type (≈8:1),
  a consent row whose box aligns with its first text line, and the disclaimer as the last row of the
  card — one affordance, not a link plus a duplicate row. Exactly three required fields plus consent.
- **Order pad**: a native-feeling segmented control (white thumb, navy label, 44px, 120ms), one
  52px amount field with the number at 24px in tabular figures, four 44px quick amounts on one line,
  then the ladder. The amount field is the only input with a big number in it, because it is the only
  number the donor types.

---

## 3. What I deliberately refused

| Refused | Why |
|---|---|
| A new palette, a second typeface, a webfont | Brand tokens only: orange `#E97824` on the action, navy `#01014E` on every authoritative number, warm off-white ground, hairline borders. The system stack is the type system. Nothing is fetched. |
| Orange on money figures, tabs, or headings | Orange appears on the primary action and the focus ring only. At 3.0:1 on white it fails as text; using it as a second signal would also make colour the only distinction between "saved" and "paid". Signs and position carry that. |
| Re-adding the PayMe / AlipayHK QR panels | The merchant codes do not exist; the three rails are links to `hollows.org` and nothing else. `assets/qr-*.svg` is left in place and unreferenced. |
| Deleting any fact to hit the character target | Visible body copy fell 46–62%, and the characters that left the surface went into `<details>` (calc hidden text 446 → 775, receipt 603 → 630). The wordiness was solved by hierarchy, not amputation. |
| Keeping the standard-rate note as a collapsed row | The brief requires it visible beside the picker; a ladder whose top two rungs fall without an adjacent reason reads as a bug. It is now two sentences *plus* a named tier. |
| Entrance animations, scroll reveals, counters | This is an app screen, not a page. Motion is feedback only: 100–130ms on hover, press (`scale(.97)` on chips, `.985` on the action), focus rings, and the disclosure chevron. Nothing performs on load, so nothing can be caught mid-frame in a fixed-height iframe. |
| Gradients, glass, icon sets, emoji, a "step 1 / step 2" eyebrow system | All banned by the brief and by the house rules. The only drawn mark is a 1.6px stroke chevron and a data-URI tick on the consent box. |
| Changing the default band (`r17`) or any engine constant | Out of scope and out of bounds. The engine block is byte-identical (1,966 bytes, checked). |
| Making the range disappear by inventing a point estimate | When a band is chosen the range is real (both ends are worked). The hero shows the range and the source line names why. |

---

## 4. Measurement

Content height = `#root`'s box height with the part-mode `min-height` neutralised (playwright,
Chromium, DPR 1). Declared height = peak + 40–70px, one number per block per language.

### Recommended declared heights

| block | lang | peak content | at | recommended | slack at 390 | slack at 1280 |
|---|---|---|---|---|---|---|
| `calc` | en | 1716 | 320 | **1780** | 341 | 417 |
| `calc` | zh-HK | 1568 | 320 | **1630** | 300 | 303 |
| `pay` | en | 376 | 320 | **440** | 64 | 82 |
| `pay` | zh-HK | 376 | 320 | **440** | 64 | 82 |
| `receipt` | en | 646 | 320 | **710** | 104 | 201 |
| `receipt` | zh-HK | 572 | 320 | **640** | 68 | 151 |

Declared heights describe the **collapsed** state. Each opened disclosure adds ~70–100px; the frame
posts a `resize` on every toggle, and at 390px the `calc` block's 341px of slack absorbs both the
assumptions and the facts disclosures without exceeding 1780.

The two half-blocks the CMS may also embed:

| block | lang | peak content | at | recommended |
|---|---|---|---|---|
| `input` | en | 1008 | 320 | **1070** |
| `input` | zh-HK | 934 | 320 | **1000** |
| `result` | en | 597 | 320 | **660** |
| `result` | zh-HK | 558 | 320 | **620** |

`part=result` is the one place a disclosure can outgrow its declared height (opening *What counts*
adds ~150px at 390); all three primary blocks have room for it.

The peak for every block is at **320px**, and for `calc` it is the single-column ladder (the two
column layout cannot hold `345k–2.1M` + `~17%` inside a 137px cell without breaking the range in
half). If the CMS can set a height per breakpoint, use **1500 / 1400** for `calc` at ≥380px and the
same `pay` / `receipt` numbers; the 320 fallback stays as declared.

### Content height, before → after (px)

| block | 320 | 390 | 568 | 768 | 1280 |
|---|---|---|---|---|---|
| calc en | 1938 → 1716 (−222) | 1752 → 1439 (−313) | 1443 → 1358 (−85) | 1533 → 1363 (−170) | 1488 → 1363 (−125) |
| calc zh | 1591 → 1568 (−23) | 1484 → 1330 (−154) | 1232 → 1304 (+72) | 1427 → 1327 (−100) | 1404 → 1327 (−77) |
| pay en | 531 → 376 (−155) | 487 → 376 (−111) | 453 → 376 (−77) | 441 → 358 (−83) | 446 → 358 (−88) |
| pay zh | 449 → 376 (−73) | 449 → 376 (−73) | 429 → 376 (−53) | 441 → 358 (−83) | 446 → 358 (−88) |
| receipt en | 836 → 646 (−190) | 790 → 606 (−184) | 606 → 572 (−34) | 592 → 509 (−83) | 524 → 509 (−15) |
| receipt zh | 706 → 572 (−134) | 681 → 572 (−109) | 556 → 551 (−5) | 524 → 489 (−35) | 499 → 489 (−10) |

`calc zh @568` is the one block that grew: the tablet breakpoint used to get a native `<select>`, and
now shows the whole ladder. That is the trade the brief asks for.

### Visible body characters (text nodes only, collapsed `<details>` excluded, measured at 390px)

| block | lang | before | after | Δ | hidden in `<details>` |
|---|---|---|---|---|---|
| calc | en | 1586 | 823 | −48.1% | 446 → 775 |
| calc | zh-HK | 789 | 411 | −47.9% | 187 → 312 |
| pay | en | 277 | 145 | −47.7% | 0 → 0 |
| pay | zh-HK | 129 | 49 | −62.0% | 0 → 0 |
| receipt | en | 584 | 304 | −47.9% | 603 → 630 |
| receipt | zh-HK | 203 | 110 | −45.8% | 178 → 187 |

---

## 5. Fact audit — where every required fact lives now

| fact | where |
|---|---|
| 35% cap on assessable income, for the year | visible `#cap` line under the two receipt rows on every state; `foot.legal`; the cap is applied by the engine |
| HK$100 annual-total receipt threshold | receipt lede, first sentence after the heading |
| six-year retention | result card → **What counts** disclosure |
| s.88 approved charity | result card → **What counts**; "recognised charitable donation" in the benefit line while under the cap |
| non-deductible list | result card → **What counts** |
| spouse: unused deduction claimable by spouse, itself capped at 35% of the spouse's own income | result card → **Can a couple combine the deduction?** |
| "not tax advice" | visible under the disclosures (`s2.scope`), and again in the disclaimer body |
| standard rate: 15% on the first HK$5M, 16% above, so the top two rungs go DOWN | visible note beside the ladder + the `Standard rate` tier subhead + the two rung rates |
| 31 March year-of-assessment end | result card → **What counts** |
| disclaimer text | receipt card → last disclosure row, text unchanged |
| three required fields + consent | receipt form (name, email, payment reference, consent) — no fourth field added |

**Four of those facts were not in the delivered copy**: s.88, the non-deductible list, the six-year
retention, and the 31 March year end. They are in the brief's must-survive list, so they are written
into the **What counts** disclosure in both languages and need the client's sign-off on wording.

---

## 6. Needs the client's confirmation

1. **The four added legal lines** above (worded to IRD vocabulary, not lifted from a page).
2. **Compact band labels** — `145–195k`, `345k–2.1M`, `5M and up` — with the exact figures kept in the
   assumption line (`HK$345,000 – 2,132,500`) and the note (`about HK$2,132,500`).
3. **Rail subtitles** are all "the Foundation's donation page", because all three rails open that one
   page; when merchant QR codes exist this becomes the tile that carries them.
4. **`?h=` / `data-fit="fixed"`** is honoured as before, but the block now reports its own content
   height honestly (no `min-height:100vh`), so the host height should be the declared number above.

---

## 7. How to test

```bash
cd design/product && /Library/Developer/CommandLineTools/usr/bin/python3 -m http.server 8767
# http://127.0.0.1:8767/index.html?part=calc&lang=en
#   part=input | result | calc | pay | receipt      lang=en | zh-HK      debug=1 for the overlay
```

Debug overlay (`?debug=1`) prints the version and the height the frame is reporting. `?part=calc`
with `lang=zh-HK` switches the table in place — the frame is never re-loaded.
