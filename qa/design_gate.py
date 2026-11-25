#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Design gate for the calculator widget — the checks a visual pass must not break.

A colour/contrast pass is exactly the kind of change that quietly fails three ways:
  · a text pair drops under WCAG AA
  · a block grows past the fixed height the client sets in their CMS
  · a touch target shrinks under 44px, or the layout overflows at 320px

So this runs the same suite against any variant directory:

    python3 qa/design_gate.py --base http://127.0.0.1:8765 --label current
    python3 qa/design_gate.py --base http://127.0.0.1:8770 --label uplift-a

Exit code is 0 only when every check passes.
"""
import argparse
import sys

from playwright.sync_api import sync_playwright

# declared heights the client will paste into the CMS (updated per pass)
# heights the client pastes into the CMS — must cover the MONTHLY layout too, which is
# a second, taller shape (that omission shipped a 70px inner scroll at 320px)
DECLARED = {
    "zh-HK": {"calc": 1495, "input": 880, "result": 725, "pay": 505, "receipt": 60, "all": 2010},
    "en": {"calc": 1610, "input": 940, "result": 860, "pay": 535, "receipt": 60, "all": 2130},
}
WIDTHS = (320, 360, 390, 414, 568, 768, 944, 1280, 1440)
PARTS = ("calc", "input", "result", "pay", "receipt", "all")

# Mirrors PHASE1 in embed/index.html. While it is true, section 5 is hidden and
# `?part=receipt` is a placeholder that renders NOTHING — so the disclaimer checks
# below apply to every part that carries content, and the placeholder is asserted
# to be empty instead. Flip this with the widget when PayMe ships.
PHASE1 = True

# the strings a text pair is checked on: the roles a designer actually restyles
CONTRAST_TARGETS = [
    ("block heading", "h2"),
    ("running text", "p.lede"),
    ("hint / note", "p.hint"),
    # 23 Nov: the band remark became a NOTE one step under the hint (12px), so the
    # smallest text on the page is now measured rather than assumed.
    ("band note (12px)", "p.note"),
    ("figure", "#net"),
    ("figure label", "#saved-label, .figs dt, dt"),
    ("primary action", "button[type=submit], .btn"),
    # 25 Nov: the disclaimer (an h3 + <ol> until this pass) left the widget for the
    # client's own page, so the smallest text role on the page is now the consent
    # line in the receipt form — still `.fine`, still 13px, still the pair that says
    # whether the fine print is legible. It lives in the phase-2 block, which is why
    # the contrast pass runs on ?part=calc&lang=en with the form hidden: computed
    # style still resolves, and a colour change to the smallest role is exactly what
    # this target exists to catch.
    ("fine print (consent line)", "p.fine"),
]

MEASURE_JS = """(sel) => {
  const el = document.querySelector(sel);
  if (!el) return null;
  const cs = getComputedStyle(el);
  const size = parseFloat(cs.fontSize);
  const weight = cs.fontWeight;
  // walk up for the first non-transparent background
  let bg = cs.backgroundColor, node = el, found = false;
  while (node) {
    const b = getComputedStyle(node).backgroundColor;
    if (b && !/rgba\(0, 0, 0, 0\)|transparent/.test(b)) { bg = b; found = true; break; }
    node = node.parentElement;
  }
  // The widget is deliberately transparent: the CMS page's own ground shows through.
  // With no solid background inside the frame, white is the honest assumption, and the
  // gate says so rather than comparing text against black.
  if (!found) bg = 'rgb(255, 255, 255)';
  return {color: cs.color, bg, size, weight, transparent: !found,
          text: (el.textContent || '').trim().slice(0, 40)};
}"""


def parse_rgb(s):
    if s.startswith("rgb("):
        parts = s[4:-1].split(",")
    elif s.startswith("rgba("):
        parts = s[5:-1].split(",")
    else:
        return None
    try:
        return tuple(float(p) for p in parts[:3])
    except ValueError:
        return None


def lin(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def ratio(fg, bg):
    L1 = 0.2126 * lin(fg[0]) + 0.7152 * lin(fg[1]) + 0.0722 * lin(fg[2])
    L2 = 0.2126 * lin(bg[0]) + 0.7152 * lin(bg[1]) + 0.0722 * lin(bg[2])
    hi, lo = max(L1, L2), min(L1, L2)
    return (hi + 0.05) / (lo + 0.05)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--label", default="variant")
    args = ap.parse_args()

    fails, notes = [], []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel="chrome")

        # ── A · contrast, on the block a donor actually reads the numbers in
        pg = browser.new_page(viewport={"width": 1100, "height": 1500})
        pg.goto(f"{args.base}/embed/?part=calc&lang=en", wait_until="load")
        pg.wait_for_timeout(900)
        for name, sel in CONTRAST_TARGETS:
            m = pg.evaluate(MEASURE_JS, sel)
            if not m:
                notes.append(f"{name}: selector {sel!r} not found (skipped)")
                continue
            fg, bg = parse_rgb(m["color"]), parse_rgb(m["bg"])
            if not fg or not bg:
                notes.append(f"{name}: unparseable colours {m['color']} / {m['bg']}")
                continue
            r = ratio(fg, bg)
            large = m["size"] >= 24 or (m["size"] >= 18.66 and int(float(m["weight"])) >= 700)
            need = 3.0 if large else 4.5
            ok = r >= need
            line = f"{name}: {r:.2f}:1 (need {need}) {m['size']:.0f}px/{m['weight']} {m['text']!r}"
            (notes if ok else fails).append(("PASS " if ok else "FAIL ") + line)
        pg.close()

        # ── B · fixed-height fit and horizontal overflow, every width, both languages
        for lang, url in (("zh-HK", "?part=$P"), ("en", "?part=$P&lang=en")):
            for w in WIDTHS:
                pg = browser.new_page(viewport={"width": w, "height": 900})
                for part in PARTS:
                    pg.goto(f"{args.base}/embed/{url.replace('$P', part)}", wait_until="load")
                    pg.wait_for_timeout(260)
                    d = pg.evaluate("""() => {
                      const els = [...document.querySelectorAll('section, .foot, p.fine')].filter(e => e.offsetParent);
                      const bottom = els.length ? Math.max(...els.map(e => e.getBoundingClientRect().bottom)) : 0;
                      return {bottom: Math.round(bottom),
                              over: document.documentElement.scrollWidth > document.documentElement.clientWidth + 1};
                    }""")
                    declared = DECLARED[lang][part]
                    if d["over"]:
                        fails.append(f"FAIL overflow {lang}/{w}px/{part}: horizontal scrollbar")
                    if d["bottom"] > declared:
                        fails.append(f"FAIL height {lang}/{w}px/{part}: content {d['bottom']} > declared {declared}")
                pg.close()

        # ── C · touch targets inside the embedded blocks
        pg = browser.new_page(viewport={"width": 390, "height": 900}, is_mobile=True, has_touch=True)
        for part in ("calc", "pay", "receipt"):
            pg.goto(f"{args.base}/embed/?part={part}", wait_until="load")
            pg.wait_for_timeout(500)
            # WCAG 2.5.8 exempts links set inside a sentence, so only measure real
            # controls: buttons, selects, summary rows, and the consent label (not the
            # bare 20px checkbox riding inside it).
            small = pg.evaluate("""() => {
              const els = [...document.querySelectorAll('button, select, summary, label.consent')].filter(e => e.offsetParent);
              return els.map(e => ({tag: e.tagName + (e.id ? '#' + e.id : ''), h: Math.round(e.getBoundingClientRect().height)}))
                        .filter(o => o.h > 0 && o.h < 44);
            }""")
            for s in small:
                fails.append(f"FAIL tap target {part}: {s['tag']} is {s['h']}px")
        pg.close()

        # ── D0 · every same-origin request must actually resolve. A variant authored in
        #     its own folder keeps working there and 404s the moment it is merged: that is
        #     how the two payment QR images shipped dead (src="assets/…" not "../assets/…").
        pg = browser.new_page(viewport={"width": 1280, "height": 900})
        bad = []
        pg.on("response", lambda r: bad.append((r.status, r.url)) if r.status >= 400 else None)
        for part in PARTS:
            pg.goto(f"{args.base}/embed/?part={part}", wait_until="load")
            pg.wait_for_timeout(500)
        pg.close()
        for status, url in bad:
            fails.append(f"FAIL asset {status}: {url}")

        # ── E · images that are present but empty render as a dead box
        pg = browser.new_page(viewport={"width": 1280, "height": 900})
        pg.goto(f"{args.base}/embed/?part=pay", wait_until="load")
        pg.wait_for_timeout(900)
        broken = pg.evaluate("""() => [...document.images]
            .filter(i => i.offsetParent && (!i.complete || i.naturalWidth === 0))
            .map(i => i.getAttribute('src'))""")
        pg.close()
        for src in broken:
            fails.append(f"FAIL image did not load: {src}")

        # ── D · the disclaimer is GONE, and every block ends clean without it
        # 25 Nov: the client carries the legal notice in a Rich Text Editor block on
        # their own page, so the widget must not carry it in any part. This check used
        # to assert the opposite three times over (visible, five items, a heading) —
        # it inverts rather than disappears, because the failure mode now is a later
        # pass restoring the block "because the parts look bare".
        #
        # Two things are still worth measuring per block: no `#disclaimer` and no
        # page-level `p.fine`, and the document ending on the last visible panel with
        # only `.wrap`'s own bottom padding under it. An orphan `border-top` (the
        # removed block's rule) or a stray margin reads as a broken end to the block
        # and is invisible in a passing crop — this is the check that sees it.
        for part in PARTS:
            pg = browser.new_page(viewport={"width": 390, "height": 60 if (PHASE1 and part == "receipt") else 900})
            pg.goto(f"{args.base}/embed/?part={part}", wait_until="load")
            pg.wait_for_timeout(400)
            if PHASE1 and part == "receipt":
                # phase 1: this block is a placeholder. It must render nothing at all —
                # a half-drawn receipt form is the failure, and a form that cannot
                # submit inside a frame a CMS may still point at is the worse one.
                e = pg.evaluate("""() => {
                  const vis = [...document.querySelectorAll('section, form, input, button, p')]
                      .filter(x => x.offsetParent && x.getBoundingClientRect().height > 0
                                   && (x.textContent || '').trim().length);
                  return {sh: document.documentElement.scrollHeight,
                          receipt: !!document.getElementById('receipt').offsetParent,
                          disc: !!document.getElementById('disclaimer'),
                          visible: vis.map(x => x.tagName + (x.id ? '#' + x.id : '')).slice(0, 5)};
                }""")
                if e["receipt"] or e["sh"] > 61:
                    fails.append(f"FAIL ?part=receipt is not an empty placeholder in phase 1: {e}")
                if e["disc"]:
                    fails.append(f"FAIL ?part=receipt still renders the disclaimer: {e}")
                pg.close()
                continue
            d = pg.evaluate("""() => {
              const wrap = document.querySelector('.wrap');
              const vis = e => e.offsetParent && e.getBoundingClientRect().height > 0
                               && getComputedStyle(e).display !== 'none';
              const kids = [...wrap.children].filter(vis);
              const last = kids[kids.length - 1];
              const edge = last.getBoundingClientRect().bottom + window.scrollY;
              // elements, not a gap: `.wrap` carries min-height:100vh, so a short block
              // is legitimately taller than its content and a gap check calls that
              // viewport stretch orphan spacing.
              const tail = last ? [...wrap.querySelectorAll('*')].filter(e => {
                  if (e.offsetParent === null || getComputedStyle(e).display === 'none') return false;
                  if (e.contains(last) || last.contains(e)) return false;
                  const r = e.getBoundingClientRect();
                  return r.height > 0 && r.top + window.scrollY > edge + 1;
                }).map(e => e.tagName + (e.id ? '#' + e.id : '')).slice(0, 4) : [];
              return {disc: !!document.getElementById('disclaimer'),
                      wrapFine: document.querySelectorAll('.wrap > p.fine').length,
                      last: last ? last.tagName + (last.id ? '#' + last.id : '') : null,
                      tail: tail,
                      rule: last ? getComputedStyle(last).borderBottomWidth : ''};
            }""")
            if d["disc"]:
                fails.append(f"FAIL the disclaimer is back in ?part={part}")
            if d["wrapFine"]:
                fails.append(f"FAIL {d['wrapFine']} page-level p.fine line(s) close ?part={part}")
            if not d["last"] or not d["last"].startswith("SECTION#"):
                fails.append(f"FAIL ?part={part} does not end on a panel: {d['last']}")
            if d["tail"]:
                fails.append(f"FAIL something still renders below the last panel in ?part={part}: {d['tail']}")
            if d["rule"] not in ("0px", ""):
                fails.append(f"FAIL ?part={part} ends on a panel that carries a bottom rule ({d['rule']})")
            pg.close()

        browser.close()

    if any('transparent' in n for n in notes):
        pass
    for n in notes:
        print(n)
    for f in fails:
        print(f)
    print(f"\n=== design gate [{args.label}]: {len(notes) - sum(1 for n in notes if n.startswith('PASS'))} notes, "
          f"{len(fails)} failures ===")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
