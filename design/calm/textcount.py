#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Count visible body-text characters per block, before vs after.

"Visible" = what a donor sees before opening anything: text inside a closed
<details> is excluded (its summary is counted). Measured at 390 and 1280.
"""
import sys
from playwright.sync_api import sync_playwright

JS = r"""() => {
  const root = document.body;
  let n = 0;
  const w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
  const vis = el => {
    if (!el || el.nodeType !== 1) return true;
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden') return false;
    if (el.classList && el.classList.contains('sr')) return false;
    return true;
  };
  let node;
  while ((node = w.nextNode())) {
    let el = node.parentElement;
    if (!el || el.closest('script,style,#dbg')) continue;
    // inside a closed <details>: only the <summary> is visible
    const d = el.closest('details');
    if (d && !d.open && !el.closest('summary')) continue;
    let hidden = false;
    for (let c = el; c && c !== document.documentElement; c = c.parentElement) {
      if (!vis(c)) { hidden = true; break; }
    }
    if (hidden) continue;
    n += node.textContent.replace(/\s+/g, ' ').trim().length;
  }
  return n;
}"""

BEFORE = "file:///Users/cya822/2SK/fred-hollows/work/iframe-poc/embed/index.html"
AFTER = "http://127.0.0.1:8766/index.html"

rows = {}
with sync_playwright() as pw:
    br = pw.chromium.launch(channel="chrome", headless=True)
    for label, base in (("before", BEFORE), ("after", AFTER)):
        for lang in ("en", "zh-HK"):
            for part in ("calc", "pay", "receipt"):
                for w in (390, 1280):
                    p = br.new_page(viewport={"width": w, "height": 400}, is_mobile=(w < 600),
                                    has_touch=(w < 600))
                    p.goto(f"{base}?part={part}&lang={lang}", wait_until="load")
                    p.wait_for_timeout(350)
                    rows.setdefault(f"{part}/{lang}", {})[f"{label}@{w}"] = p.evaluate(JS)
                    p.close()
    br.close()

print(f"{'block':16}{'before@390':>11}{'after@390':>10}{'Δ':>7}   {'before@1280':>12}{'after@1280':>11}{'Δ':>7}")
tot = [0, 0]
for k, v in rows.items():
    b3, a3, b12, a12 = v["before@390"], v["after@390"], v["before@1280"], v["after@1280"]
    tot[0] += b3; tot[1] += a3
    print(f"{k:16}{b3:>11}{a3:>10}{a3-b3:>7}   {b12:>12}{a12:>11}{a12-b12:>7}")
print(f"{'TOTAL @390':16}{tot[0]:>11}{tot[1]:>10}{tot[1]-tot[0]:>7}"
      f"   ({100*(tot[1]-tot[0])/tot[0]:.0f}%)")
