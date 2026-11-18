#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Payment block: QR on desktop, tap-through rows on mobile (19 Nov 2026).

Kevin: "for payment module, it should show the QR code in desktop, and no qr code in
mobile but clickable links, perhaps we can use the PayMe, Alipay HK and Credit Card
logo/icons?"

Two things this run establishes:

1. The charity ALREADY publishes live PayMe and AlipayHK donation codes on its own
   ways-to-give page. Both decode (opencv QRCodeDetector):
     PayMe     -> https://qr.payme.hsbc.com.hk/2/J9idwVdAVdVPhjocykRTAB
     AlipayHK  -> https://render.alipay.hk/p/s/hkwallet/landing?scheme=alipayhk://…
   so the desktop QR panel is real payment, not a placeholder.

2. There are no official logo files anywhere on their site (only these co-branded QR
   cards, whose wordmark strips are illegible at icon size). The mobile rows therefore
   carry the app name in type with a brand-colour rule, and a logo slot is marked for
   the day the client supplies proper marks.

    python3 qa/apply_payqr_20261119.py --check
    python3 qa/apply_payqr_20261119.py
"""
import shutil
import sys

SRC = "embed/index.html"
BAK = "embed/index.html.bak-pre-payqr-20261119"
CHECK = "--check" in sys.argv

PAYME_URL = "https://qr.payme.hsbc.com.hk/2/J9idwVdAVdVPhjocykRTAB"
ALIPAY_URL = ("https://render.alipay.hk/p/s/hkwallet/landing"
              "?scheme=alipayhk%3A%2F%2Fplatformapi%2Fstartapp%3FappId%3D20000067"
              "%26url%3Dhttps%253A%252F%252Fcod.run%252Fzf950015iae7uhyx")
CARD_URL = "https://www.hollows.org/zh-Hant-HK/donate/"

OLD_BLOCK = '''    <div class="rails">
      <a href="https://www.hollows.org/zh-Hant-HK/ways-to-support/ways-to-give/" target="_top" rel="noopener" data-rail="payme">
        <span class="nm">PayMe</span>
        <span class="sub" data-i18n="s3.payme.sub">Phone wallet</span>
        <span class="go" aria-hidden="true">↗</span>
      </a>
      <a href="https://www.hollows.org/zh-Hant-HK/ways-to-support/ways-to-give/" target="_top" rel="noopener" data-rail="alipay">
        <span class="nm">AlipayHK</span>
        <span class="sub" data-i18n="s3.alipay.sub">Phone wallet</span>
        <span class="go" aria-hidden="true">↗</span>
      </a>
      <a href="https://www.hollows.org/zh-Hant-HK/donate/" target="_top" rel="noopener" data-rail="card">
        <span class="nm" data-i18n="s3.card.nm">Credit card</span>
        <span class="sub" data-i18n="s3.card.sub">On the web page</span>
        <span class="go" aria-hidden="true">↗</span>
      </a>
    </div>'''

NEW_BLOCK = '''    <!-- Desktop: the two live donation codes the Foundation already publishes on its
         own ways-to-give page. Both were decoded from the published assets, so this
         panel takes real payments. Replace assets/logos/*.png when the charity issues
         campaign-tagged codes; nothing else changes. -->
    <div class="paygrid">
      <figure class="qrcard">
        <img src="../assets/logos/payme.png" width="450" height="350"
             alt="PayMe donation QR code for The Fred Hollows Foundation">
        <figcaption><b>PayMe</b><span data-i18n="s3.scan">Scan with your phone</span></figcaption>
      </figure>
      <figure class="qrcard">
        <img src="../assets/logos/alipayhk.png" width="450" height="350"
             alt="AlipayHK donation QR code for The Fred Hollows Foundation">
        <figcaption><b>AlipayHK</b><span data-i18n="s3.scan">Scan with your phone</span></figcaption>
      </figure>
      <a class="qrcard card" href="''' + CARD_URL + '''" target="_top" rel="noopener" data-rail="card">
        <span class="glyph" aria-hidden="true">
          <svg viewBox="0 0 24 17" width="46" height="33" fill="none" stroke="currentColor" stroke-width="1.4">
            <rect x="1" y="1" width="22" height="15" rx="2.5"/>
            <path d="M1 6h22" stroke-width="2.6"/>
            <path d="M4.5 11.5h5"/>
          </svg>
        </span>
        <figcaption><b data-i18n="s3.card.nm">Credit card</b><span data-i18n="s3.card.sub">On the Foundation's donation page</span></figcaption>
      </a>
    </div>

    <!-- Mobile: no QR (you cannot scan your own screen) — each row opens the payment
         app or the card page directly. The <i class="mark"> slot is where an official
         logo goes once the client supplies one; until then the brand rule carries it. -->
    <div class="rails">
      <a href="''' + PAYME_URL + '''" target="_top" rel="noopener" data-rail="payme" class="r-payme">
        <span class="nm">PayMe</span>
        <span class="sub" data-i18n="s3.payme.sub">Open PayMe and give</span>
        <span class="go" aria-hidden="true">↗</span>
      </a>
      <a href="''' + ALIPAY_URL + '''" target="_top" rel="noopener" data-rail="alipay" class="r-alipay">
        <span class="nm">AlipayHK</span>
        <span class="sub" data-i18n="s3.alipay.sub">Open AlipayHK and give</span>
        <span class="go" aria-hidden="true">↗</span>
      </a>
      <a href="''' + CARD_URL + '''" target="_top" rel="noopener" data-rail="card" class="r-card">
        <span class="nm" data-i18n="s3.card.nm">Credit card</span>
        <span class="sub" data-i18n="s3.card.sub">On the Foundation's donation page</span>
        <span class="go" aria-hidden="true">↗</span>
      </a>
    </div>'''

CSS_ANCHOR = ".rails{display:grid;border-top:var(--rule);margin-top:18px}"

CSS_ADD = """.rails{display:grid;border-top:var(--rule);margin-top:18px}
/* ── payment: QR on a desktop, tap-through rows on a phone ──────────────────────
   A donor cannot scan the screen they are reading, so the two arrangements are
   mutually exclusive rather than progressive. Breakpoint 720px: below it every
   real phone and every narrow CMS column gets the rows. */
