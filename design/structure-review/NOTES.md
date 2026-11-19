# Structure review — Fred Hollows HK donation tax calculator

**Scope: analysis and wireframe only.** Nothing in `embed/` or `qa/` was touched, nothing was deployed.
Every height, word count and figure below was measured on the live POC on 19 November 2026.

Files in this folder:

| file | what it is |
|---|---|
| `NOTES.md` | this note — the analysis, the three answers, the costs, the decisions needed |
| `wireframe.html` | the block as built and as proposed, at 390 px and 1,140 px, in English and Chinese, with the live figures. It measures itself on load; the table at its foot is generated, not typed. |
| `shots/` | screenshots of the wireframe at 390 and 1,280 |

---

## 0 · How the numbers were produced

| what | how |
|---|---|
| Block height | content height = bottom edge of `#root`'s last child − `#root` top + bottom padding. `scrollHeight` is unusable here: `body[data-part] .wrap{min-height:100vh}` floors it at the viewport height, which is exactly why a frame can look "big enough" while the content is clipped. |
| "as built" heights | the live block, one fresh load per state, so no state leaks between measurements. |
| "proposed" heights | the wireframe, which is built from the live block's own type scale, gutters and component metrics. It reproduces the live block to within 16 px, so its numbers are comparable and slightly pessimistic. |
| Words | every rendered text node outside a closed `<details>`, counted in the browser; summaries count as visible, their bodies do not. |
| Rendered figures | read off the live DOM in four states (band / exact × one-off / monthly), both languages, and typed into the wireframe unchanged. |
| Per-item height effects | measured by toggling that one change on the finished proposal. Items share the spacing at each junction, so they do not sum — the state ledger is the authoritative number and the item list explains it. |

Declared frame heights today: **1,950 px English / 1,940 px Chinese** for this block, measured including the
monthly state.

---

## 1 · What is on the page, as rendered

`?part=calc` is two sections in one scroll. The two sections carry step discs; the other two blocks in the
full widget (`How you give`, `Claim your receipt`) carry none.

| # | Block | Rendered content | Height @390 once / monthly |
|---|---|---|---|
| 1 | `1 Your gift` · card A | seg (One-off / Monthly), amount, 4 quick chips, [monthly: months `<select>` + 4 month chips + hint] | |
| 2 | · card B, no heading of its own | legend `Your assessable income this year, roughly` set at **13 px**, one hint, the 9-rung ladder (native select below 721 px), the standard-rate note | 651 → 900 (whole section) |
| 3 | disclosure, outside any card | `Use your exact income` — a second input for the same value | 49 |
| 4 | disclosure, outside any card | `What counts as a deductible gift` — s.88, the non-deductible list, below-allowance | 49 |
| 5 | `2 What it costs you` | navy panel: You pay, caption, 3-row ledger; benefit sentence; **three separate grey lines**; disclosure `Can a couple combine the deduction?` | 596 → 616 |
| 6 | foot | `*` legal line + collapsed `Disclaimer` | 60 + 59 |
| — | `How you give`, `Claim your receipt` | hidden in this block, present in the full widget | 0 |

**Text, measured:** 161 words visible in the one-off state (208 monthly), 275 Chinese characters, and
**218 more words behind four taps** (28 exact · 62 what counts · 50 spouse · 95 disclaimer). Thirty-seven
visible text nodes, set in **eighteen distinct type styles** (twenty in the monthly state).

**So the first finding changes the answer to Q1: the page does not have too much text.** 161 words is a third
of a short article. What it has is eighteen type styles and thirty-seven text objects arranged for two
questions — the reader is not tired, they cannot tell what is a decision and what is commentary.

### The structural fault, stated precisely

**The commentary outranks the questions.** Measured on the live block:

| element | size / weight / colour | role |
|---|---|---|
| `details.q summary` — every disclosure | **15 px**, 500, **navy `#01014E`** | commentary |
| `legend.flabel` — `Your assessable income this year, roughly` | **13 px**, 600, grey `#3F3F4A` | a decision |
| `label.flabel` — `Donation amount` | 13 px, 600, grey | a decision |

