# Direction A — “quiet editorial”

A working variant of the Fred Hollows HK donation tax-calculator iframe, built on top of
`embed/index.html` without changing the tax engine, the height/language contract, the analytics
events or the form.

Files in this folder

| file | what it is |
|---|---|
| `index.html` | the finished variant — one self-contained file, no external requests |
| `NOTES.md` | this note |
| `COPY-CHANGES.md` | every string that changed, old → new, both languages |
| `shots/` | calc · pay · receipt, English and Chinese, 390 and 1280, captured at the declared height |
| `qa_calm.py` | 81 assertions: engine bytes, key parity, CJK, facts, touch targets, overflow, heights |
| `_sweep.py`, `textcount.py`, `copy_diff.py`, `shots.py`, `build.py` | the measurement and build tools used below |

---

## 1 · The design read

The donor is on a phone, in a hurry, and slightly suspicious: a charity is telling them that giving
away money costs them less than they think. The block has to feel *more* careful than the page around
it, not louder. It also has to survive a fixed pixel height inside a CMS, so every pixel of chrome is
a pixel of content lost.

The register is the charity's own printed matter — an annual report page, a receipt, a BIR60 — not a
web form. That register has three properties I used: one narrow column, rules instead of boxes, and a
figure so much larger than its label that the arithmetic is legible at a glance.

> **On this page, the arithmetic of a deduction — you give X, it costs you Y — becomes a ruled ledger:
> the money in large tabular figures, the tax in small type beside it, structure carried by hairlines
> and aligned columns, the way a receipt carries it.**

The old build was 4 rounded cards with 1px borders, nine bordered radio rows inside one of them, a
3-up cell strip with internal borders, and body type at 15px nearly everywhere (heading 20px, the
one number 28px). That is boxes inside boxes, and a flat type scale — the two things that make a
government-adjacent widget look like a form to be endured.

## 2 · Three decisions that carry the improvement

**1 · One type scale, reversed.** Five steps plus the display figure: 32 / 20 / 17 / 15 / 13 / 11.5px,
and the result number at 56px desktop, 40px on a phone. The heading-to-body ratio goes from 1.2 to
1.9, and the number is now 2.8× its own label. Nothing is "15px everywhere" any more, and no size
exists for decoration: 20px is only ever a statement, 13px is only ever a label.

**2 · Rules, not cards.** Every structural line in the build is one hairline — `rgba(10,9,9,.12)` — on
a transparent ground, at a 640px measure. The nine income rungs became a ruled table with the rate in
a right-aligned tabular column; the three payment rails became three ruled rows; the receipt fields
became underline-only fields. The card, the pill segmented control, the pill chips, the cell strip's
internal borders and the orange 3px bar are gone. Not one box remains, so nothing is nested in
anything.

**3 · Wordiness spent on hierarchy, not on facts.** The calculator now reads as two short decisions
(“Your gift”, then “What it costs you”), not a wall of caveats. What moved: the four-line grey lecture
under the income picker (which repeated the below-allowance rule the rung label already states), the
“Assumptions: / Cap:” audit pair, the three copies of “on the Foundation's donation page”, the
“This is the amount you actually pay” caption, and the step eyebrows. What did **not** move: every
fact still stands in the block, and the two that used to be prose are now where they belong —
the standard-rate explanation sits *immediately under the rate ladder* (where the falling rungs would
otherwise read as a bug), and the section-88 rule plus the non-deductible list sit in one disclosure
opened from “What counts as a deductible gift”.

Visible body text on load, characters per block (no `details` opened):

| block | before en | after en | | before zh | after zh |
|---|---|---|---|---|---|
| calc | 2191 | **1270** (−42%) | | 970 | **704** (−27%) |
| pay | 324 | **149** (−54%) | | 136 | **58** (−57%) |
| receipt | 707 | **516** (−27%) | | 210 | **162** (−23%) |
| **total @390** | 4538 | **2859** (−37%) | | 1316 | **924** (−30%) |

85 keys were rewritten in both tables, 7 added, 13 removed (full old → new list in
`COPY-CHANGES.md`). And it got shorter as well as quieter: calc/en 1937 → 1421px peak, pay 1144 → 434, receipt/en
959 → 845.

## 3 · Trade-offs I refused

- **No single call to action in the payment block.** The three rails are peers; a filled button on the
  credit card would rank them, and the charity has not said which route it prefers. Each row is a
  full-width 64px target and is the action. The receipt block keeps the one orange button.
- **No step numbers, no eyebrows.** “Step 1 / Step 2 / Step 3” was removed, not restyled. The three
  block headings sequence themselves (“Your gift” → “What it costs you” → “How you give”), and as
  separate embeds a step number is a promise the block cannot keep (this is a five-block contract:
  the page may show only one of them).
- **No colour on the numbers.** Orange is used exactly once per block — the primary button — and navy
  only for links and the selected rung. The saving figure would look better in orange; it would also
  compete with the button, which is the only thing the donor must still do.
