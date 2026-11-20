# Client comment pass 2 — 20 Nov 2026

Denise returned an annotated deck (`~/Downloads/Calculator_Comments.pptx`, 8 slides) against the live
POC widget, plus `~/Downloads/Tax Calculator.docx` with the wording her side has approved.
This is the recorded change list for that pass: what her note said, what shipped, and the three
judgement calls Kevin should know about.

Applied by `qa/apply_client_comments2_2026120.py` (37 edits, each asserted to occur exactly once,
re-runnable from the local `embed/index.html.bak-pre-client2-2026120` backup — `.bak*` is git-ignored,
so a fresh clone must restore it from git history at `71362e7` first).

---

## 1 · The eight comments

| # | Her note (slide) | What shipped | Evidence |
|---|---|---|---|
| C1 | "Please use white background" (slide 1) | `--ground` `#F3F3F0` → `#fff`. Card surfaces stay white and are held by the existing 1px `--line` hairlines; **no shadow was added**. | `qa/poc_test` 73 checks · screenshot `shots/client2-2026120/calc-1440-zh.png` |
| C2 | "Please adjust the width of the calculator, especially for desktop view" | `.wrap` `max-width` 44rem (704px) → **56rem (896px)**. Gutters (`--gut`) and the `max-width:640px` mobile block are untouched, so the phone scale does not move. | `.wrap` measured 896px at 1100 and 1440 |
| C3 | "Donation field set minimum at HK$100" | Below HK$100 **no estimate is shown**; her own line — 捐款金額達到或超過 HK$100 可獲得稅收減免。 / *Donation amount at HK$100 or above will receive tax deduction receipt* — appears under the amount field **and** in place of the estimate. The typed amount is **never clamped** (`50` stays `50`), and `calc_result_shown` is not sent, because no result was shown. | `qa/poc_test` 3 floor checks; HK$100 itself renders the estimate (HK$14 – 17) |
| C4 | "Take out this section, only let user to select donate one-off or monthly" (slide 2) | The months field (`#months-field`, the 1–12 `<select>`, `clampMonths`) is **deleted**. **Monthly now means 12 months** — the annual deduction is `amount × 12`, stated in the caption ("每月 HK$1,300 × 12 個月 = 全年 HK$15,600。") rather than assumed silently. | `qa/poc_test` monthly cases; `?part=calc` monthly 1,300 → 15,600 |
| C5 | "No need minus sign" (slide 5) | Tax saved renders **positive**: `HK$182`, `HK$182 至 HK$221`. The `−` prefix was removed from the render path and from the static default markup. | `qa/lang_parity` "never renders with a minus sign" |
| C6 | "Take out, as we already mentioned it calculate based on personal basic allowance; unless it allow ppl to select single or married at the beginning" (slide 7) | The result block's `<p class="scope">` — 只估算個人在薪俸稅下的捐款扣稅，並非稅務建議。 / *One person, salaries tax only. An estimate, not tax advice.* — is **deleted**. The single-person allowance is still stated once, where the income is chosen (未扣除免稅額（以 HK$145,000 估算）). | `qa/poc_test` "no longer repeats the allowance/scope reminder" |
| C7 | "Take out, if the user already select at the beginning no need to remind here and it is redirect to another donation page now" (slide 7) | The payment block's 改為每月捐款 / *Give monthly instead* link is **deleted**. The one-off / monthly choice is made at step 1 and nothing repeats it. | block diff; `?part=pay` peak 543 → 523 |
| C8 | Their `Tax Calculator.docx` disclaimer (EN 128–132, ZH 134–138) | Adopted **verbatim**, character for character, in both languages, replacing our draft. Both placements carry it: the collapsed `#disclaimer` block (the full five lines, visible in every `?part=` mode) and the footnote at the foot of the calculator block (their first line). Their text was not edited, re-punctuated or merged — including its own mixed full-stop usage (Chinese lines 1, 2 and 4 end in an ASCII period, lines 3 and 5 in 。). | `qa/lang_parity` "verbatim, in both languages" compares the rendered DOM to the docx text |