`What counts as a deductible gift` and `Use your exact income` are set **larger, darker and in the brand
colour** than the two things a donor must answer. That is why the block reads as a pile of text: the eye is
drawn to the commentary, and the decisions look like field labels. Fixing it costs no words.

Three more faults, each verified:

1. **One value, two controls.** The months field ships a 12-option `<select>` *and* a 4-chip row bound to the
   same value, both visible at once — worth 106 px of the tallest state, to duplicate a control that is
   already on screen. The chips cannot say 4 months; the select can.
2. **One question cut in half by a card border.** The band picker sits inside card B; the exact-income input
   sits outside it, as a disclosure of identical weight to the eligibility note. Two ways to answer one
   question, in two places, at two levels.
3. **The answer is followed by three grey lines**, each with its own top margin (22 / 6 / 14), totalling
   181 px at 320 px — the assumption, the cap and the scope, as three unrelated blocks.

One cosmetic point, checked rather than assumed: in the desktop ladder the widest rung
(`HK$2,132,500 – 5,000,000`) leaves exactly **10 px** between the range and its rate — one character space —
at every width from 721 px up. Measured as a gap, not an overlap; it reads as a single run of text, and it is
the visible symptom of a nine-rung ladder that has no room left.

---

## 2 · Q1 — Is this too much text, and where should it be grouped?

### The split: two decisions, everything else is reference

A donor has exactly **two things to decide**, in this order:

1. **How much am I giving** — one-off or monthly, the amount, and (if monthly) how many months.
2. **What rate applies to me** — a rough income band, or an exact figure.

Everything else is either the **answer** to those two, or **reference material that belongs to one of them**:

| # | Item | Kind | Owner | Why it belongs there |
|---|---|---|---|---|
| 1 | Mode, amount, quick chips | **DECISION 1** | — | — |
| 2 | Months given | **DECISION 1** | — | Exists only when monthly |
| 3 | Income band | **DECISION 2** | — | — |
| 4 | Exact income | **DECISION 2**, other form | — | Not a separate choice: the same value in another unit |
| 5 | s.88 / what counts, the non-deductible list, below-allowance | REFERENCE — a **gate on decision 1** | decision 1 | "Can I even claim this?" is asked while choosing the amount, not after the number |
| 6 | Standard rate 15 % / 16 %, falling rungs | REFERENCE — **explains the ladder** | decision 2 | It explains why the last two rungs fall; meaningless away from the ladder |
| 7 | HK$145,000 basic-allowance assumption | REFERENCE — a **modelling assumption** | decision 2 | It qualifies the band labels |
| 8 | 35 % cap | REFERENCE — **reassures the answer** | the answer | It says "this number is not capped". Collapsing it makes the figure look conditional. |
| 9 | Spouse rule | REFERENCE — **follows the answer** | the answer | Only bites when the number is large |
| 10 | "One person, salaries tax only. An estimate, not tax advice." | REFERENCE — **scope** | the answer | — |
| 11 | HK$100 receipt threshold, six-year retention | REFERENCE — **instruction** | the receipt form | Already correctly placed |
| 12 | `*` legal line, disclaimer | REFERENCE — **mandatory close** | the block | Must stay last |

**The organising principle the page is missing, in one sentence: a page has a decision, an answer and a way to
act — everything else belongs to the thing it explains.** The block groups by "card", which is why four
unrelated reference items sit at one visual level while the two decisions sit at another.

### Verdict on each of the seven areas

| Area | Verdict | What changes |
|---|---|---|
| **1 · Your gift** | **Keep the step, cut the duplicate control** | The 4-chip months row goes; the `<select>` stays as the single control. Label, hint, mode switch and amount field unchanged. |
| **2 · Income band** | **Promote to its own step (2)** | It stops being a 13 px legend inside card B and becomes a heading at heading size with its own numeral. Biggest hierarchy fix, no words moved. |
| **3 · `Use your exact income`** | **Merge into area 2** — see Q2 | Becomes a control at the foot of the income group that swaps the ladder for an input in place. |
| **4 · `What counts as a deductible gift`** | **Move up, into the gift group** | A gate on decision 1; now sits under the amount it qualifies and stops looking like a peer of the income control. Words unchanged. |
| **5 · What it costs you** | **Keep the figure and ledger exactly; group the three grey lines** | The three sentences become one meta block — same words, no rules between them, 47 px less. Then **one closing group** for the spouse rule (Q3). |
| **6 · How you give** | **Keep; one redundancy to remove** | `Give monthly instead` points at the same destination as the `Monthly` segment: hide it when the block is already monthly. Full widget only — outside this block. |
| **7 · Foot** | **Keep, unchanged, last** | Legal line + collapsed disclaimer. Must stay the final element. |

