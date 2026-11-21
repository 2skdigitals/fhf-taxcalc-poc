#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Drop the PayMe rail, 21 Nov 2026.

Kevin: PayMe is out. The payment block keeps AlipayHK and the credit card.

Every replacement asserts its old string occurs EXACTLY once — a string found
twice means the edit would land somewhere it was not measured, and zero means
the copy has already drifted. Run it against a .bak; it is idempotent in the
sense that a second run fails loudly rather than corrupting the file.

    /Library/Developer/CommandLineTools/usr/bin/python3 qa/apply_payme_removal_20261121.py
"""
import pathlib
import sys

SRC = pathlib.Path(__file__).resolve().parent.parent / "embed" / "index.html"
src = SRC.read_text(encoding="utf-8")
rows = []


def sub(label, old, new, want=1):
    global src
    n = src.count(old)
    if n != want:
        sys.exit(f"ABORT  {label}: expected {want} occurrence(s), found {n}\n---\n{old[:200]}")
    src = src.replace(old, new)
    rows.append((label, n))


# ── 1 · CSS ─────────────────────────────────────────────────────────────────
sub("css · the unused .r-payme rule",
    '.rails a.r-payme{border-left:3px solid #E2001A;padding-left:14px}\n',
    '')

sub("css · paygrid 3 columns → 2 equal columns, held to a pair width",
    '  .paygrid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:var(--gut);\n'
    '           border-top:var(--rule);margin-top:18px;padding-top:26px;align-items:start}',
    '  /* Two rails, so two equal columns — and the pair is held to a pair-width, or a\n'
    '     190px code and a 190px card drift 800px apart on a wide desktop. */\n'
    '  .paygrid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:var(--gut);\n'
    '           max-width:min(100%,520px);\n'
    '           border-top:var(--rule);margin-top:18px;padding-top:26px;align-items:start}')

# ── 2 · desktop markup ──────────────────────────────────────────────────────
sub("markup · the desktop comment still says 'two live codes'",
    '    <!-- Desktop: the two live donation codes the Foundation already publishes on its\n'
    '         own ways-to-give page. Both were decoded from the published assets, so this\n'
    '         panel takes real payments. Replace assets/logos/*.png when the charity issues\n'
    '         campaign-tagged codes; nothing else changes. -->',
    '    <!-- Desktop: the live AlipayHK donation code the Foundation already publishes on\n'
    '         its own ways-to-give page, decoded from the published asset, so this panel\n'
    '         takes real payments. Replace assets/logos/*.png when the charity issues a\n'
    '         campaign-tagged code; nothing else changes. -->')

sub("markup · the PayMe QR figure",
    '      <figure class="qrcard">\n'
    '        <img loading="lazy" src="../assets/logos/payme.png" width="450" height="306"\n'
    '             alt="PayMe donation QR code for The Fred Hollows Foundation" data-i18n-alt="s3.qr.alt.payme">\n'
    '        <figcaption><b>PayMe</b><span data-i18n="s3.scan">Scan with your phone</span></figcaption>\n'
    '      </figure>\n',
    '')

# ── 3 · mobile markup ───────────────────────────────────────────────────────
sub("markup · the PayMe tap-through row",
    '      <a href="https://qr.payme.hsbc.com.hk/2/J9idwVdAVdVPhjocykRTAB" target="_top" rel="noopener" data-rail="payme" class="r-payme">\n'
    '        <span class="nm">PayMe</span>\n'
    '        <span class="sub" data-i18n="s3.payme.sub">Open PayMe and give</span>\n'
    '        <span class="go" aria-hidden="true">↗</span>\n'
    '      </a>\n',
    '')

# ── 4 · i18n, both tables ───────────────────────────────────────────────────
sub("i18n zh · s3.qr.alt.payme",
    '      "s3.qr.alt.payme": "PayMe 捐款二維碼（護瞳行動）",\n', '')
sub("i18n zh · s3.payme.sub",
    '      "s3.payme.sub": "開啟 PayMe 完成捐款",\n', '')
sub("i18n zh · s3.lede names the two rails that are left",
    '      "s3.lede": "以手機掃描二維碼，或直接於本裝置開啟付款 App。",',
    '      "s3.lede": "以手機掃描 AlipayHK 二維碼，或於護瞳行動網站以信用卡付款。",')

sub("i18n en · s3.qr.alt.payme",
    '      "s3.qr.alt.payme": "PayMe donation QR code for The Fred Hollows Foundation",\n', '')
sub("i18n en · s3.payme.sub",
    '      "s3.payme.sub": "Open PayMe and give",\n', '')
sub("i18n en · s3.lede names the two rails that are left",
    '      "s3.lede": "Scan the code with your phone, or open the app on this device.",',
    '      "s3.lede": "Scan the AlipayHK code with your phone, or pay by credit card on the Foundation\'s donation page.",')

# ── 5 · the dead deep-link bench is keyed by rail ────────────────────────────
sub("js · the deep-link handler branches on a rail that no longer exists",
    '      var scheme = rail === "payme" ? "payme://" : "alipays://platformapi/startapp";',
    '      /* AlipayHK is the only wallet rail on the page: one scheme, one app name,\n'
    '         and nothing to branch on. */\n'
    '      if (rail !== "alipay") return;\n'
    '      var scheme = "alipays://platformapi/startapp";')
sub("js · the app-open message names the rail",
    '      msg.textContent = t("d.dl.open", {app: rail === "payme" ? "PayMe" : "AlipayHK"});',
    '      msg.textContent = t("d.dl.open", {app: "AlipayHK"});')

# ── 6 · equal weight: the card tile loses the generic .card panel ─────────────
# With three tiles the credit card's padded .card box was the widest thing in the
# row and read as a different kind of object. With two, that mismatch is the whole
# layout. Both tiles become the same construction: a bordered 190x148 box + caption.
sub("markup · the card tile drops the generic .card panel",
    '<a class="qrcard card" href="https://www.hollows.org/zh-Hant-HK/donate/"',
    '<a class="qrcard" href="https://www.hollows.org/zh-Hant-HK/donate/"')
sub("css · the card hover follows the class it now has",
    '  .qrcard.card:hover .glyph{border-color:var(--line-2)}\n'
    '  .qrcard.card:hover figcaption b{color:var(--navy)}',
    '  .qrcard:hover .glyph{border-color:var(--line-2)}\n'
    '  .qrcard:hover figcaption b{color:var(--navy)}')

# ── 7 · a running comment that still counts three ───────────────────────────
sub("comment · 'the three rails + QR'",
    '       ?part=pay      the three rails + QR',
    '       ?part=pay      the two rails + QR')

SRC.write_text(src, encoding="utf-8")
for label, n in rows:
    print(f"OK  ×{n}  {label}")
print(f"\nwrote {SRC}  ({len(src)} chars)")