.paygrid{display:none}
.rails a.r-payme{border-left:3px solid #E2001A;padding-left:14px}
.rails a.r-alipay{border-left:3px solid #1677FF;padding-left:14px}
.rails a.r-card{border-left:3px solid var(--navy);padding-left:14px}
@media (min-width:720px){
  .rails{display:none}
  .paygrid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:var(--gut);
           border-top:var(--rule);margin-top:18px;padding-top:26px;align-items:start}
  .qrcard{margin:0;display:block;color:inherit;text-decoration:none}
  .qrcard img{display:block;width:100%;max-width:190px;height:auto;border-radius:10px;
              border:1px solid var(--line);background:var(--white)}
  .qrcard .glyph{display:flex;align-items:center;justify-content:center;
                 width:190px;height:148px;border:1px solid var(--line);border-radius:10px;
                 color:var(--navy);background:var(--white)}
  .qrcard figcaption{margin-top:12px;font-size:var(--t-cap);color:var(--muted);line-height:1.5}
  .qrcard figcaption b{display:block;font-size:var(--t-sm);font-weight:600;color:var(--ink);
                       letter-spacing:-.01em;margin-bottom:2px}
  .qrcard.card:hover .glyph{border-color:var(--line-2)}
  .qrcard.card:hover figcaption b{color:var(--navy)}
  .qrcard:hover img{border-color:var(--line-2)}
}"""

STRINGS = [
    # the lede now has to explain two arrangements in one line
    ('"s3.lede": "三種方式均於護瞳行動的捐款頁完成。"',
     '"s3.lede": "以手機掃描二維碼，或直接於本裝置開啟付款 App。"'),
    ('"s3.lede": "All three finish on the Foundation\'s donation page."',
     '"s3.lede": "Scan the code with your phone, or open the app on this device."'),
    # mobile row copy: they now open the app, they do not "go to a page"
    ('"s3.payme.sub": "手機錢包"', '"s3.payme.sub": "開啟 PayMe 完成捐款"'),
    ('"s3.alipay.sub": "手機錢包"', '"s3.alipay.sub": "開啟 AlipayHK 完成捐款"'),
    ('"s3.payme.sub": "Phone wallet"', '"s3.payme.sub": "Open PayMe and give"'),
    ('"s3.alipay.sub": "Phone wallet"', '"s3.alipay.sub": "Open AlipayHK and give"'),
    ('"s3.card.sub": "網頁付款"', '"s3.card.sub": "於護瞳行動捐款頁以信用卡捐款"'),
    ('"s3.card.sub": "On the web page"', '"s3.card.sub": "On the Foundation\'s donation page"'),
    # the static fallbacks keep the same shape
    ('<p class="lede" data-i18n="s3.lede">All three finish on the Foundation\'s donation page.</p>',
     '<p class="lede" data-i18n="s3.lede">Scan the code with your phone, or open the app on this device.</p>'),
]


def main():
    html = open(SRC, encoding="utf-8").read()

    if html.count(OLD_BLOCK) != 1:
        raise SystemExit("FAIL: rails block not found exactly once — has the markup drifted?")
    html = html.replace(OLD_BLOCK, NEW_BLOCK)

    if html.count(CSS_ANCHOR) != 1:
        raise SystemExit("FAIL: CSS anchor not found exactly once")
    html = html.replace(CSS_ANCHOR, CSS_ADD)

    # new string, both tables
    zh_anchor = '      "s3.h": "捐款方式",\n'
    en_anchor = '      "s3.h": "How you give",\n'
    if html.count(zh_anchor) != 1 or html.count(en_anchor) != 1:
        raise SystemExit("FAIL: s3.h anchors not unique")
    html = html.replace(zh_anchor, zh_anchor + '      "s3.scan": "用手機掃描",\n')
    html = html.replace(en_anchor, en_anchor + '      "s3.scan": "Scan with your phone",\n')

    for old, new in STRINGS:
        n = html.count(old)
        if n != 1:
            raise SystemExit(f"FAIL: expected 1, found {n}\n  {old[:110]}")
        html = html.replace(old, new)

    # the live payment endpoints must be present exactly as decoded
    for url, label in ((PAYME_URL, "PayMe"), (ALIPAY_URL, "AlipayHK")):
        if html.count(url) != 1:
            raise SystemExit(f"FAIL: {label} endpoint not present exactly once")
    # code comments legitimately say "POC" (this file's own header does); what must not
    # carry it is the copy a donor reads, i.e. the two string tables.
    tables = html.split('  "zh-HK": {', 1)[1].split('  };', 1)[0]
    for bad in ("POC", "test code", "示意", "placeholder"):
        if bad in tables:
            raise SystemExit(f"FAIL: '{bad}' present in the copy tables")

    print("payment block rebuilt: desktop QR grid (2 live codes + card tile) / mobile rows")
    if CHECK:
        print("CHECK OK — nothing written")
        return
    shutil.copyfile(SRC, BAK)
    open(SRC, "w", encoding="utf-8").write(html)
    print(f"applied → {SRC} (backup {BAK})")


if __name__ == "__main__":
    main()