### Proposed block, in order

```
1  Your gift            mode · amount · chips · [months]
                        └ What counts as a deductible gift        (collapsed, in-group)
2  Your income, roughly ladder  ── or ──  Use your exact income    (in-place swap)
                        └ the standard-rate note, in both states
3  What it costs you    the figure · ledger · benefit sentence
                        · one meta block (assumed / cap / scope)
                        └ Common questions → spouse rule
*  legal line
▾  Disclaimer           (collapsed, last)
```

In the full widget that becomes five numbered blocks — gift, income, cost, pay, receipt — which also fixes an
existing inconsistency: today only two of the four visible blocks carry a numeral.

**Height:** 1,909 px at 320 px in the monthly state against 1,912 px today — the restructure is height-neutral
where it is tightest (see §6). In the one-off state it is 83 px taller, because the second decision now has a
heading and the closing group has a label. Both states stay inside the declaration.

**Cost:** one numeral changes (the result's disc goes 2 → 3; the numerals are `aria-hidden`, no copy string
changes). No other copy changes. The months chips are removed as a control, not as a word.

---

## 3 · Q2 — Should the exact-income input be one control with the band picker?

**Yes. One control, two states, swapped in place.** What exists now is not a choice a donor makes — it is a
fallback hidden behind a disclosure that outranks the primary control on screen.

### Interaction

```
            ┌ Your income, roughly ───────────────────────┐
 range      │ Before allowances (HK$145,000 assumed).     │
 (default)  │  ○ Not sure                      2% – 17%   │
            │  ○ Below HK$145,000              No tax     │
            │  …                                          │
            │  ● HK$345,000 – 2,132,500        About 17%  │
            │  …                                          │
            │  Above HK$2,132,500 the standard rate …     │
            │ ──────────────────────────────────────────  │
            │  Use your exact income                    → │  ← 48 px row, in-group
            └─────────────────────────────────────────────┘
                              ↓ tap
            ┌ Your income, roughly ───────────────────────┐
 exact      │ Assessable income for the year              │
            │ HK$ 500,000                                 │
            │ One figure instead of a range, worked …     │
            │ Above HK$2,132,500 the standard rate …      │
            │ ──────────────────────────────────────────  │
            │ ← Use an income range instead               │
            └─────────────────────────────────────────────┘
```

The card never grows by the size of the input: the ladder is **replaced**, not supplemented. One control, one
job, and the two forms of the same answer are never both on screen — which is exactly what the current build
gets wrong.

### What happens to each thing

| Question | Answer |
|---|---|
| **The "Not sure" rung** | **Stays where it is**, first in the ladder, copy unchanged. It answers the question the ladder asks ("roughly which band?"). In exact mode it is not shown, because the ladder is not shown; the previous rung is remembered so switching back loses nothing. It does not become a "third state": exact is not a rung, it is the same question in another unit. |
| **The two captions** | **Each state owns one, and only one is visible at a time.** `Before allowances (HK$145,000 assumed).` qualifies the range labels and travels with the ladder. `One figure instead of a range, worked through the bands and the 35% cap. Never sent, never stored.` travels with the input. Today both exist, but the second sits in a separate row below the card, after the note. |
| **Standard-rate note (15 % / 16 %)** | **Stays visible in both states.** It is the only place the falling top rungs are explained, and hiding it in exact mode would make a statutory fact reachable only by switching back. It costs 62 px to keep — and that 62 px is the last thing standing between the proposal and a 320 px fit (§6). |
| **The `Use your exact income` string** | Kept verbatim as the affordance. It is already the right words. |
| **A third state** (an "Exact figure…" rung inside the ladder) | **Rejected.** It makes a homogeneous list heterogeneous, puts a non-range option inside a list of ranges (and inside the native picker on mobile), and still has to reveal an input — the same swap with an extra step and a broken list. |

