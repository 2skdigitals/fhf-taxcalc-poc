# Embed snippets — one iframe per language

**One frame replaces the three part-frames on the English page.** The bare `/embed/` URL already renders the
calculator, the result, the payment panel and the receipt block in sequence, so there is nothing to assemble on
their side.

Verified live 23 Nov 2026: `/embed/` → `lang=zh-Hant-HK`, three content sections (calculator, result, payment);
`/embed/?lang=en` → `lang=en`, three sections. Both return 200. **Phase 1 has no receipt block** — it returns
with PayMe, and `?part=receipt` currently renders an empty 60px frame.

---

## Chinese page — `/zh-Hant-HK/campaigns/charitable-tax-deduction/`

Already correct today. No change needed. For reference:

```html
<iframe
  src="https://2skdigitals.github.io/fhf-taxcalc-poc/embed/"
  title="慈善捐款扣稅計算機"
  style="border:0;width:100%;height:2225px;display:block"
  loading="lazy"></iframe>
```

## English page — `/en-HK/campaigns/charitable-tax-deduction/`

Replace the **three** existing frames (`?part=calc&lang=en`, `?part=pay&lang=en`, `?part=receipt&lang=en`) with
this **one**:

```html
<iframe
  src="https://2skdigitals.github.io/fhf-taxcalc-poc/embed/?lang=en"
  title="Tax deduction calculator"
  style="border:0;width:100%;height:2550px;display:block"
  loading="lazy"></iframe>
```

---

## Heights

| Frame | Height to set | Measured content |
|---|---|---|
| Chinese, calculator → payment | **2225** | 2160 |
| English, calculator → payment | **2550** | 2482 |

Both sizes carry slack, so nothing clips if a string wraps differently at their column width. **These numbers
are current as of 23 Nov 2026**, measured by `qa/sweep_heights.py` after phase 1 (the receipt block hidden, the
AlipayHK receipt line added) — that pass REMOVED ~560–710px from the one-link frame and added ~43px to the payment
block, so any height issued before it is stale. English is still ~260px taller than Chinese at its peak: set the
column for the language you are embedding, never reuse the other.

## Why one frame rather than three

- The donor sees one continuous flow — choose amount, see the result, pay, claim the receipt — instead of three
  panels that each restart the page's vertical rhythm.
- One scroll position, one focus order, one `page_view` context for the events.
- Two fewer iframes to size, lazy-load and keep in step when a block's copy changes.

The three-part split remains available if they ever want the blocks separated again: `?part=calc`, `?part=pay`,
`?part=receipt`, with heights 1720 / 690 / 60 (zh) and 2030 / 800 / 60 (en) — the receipt block is 990 / 1185
when it returns in phase 2.