- **No motion beyond 140ms.** Hover/active only, `prefers-reduced-motion` honoured. No entrance
  animation: a block whose job is a number should not animate the number arriving.
- **I did not re-add the merchant QR panel**, and the three rails still point at `hollows.org`
  (rules 7 of the brief).
- **I did not reduce the caveats to fit the frame.** The disclaimer, the spouse rule, the cap and the
  scope sentence are all still there in full; if height had to give, it gave at the type scale.
- **I did not touch the tax engine, the postMessage contract, GTM, or the form's three fields.** The
  consent checkbox is now wrapped by its label so the whole 44px row toggles it; the `#consent`
  input id, and every id the JS reads, are unchanged.

## 4 · Heights

Content peak measured at 22 widths (320 → 1440), both languages, peak taken and 55px added. One
number per block per language, as the component requires:

| block | URL | peak · zh-HK | **declared zh** | peak · en | **declared en** |
|---|---|---|---|---|---|
| Calculator + result | `?part=calc` | 1380 (at 944) | **1440** | 1421 (at 944) | **1480** |
| Payment | `?part=pay` | 434 (at 944) | **490** | 434 (at 944) | **490** |
| Receipt | `?part=receipt` | 759 (at 320) | **820** | 845 (at 320) | **900** |

Against the contract in `docs/INTERFACE.md` §2 (1650 / 2000 / 1040 / 1210 / 860 / 1030):

| block | old zh | new zh | saved | old en | new en | saved |
|---|---|---|---|---|---|---|
| calc | 1650 | 1440 | −210 | 2000 | 1480 | **−520** |
| pay | 1040 | 490 | **−550** | 1210 | 490 | **−720** |
| receipt | 860 | 820 | −40 | 1030 | 900 | −130 |

**If the component can take a different height per breakpoint**, the receipt block is where it pays:

| block | ≤480px | ≥568px |
|---|---|---|
| calc · zh-HK / en | 1440 / 1480 | 1440 / 1480 |
| pay · zh-HK / en | 490 / 490 | 490 / 490 |
| receipt · zh-HK / en | 820 / 900 | 710 / 740 |

**Disclosure states.** These heights are for the block as it loads. Opening the disclosures grows it,
and a fixed frame with `scrolling="no"` will clip: calc +494px (zh) / +543px (en) at 320 with all
three open; receipt +255 / +401. Either wire the existing `resize` message (INTERFACE §3, seven
lines) or give `?part=calc` 2000px and accept the dead space — I recommend the listener, because
2000px is exactly the slack we just removed.

## 5 · Where each required fact now lives

| fact | location |
|---|---|
| 35% cap on assessable income | `#cap` line in the result, and `foot.legal` in `?part=calc` |
| HK$100 annual-total receipt threshold | `rc.threshold`, above the receipt form |
| six-year retention | `rc.keep`, under the submit button |
| s.88 approved charity + non-deductible list | disclosure “What counts as a deductible gift” (calc) |
| spouse rule, its own 35% cap | disclosure “Can a couple combine the deduction?” |
| “not tax advice” scope sentence | `s2.scope` under the result; full scope in `rc.disc.body` |
| standard rate 15% / 16%, top rungs fall | `s1.band.note`, directly under the ladder |
| 31 March year-of-assessment end | `s1.months.hint` (monthly) and `rc.disc.body` |
| disclaimer text | disclosure at the foot of the receipt block |

`qa_calm.py` asserts all of the above in both languages by rendering the block and searching the
rendered text — not by reading the source.

## 6 · Re-measuring

```bash
cd design/calm && /Library/Developer/CommandLineTools/usr/bin/python3 -m http.server 8766
/Library/Developer/CommandLineTools/usr/bin/python3 qa_calm.py      # 81 assertions + height sweep
/Library/Developer/CommandLineTools/usr/bin/python3 textcount.py    # before/after word count
/Library/Developer/CommandLineTools/usr/bin/python3 shots.py --dir shots --lang en
python3 build.py    # rebuild index.html from _new_style.css / _new_body.html / _new_i18n.json
```

`build.py` refuses to write if the `FHF_TAX_ENGINE_START…END` block changes; it is byte-identical to
`embed/index.html` (sha256 `b232c76c…`).

## 7 · Known limits

- The 390px shot of `?part=calc` carries ~160px of dead space at the foot: one integer has to cover a
  320px peak. A breakpoint pair does not help calc; splitting `?part=input` + `?part=result` (as
  INTERFACE §2 already allows) is the only real fix.
- The Chinese build is 40–85px *shorter* than the English at every width now, so the two declared
  heights stay different — do not reuse one for the other.
- The `<select>` used below 721px is a native control; its arrow is drawn with a CSS gradient. iOS
  centres the option text slightly differently, which is fine but not pixel-identical to Android.
- Screenshots are 2× DPR PNGs; `pay` is the smallest file because it is nearly all white space —
  that is a real render, not a failed one (check: the text is legible at 100%).