### Why this is worth more than the height it saves

Measured on the live page, the same gift of HK$1,300:

| | band 345,000 – 2,132,500 | exact 500,000 |
|---|---|---|
| You pay | `HK$1,079 – 1,118` | `HK$1,079` |
| caption | `Both ends of your range.` | `Worked exactly from HK$500,000.` |
| ledger | `−HK$182 to −HK$221` · `14% – 17%` | `−HK$221` · `Marginal rate 17%` |
| benefit | `HK$1,300 given, deductible. Every HK$100 costs you about HK$83 to HK$86.` | `…all of it deductible… costs you about HK$83.` |

The exact state is the one that delivers the widget's promise: one number, one rate, one sentence. It is
currently the **least discoverable control in the block** — a grey 15 px row under a card — while the state it
produces is the best thing on the page. Promoting it is a conversion change, not a tidiness change.

### Height: the disclosure is what breaks the frame

| | 320 | 390 | 1,280 |
|---|---|---|---|
| today, monthly | 1,912 | 1,719 | 1,879 |
| today, monthly, **exact open** | **2,129** | 1,909 | **2,081** |
| declared | **1,950** | 1,950 | 1,950 |
| overflow when open | **+179** | −41 | **+131** |
| proposed, monthly | 1,909 | 1,700 | 1,885 |
| proposed, monthly, **exact on** | **1,997** | 1,805 | 1,826 |
| overflow when on | **+47** | −145 | −124 |

Opening the exact row today adds **217 px at 320 px** and takes the block 179 px past its declared height
(131 px at 1,280). Swapping in place costs about 88 px, so the state stops breaking two of the three widths
and the third is 47 px away.

---

## 4 · Q3 — Should the two disclosures become one FAQ?

### The three placements, on the criteria that matter here

| | (a) one FAQ inside the calculator, closing the block | (b) FAQ on the CMS page, linked from the calculator | (c) hybrid: one question inline where it bites, the rest in a closing group |
|---|---|---|---|
| **Context at the point of doubt** | ✗ The eligibility rule lands ~900 px (2.5 screens on a phone) below the amount field it qualifies | ✗ A different page, calculator left behind, for one paragraph | ✓ Eligibility under the amount; the spouse rule under the number |
| **Height cost** | +36 px (a group label; the rows already exist) | −98 px, and the eligibility row leaves the input half | +36 px, or +85 px with the optional second question |
| **SEO value** | ✗ An iframe cannot rank. Zero. | ✓ Their CMS page can rank, and a Q&A block is the one format still worth rich results | ✓ The same CMS block, plus the in-context copy for the donor |
| **Mobile (80–90 % of traffic)** | ~2.5 screens of scrolling to an answer | A page change on a thumb, then back | Nothing to scroll for the eligibility question |
| **Split embed** (`?part=input` / `?part=result`) | ✓ The only place both halves can see it | ~ depends on the host page's link placement | ✓ Each half carries the question that bites in it |
| **Maintenance** | Ours, once | Theirs, forever, in a CMS we do not touch — it will drift from the frozen register | Split: in-widget copy frozen with the block, CMS copy theirs |

### Recommendation: **(c), with the split drawn this way**

- **`What counts as a deductible gift` stays in the input half**, moved up into the gift group. It is a gate on
  decision 1 — "can I claim this at all?" — and the one question with real search demand. Moving it to the
  bottom would put the answer to a pre-donation question after the donation decision.
- **`Can a couple combine the deduction?` moves into one closing group** at the end of the result block, under
  a single label (`Common questions`). That is the block both halves can see, and the only question that needs
  the result above it.
- **The complete set is published as a FAQ on their CMS page**, beside or below the embed, linking into the
  calculator. Not a competing placement — a different audience. The iframe serves the donor mid-decision; the
  CMS page serves the search result, and is the canonical indexable copy.

