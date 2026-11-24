#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Port the approved Option B payment block into embed/index.html.

Kevin chose Option B ("size by function") from `design/pay-desktop/options.html`
on 24 Nov and asked for a bigger QR. Both are applied here, once, in a script
rather than by hand, so the transformation is reviewable and re-runnable:

  1. the desktop pair becomes two tiles — a wide AlipayHK tile (QR + labels +
     the receipt note) and a compact credit-card tile;
  2. the receipt note MOVES into the AlipayHK tile, carrying #payhelp, the
     .helpbtn/.helppop contract and every crop untouched;
  3. the QR becomes the verified tight crop (assets/logos/alipayhk-qr.png);
  4. both tiles are click-anywhere via a stretched link, because a <button>
     (the note's ?) may not be nested inside an <a>.

Mobile is not edited: below 720px the tiles collapse to the one thing a phone
needs from them — the receipt line, still between the two rails.

Run:  python3 qa/apply_pay_optionb_20261124.py [--check]
"""
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "embed" / "index.html"
html = SRC.read_text(encoding="utf-8")

# ── 1 · lift the receipt note (comment + #payhelp) out of .rails ─────────────
NOTE_START = (
    "      <!-- Phase 1: the receipt route for an AlipayHK gift. AlipayHK issues the"
)
NOTE_END = (
    "      </div>\n"
    "\n"
    "      <a href=\"https://www.hollows.org/zh-Hant-HK/donate/\" target=\"_top\" "
    "rel=\"noopener\" data-rail=\"card\" class=\"r-card\">"
)
i = html.index(NOTE_START)
j = html.index(NOTE_END, i)
note = html[i:j + len("      </div>\n")]
rails_after = html[j + len("      </div>\n"):]          # starts with the blank line

assert note.count('id="payhelp"') == 1, "expected exactly one #payhelp in the note"
assert note.count('id="alipay-help-panel"') == 1
assert note.count("alipay-receipt-o") == 6, "six receipt crops must travel with the note"

# Option B marks the note with a 6px dot; the copy and the button are untouched
assert note.count('        <p class="payhelp-line">\n'
                  '          <span data-i18n="s3.receipt.line">') == 1
note = note.replace(
    '        <p class="payhelp-line">\n'
    '          <span data-i18n="s3.receipt.line">',
    '        <p class="payhelp-line">\n'
    '          <span class="payhelp-dot" aria-hidden="true"></span>\n'
    '          <span data-i18n="s3.receipt.line">',
    1,
)

# the note now sits inside .tile-a-txt → +4 spaces of indent
note_indented = "\n".join(("    " + ln) if ln.strip() else ln for ln in note.split("\n"))

# ── 2 · the new desktop pair ────────────────────────────────────────────────
OLD_PAIR_START = (
    "    <!-- Desktop: the live AlipayHK donation code the Foundation already publishes on"
)
OLD_PAIR_END = (
    "        <figcaption><b data-i18n=\"s3.card.nm\">Credit card</b>"
    "<span data-i18n=\"s3.card.sub\">On the Foundation's donation page</span></figcaption>\n"
    "      </a>\n"
    "    </div>\n"
)
k = html.index(OLD_PAIR_START)
l = html.index(OLD_PAIR_END, k) + len(OLD_PAIR_END)

ALIPAY_URL = (
    "https://render.alipay.hk/p/s/hkwallet/landing?scheme=alipayhk%3A%2F%2Fplatformapi"
    "%2Fstartapp%3FappId%3D20000067%26url%3Dhttps%253A%252F%252Fcod.run%252Fzf950015iae7uhyx"
)
CARD_URL = "https://www.hollows.org/zh-Hant-HK/donate/"

NEW_PAIR = f"""    <!-- Desktop, Option B (approved 24 Nov): the QR is the only element that has
         to be a picture, so its tile carries the width; the card is a link, so it
         becomes a compact tile. Both tiles are click-anywhere, but the tile is a
         <div> and only its own <a> stretches over it: the receipt note inside the
         AlipayHK tile holds a <button>, and a button may not live inside an <a>.
         The code is the tight crop — 264px, the code plus the spec's 4-module
         quiet zone — because the published card is 450x350 with the code at 212px
         inside 119px of white a side, which at 190px rendered a ~90px code no
         scanner decodes. Same code, same destination, bigger on screen. -->
    <div class="paygrid">
      <div class="tile tile-a">
        <img class="tile-qr" loading="lazy" src="../assets/logos/alipayhk-qr.png" width="264" height="264"
             alt="AlipayHK donation QR code for The Fred Hollows Foundation" data-i18n-alt="s3.qr.alt.alipay">
        <div class="tile-a-txt">
          <a class="tile-link" href="{ALIPAY_URL}" target="_top" rel="noopener" data-rail="alipay">
            <b class="tile-nm">AlipayHK</b>
          </a>
          <span class="tile-sub" data-i18n="s3.scan">Scan with your phone</span>
{note_indented}        </div>
      </div>
      <div class="tile tile-b">
        <span class="tile-glyph" aria-hidden="true">
          <svg viewBox="0 0 24 17" width="46" height="33" fill="none" stroke="currentColor" stroke-width="1.4">
            <rect x="1" y="1" width="22" height="15" rx="2.5"/>
            <path d="M1 6h22" stroke-width="2.6"/>
            <path d="M4.5 11.5h5"/>
          </svg>
        </span>
        <a class="tile-link" href="{CARD_URL}" target="_top" rel="noopener" data-rail="card">
          <b class="tile-nm" data-i18n="s3.card.nm">Credit card</b>
        </a>
        <span class="tile-foot">
          <span data-i18n="s3.card.sub">On the Foundation's donation page</span>
          <span class="go" aria-hidden="true">↗</span>
        </span>
      </div>
    </div>
"""

out = html[:k] + html[l:i] + "\n".join(
    ("  " + ln) if ln.strip() else ln for ln in NEW_PAIR.split("\n")
) + rails_after.lstrip("\n")
# (html[l:i] is the mobile-rails comment block plus the AlipayHK row, which stays
# exactly as it was; the new pair is inserted where the note used to sit, so on a
# phone the note is still BETWEEN the two rails — it is simply nested inside the
# tile now, and the tile collapses to nothing but the note below 720px.)

# ── 3 · the pair belongs INSIDE .rails, or the note renders above both rails ──
assert out.index('<div class="rails">') < out.index('<div class="paygrid">')
assert out.index('<div class="paygrid">') < out.index('data-rail="card" class="r-card"')

# the note now carries the Option B dot; the copy and the button are untouched
assert out.count('id="payhelp"') == 1, "the note must exist exactly once"
assert out.count('class="payhelp-line"') == 1
assert 'class="payhelp-dot"' in out

if "--check" in sys.argv:
    print("would rewrite", SRC)
    print(out[out.index('    <!-- Desktop, Option B'):out.index('    <!-- Mobile: no QR')][:4000])
    raise SystemExit(0)

SRC.write_text(out, encoding="utf-8")
print(f"rewrote {SRC} ({len(html)} → {len(out)} bytes)")