## 2 · The combined link (`?part=all`)

- `?part=all` renders calculator → result → payment → receipt in one document, in that order, using the
  design's own section rhythm. The step numerals run 1–5 across the whole flow (payment = 4, receipt = 5),
  so the combined document is one numbered journey rather than four blocks glued together.
- **A bare `/embed/` URL now defaults to `all`.** Nothing depended on the old empty state: no CSS rule,
  no test and no sibling page keyed off "no part" — `qa/fixture.html`, `/harness/`, `/preview/` and
  `/events/` either pass an explicit `part` or pass none (and none now means `all`).
- The five existing values (`input`, `result`, `calc`, `pay`, `receipt`) are unchanged and still gated by
  `qa/poc_test` at 328/568/944/1280px. The four-block split remains the recommended production arrangement.
- Anchor behaviour is intact: `#goto-result` ("See what it costs you") jumps to the result section inside
  the same document, and the consent line's `#disclaimer` link still opens the collapsed text as well as
  jumping to it.

## 3 · Judgement calls (read these)

1. **Monthly = 12 months is my assumption, made on your behalf.** The client removed the months control
   without saying what monthly should mean. Twelve months is the only reading that makes "monthly" a full
   assessment year, and it is stated in the visible caption. If their monthly product has a shorter
   default, this is the one number to change: `var MONTHS = 12;` in `embed/index.html`.
2. **C6 removes the widget's only "salaries tax only" statement.** Their approved disclaimer does not say
   it either — it says *"Estimates tax using progressive or standard rates (whichever is lower); actual
   results depend on the IRD"*, and their own FAQ says the deduction runs against salaries tax, profits tax
   **and** personal assessment. So a reader can now believe the calculator answers a broader question than
   it does. I did **not** re-add the sentence (their text governs and they asked for the removal) and I did
   not edit their disclaimer to cover it. **Recommendation:** ask Denise for one line in their own
   disclaimer — e.g. *"Covers salaries tax for an individual only."* — or put it on the Optimizely page
   above the frame. Flagged, not fixed.
3. **C3's floor is applied to the amount in the field, not to the annual total.** HK$50/month is HK$600 a
   year and *is* deductible, but her note is about the donation field, so HK$50 entered as a monthly gift
   shows no estimate. If the floor should test the annual figure instead, that is a one-line change.

## 4 · Heights reissued

Every block moved, so every number in `docs/INTERFACE.md` §2 was reissued in the same pass — a stale
height in a sibling page is silent clipping. The five quoted widths (320 / 390 / 768 / 1024 / 1440) are
printed by `qa/sweep_heights.py` on every run.

| Block | declared zh / en | peak (22 widths) |
|---|---|---|
| `?part=all` | 2880 / 2990 | 2811 @900 / 2927 @320 |
| `?part=calc` | 1800 / 1800 | 1722 @900 / 1742 @900 |
| `?part=input` | 1040 / 1040 | 974 @820 / 974 @820 |
| `?part=result` | 890 / 890 | 833 @900 / 833 @900 |
| `?part=pay` | 580 / 580 | 523 @900 / 523 @900 |
| `?part=receipt` | 810 / 910 | 746 @320 / 852 @320 |

**The combined frame is 2,811px zh / 2,927px en at its tallest reachable state** — inside a sane iframe,
but a 2.9m-pixel-tall block on a phone is a long scroll inside a frame. Recommendation stands: use
`?part=all` for a quick one-link review, ship the four blocks in production.

## 5 · QA after the pass

`qa/test_tax_engine.py` 6/6 exact · `qa/verify_six_examples.py` 6/6 in both languages ·
`qa/poc_test.py` **73 passed, 0 failed** · `qa/lang_parity.py` 15 passed · `qa/sweep_heights.py` no
overflow in either language · `qa/design_gate.py` clean. The tax engine was not touched: every change in
this pass is copy, CSS or layout (`git diff` on the engine block is empty).