**Why not (a), plainly:** one FAQ at the end is tidier for us and worse for the donor. It answers "can I claim
this?" only after they have chosen an amount and scrolled past the answer. Grouping is not collecting — a
question belongs where it is asked.

**Why not (b) alone:** the donor who most needs the eligibility rule is mid-form on a phone; sending them to
another page for one paragraph is where they leave. Zero height cost is not worth losing the answer at the
moment of doubt.

**Condition on (c):** it needs their content team to own the CMS FAQ. If that cannot be staffed, fall back to
(a) with eligibility left in the input half — and accept that the SEO version never exists.

**Height:** +36 px for the group label, +49 px more if the optional second question (`What if my gift is more
than 35% of my income?`) is approved. The wireframe draws **only the spouse row**: at 320 px the block has no
room for the second question (§6), so it is priced but not shown.

---

## 5 · Copy ledger — every string this proposal touches

**Copy is frozen.** Nothing below is applied. Three rows are new, one is optional, one is a defect fix.

| # | Key | Status | Before | After (proposed) |
|---|---|---|---|---|
| 1 | `s1.exact.back` | **NEW** — required by Q2 | — (no such control exists) | EN `Use an income range instead` · ZH `改用入息範圍` |
| 2 | `faq.h` | **NEW** — required by Q3(c) | — | EN `Common questions` · ZH `常見問題` |
| 3 | `s2.capq.q` | **NEW, optional, not drawn** | — | EN `What if my gift is more than 35% of my income?` · ZH `捐款超過入息 35% 會怎樣？` |
| 3a | `s2.capq.a` | **optional** — assembled from two *existing* sentences, so no new statutory language | — | EN `The cap is 35% of assessable income for the year. What you cannot use — including the part above the 35% cap — your spouse may claim on their own BIR60.` · ZH `扣稅上限為應評稅入息的 35%（全年合計）。您未能用盡的扣稅額（包括超出 35% 上限而未扣除的部分），配偶可在其 BIR60 報稅表內申報。` — verbatim from `s2.cap.def` + `s2.spouse.a` |
| 4 | `d.benefit.range` | **DEFECT FIX (EN only)** — the `{cap}` slot is empty under the cap, leaving a bare adjective after a comma | `HK$1,300 given, deductible. Every HK$100 costs you about HK$83 to HK$86.` | `HK$1,300 given, all of it deductible. Every HK$100 costs you about HK$83 to HK$86.` |

No other string changes. In particular `s1.exact.hint` (`One figure instead of a range, worked through the
bands and the 35% cap. Never sent, never stored.`) **survives the swap unchanged** — it names the range it
replaced, so it still reads correctly with the range one tap away.

**Register check on the new strings:** `改用入息範圍` and `常見問題` are 書面語, noun-phrase shaped like the
neighbouring keys (`改用自己的入息數字`, `哪些捐款才可扣稅`). `捐款超過入息 35% 會怎樣？` keeps the existing
`35%` spacing convention. The Chinese template has no equivalent of the `d.benefit.range` gap —
`可作認可慈善捐款扣除。` reads correctly — so row 4 is an English-only fix.

---

## 6 · Height ledger

Declared: **1,950 px** English / 1,940 Chinese. Worst case is the monthly state at 320 px.

| state | 320 | 390 | 1,280 | Δ at 320 |
|---|---|---|---|---|
| as built · one-off | 1,573 | 1,450 | 1,700 | |
| as built · monthly | 1,912 | 1,719 | 1,879 | |
| as built · monthly, exact open | **2,129** | 1,909 | **2,081** | |
| proposed · one-off | 1,656 | 1,536 | 1,761 | +83 |
| proposed · monthly | 1,909 | 1,700 | 1,885 | −3 |
| proposed · monthly, exact on | **1,997** | 1,805 | 1,826 | −132 |

Red = past the declaration. The "as built" rows are the live block; the "proposed" rows are this wireframe,
which runs ~8 px tall against the live block, so treat them as a few pixels pessimistic.

