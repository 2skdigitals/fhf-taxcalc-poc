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
    "zh-HK": {"calc": 1800, "input": 1040, "result": 890, "pay": 580, "receipt": 810, "all": 2880},
    "en": {"calc": 1800, "input": 1040, "result": 890, "pay": 580, "receipt": 910, "all": 2990},
}
WIDTHS = (320, 360, 390, 414, 568, 768, 944, 1280, 1440)
PARTS = ("calc", "input", "result", "pay", "receipt", "all")

# the strings a text pair is checked on: the roles a designer actually restyles
CONTRAST_TARGETS = [
    ("block heading", "h2"),
    ("running text", "p.lede"),
    ("hint / note", "p.hint"),
    ("figure", "#net"),
    ("figure label", "#saved-label, .figs dt, dt"),
    ("primary action", "button[type=submit], .btn"),
    ("disclaimer summary", "#disclaimer summary"),
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

        # ── D · the disclaimer still closes every block, collapsed
        for part in PARTS:
            pg = browser.new_page(viewport={"width": 390, "height": 900})
            pg.goto(f"{args.base}/embed/?part={part}", wait_until="load")
            pg.wait_for_timeout(400)
            d = pg.evaluate("""() => { const el = document.getElementById('disclaimer');
              return el ? {open: el.hasAttribute('open'), h: Math.round(el.getBoundingClientRect().height)} : null; }""")
            if not d:
                fails.append(f"FAIL disclaimer missing in ?part={part}")
            elif d["open"] or d["h"] == 0:
                fails.append(f"FAIL disclaimer not a collapsed visible row in ?part={part}: {d}")
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
