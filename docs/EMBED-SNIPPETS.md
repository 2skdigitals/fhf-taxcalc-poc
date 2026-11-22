# Embed snippets — one iframe per language

**One frame replaces the three part-frames on the English page.** The bare `/embed/` URL already renders the
calculator, the result, the payment panel and the receipt block in sequence, so there is nothing to assemble on
their side.

Verified live 23 Nov 2026: `/embed/` → `lang=zh-Hant-HK`, four sections; `/embed/?lang=en` → `lang=en`, four
sections. Both return 200.

---

## Chinese page — `/zh-Hant-HK/campaigns/charitable-tax-deduction/`

Already correct today. No change needed. For reference:

```html
<iframe
  src="https://2skdigitals.github.io/fhf-taxcalc-poc/embed/"
  title="慈善捐款扣稅計算機"
  style="border:0;width:100%;height:2880px;display:block"
  loading="lazy"></iframe>
```

## English page — `/en-HK/campaigns/charitable-tax-deduction/`

Replace the **three** existing frames (`?part=calc&lang=en`, `?part=pay&lang=en`, `?part=receipt&lang=en`) with
this **one**:

```html
<iframe
  src="https://2skdigitals.github.io/fhf-taxcalc-poc/embed/?lang=en"
  title="Tax deduction calculator"
  style="border:0;width:100%;height:2990px;display:block"
  loading="lazy"></iframe>
```

---

## Heights

| Frame | Height to set | Measured content |
|---|---|---|
| Chinese, all-in-one | **2880** | 2723 |
| English, all-in-one | **2990** | 2769 |

Both sizes carry slack, so nothing clips if a string wraps differently at their column width. **These numbers
are current as of 23 Nov and will be re-confirmed after the copy pass lands** — the copy changes remove the
amount chips and one accordion and add a help popup, so the content height moves and the declared value will be
reissued with it.

## Why one frame rather than three

- The donor sees one continuous flow — choose amount, see the result, pay, claim the receipt — instead of three
  panels that each restart the page's vertical rhythm.
- One scroll position, one focus order, one `page_view` context for the events.
- Two fewer iframes to size, lazy-load and keep in step when a block's copy changes.

The three-part split remains available if they ever want the blocks separated again: `?part=calc`, `?part=pay`,
`?part=receipt`, with heights 1800 · 580 · 810 (zh) / 910 (en).