**Where the height goes at 320 px, monthly** (each measured by toggling that one change):

| change | Δ px |
|---|---|
| months: the 4-chip row removed, the `<select>` kept | **−106** |
| three grey lines regrouped into one meta block | **−47** (181 → 134, measured element-to-element) |
| closing group: one label added | **+36** |
| *(optional second question, if approved)* | *+49* |
| the step numeral on the result — costs nothing, the heading sets the row height | 0 |
| eligibility row moved into the gift card | +2 |
| **derived remainder**: income promoted to its own step — a second heading, a section break in place of a card-to-card gap | **+112** |
| **net, monthly state** | **−3** |

That derived +112 is the price of the thing the client asked for: the second decision announcing itself as a
decision. It is paid for by the two duplicate/loose items above it (the chips and the grey lines), so the block
comes out the same height it went in — while the state that was 179 px over the declaration is now 47 px over.

### The last 47 px at 320

The block fits at 390 and 1,280 in every state, with 145 px and 124 px to spare in the loose one. Only the
exact state at 320 px is still over, and there are exactly two honest ways to close it — this is a client
decision, not a design one:

| option | effect | cost |
|---|---|---|
| **A. Raise this block's declaration to 2,010 px** | every state fits at every width, with margin for the CMS's own line-height and font fallback | +60 px of page length for every visitor, in every state |
| **B. Hide the standard-rate note while exact mode is on** (−62 px) | 320 px exact becomes ≈1,935 and fits | the 15 % / 16 % rule is then reachable only by switching back to the ladder — a statutory fact behind a state |

My recommendation is **A**, and only if 320 px still matters to them: at 375 px and above the exact state
already fits. **B** is cheaper and I would not take it — the note is the only explanation of the falling top
rungs anywhere in the block.

---

## 7 · What I deliberately refuse to change

- **The words of every statutory fact.** 35 % cap, HK$100 threshold, six years, s.88, the non-deductible list,
  the spouse rule, not-tax-advice, 15 % / 16 % with the falling rungs, 31 March, the disclaimer — not one
  sentence is reworded. The only edit is a template slot that renders a bare adjective (§5 row 4).
- **The order of the two decisions.** Gift before income. A donor knows what they are giving; nobody knows
  their assessable band without stopping to think. "Income first" is more tax-logical and worse for the donor.
- **The 35 % cap line stays visible**, not collapsed into the FAQ. It is what stops the figure reading as
  conditional. Reachable-but-hidden is not the same as reassuring.
- **The hero treatment.** Navy panel, one display figure, three-row ledger — the strongest thing in the block.
- **The `Not sure` rung.** The honest default for someone who does not know their band, and the reason a
  first-time donor can use the block at all.
- **The Disclaimer row, collapsed, at the very end.** Hard constraint.
- **`How you give` and `Claim your receipt`.** Out of scope; separately declared heights. (One note recorded,
  not acted on: in the full widget those two blocks carry no numeral while the first two do.)
- **Anything that adds a step, a modal, a tooltip or a wizard.** The block is used once, on a phone, by
  someone slightly suspicious. Fewer states, not more.

---

## 8 · Decisions I need from the client

| # | Question | My recommendation |
|---|---|---|
| 1 | Approve the two new strings (`Use an income range instead`, `Common questions`)? | Yes — both are structural, not editorial |
| 2 | Approve the optional fourth question about the 35 % cap? | Yes on the copy; it cannot be drawn until the 320 px question below is settled (+49 px) |
| 3 | The months chips: delete them, or delete the `<select>`? | Delete the chips. The `<select>` is the only control that can say 4 months, and the chips cost 106 px in the state that sets the height. Deleting the select instead saves 60 px and loses eight values. |
| 4 | At 320 px, option A (raise the declaration to 2,010) or option B (hide the note in exact mode)? | A. Nothing statutory goes behind a state. |
| 5 | Does their CMS team own the FAQ page? | If yes, (c) as proposed. If no, fall back to (a) with eligibility left in the input half. |
| 6 | Renumber the result 2 → 3? | Yes — it makes the full widget a numbered spine and costs nothing in height |
