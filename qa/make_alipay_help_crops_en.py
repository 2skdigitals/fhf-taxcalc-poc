#!/usr/bin/env python3
"""Build the ENGLISH AlipayHK receipt-help crops for the tax-calculator tooltip.

Source: the client's seven WhatsApp captures in
  ~/Downloads/Alipay_Receipt_Application EN/     (942 x 2048 JPEG)
Output: assets/help/alipay-receipt-en-*.webp      (320 wide, RGB)

The Chinese crops beside these were the client's own annotated screens; the
English captures carry NO annotation, so this script draws the same red
highlight (3px at 320, sampled off the Chinese sources: #EE0D01) and applies the
same masking discipline:

  * the transaction reference line and the gift amount are painted out on the
    donation-record screen — a published reference is the key a receipt claim
    matches on, so it must never reach a public page, and a HK$10 test gift
    contradicts a widget that refuses anything under HK$100;
  * donor name / email / phone / postal address appear only as empty
    placeholders (the client's own form was never filled);
  * crops are pixel coordinates at 942 scale, then resized to 320 wide — never
    proportional, which is what clipped a row on the Chinese pass.

Re-runnable: python3 qa/make_alipay_help_crops_en.py [--preview]
  --preview writes 2x PNGs to /tmp/en-crops-preview/ instead of the assets,
  so a crop can be looked at before it ships.
"""
import sys, pathlib
from PIL import Image, ImageDraw

SRC = pathlib.Path.home() / "Downloads" / "Alipay_Receipt_Application EN"
ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "help"
PREVIEW = pathlib.Path("/tmp/en-crops-preview")
W = 320                       # every crop is 320 wide (matches the Chinese set)
RED = (238, 13, 1)            # sampled from the client's own Chinese annotations
BORDER = 6                    # 6px at 942 -> ~2-3px at 320

# name -> (source file, crop box, red box or None, [(mask box, fill), ...])
JOBS = [
    # Option 1, step 1 — the unticked "Receipt request" row under the amount
    ("alipay-receipt-en-o1-step-1",
     "WhatsApp Image 2026-11-26 at 11.56.36.jpeg",
     (0, 1150, 942, 1420), (20, 1300, 925, 1400), []),
    # Option 1, step 2 — ticked, donor form open (placeholders only)
    ("alipay-receipt-en-o1-step-2",
     "WhatsApp Image 2026-11-26 at 11.56.36 (1).jpeg",
     (0, 440, 942, 1850), None, []),
    # Option 2, step 1 — home screen, Charity in the shortcut grid
    ("alipay-receipt-en-o2-step-1",
     "WhatsApp Image 2026-11-26 at 11.56.35.jpeg",
     (0, 225, 942, 1330), (585, 690, 722, 852), []),
    # Option 2, step 2 — Mine menu, Donation record row
    ("alipay-receipt-en-o2-step-2",
     "WhatsApp Image 2026-11-26 at 11.56.35 (2).jpeg",
     (0, 540, 942, 1285), (118, 1020, 920, 1146), []),
    # Option 2, step 3 — the record itself: amount + reference painted out
    ("alipay-receipt-en-o2-step-3",
     "WhatsApp Image 2026-11-26 at 11.56.35 (3).jpeg",
     (0, 140, 942, 620), (18, 258, 922, 496),
     [((726, 303, 942, 378), "white"),      # HK$10 + chevron
      ((205, 426, 780, 490), "white")]),    # AlipayHK transaction reference
    # Option 2, step 4 — the Receipt request button
    ("alipay-receipt-en-o2-step-4",
     "WhatsApp Image 2026-11-26 at 11.56.35 (4).jpeg",
     (0, 1430, 942, 1700), (60, 1449, 882, 1568), []),
]

# The Charity Donation landing capture carries no step in the four-step flow —
# the Chinese build dropped its equivalent for the same reason (the Mine menu
# already answers "then Donation record"). Kept here so the decision is visible.


def build():
    PREVIEW.mkdir(exist_ok=True)
    rows = []
    for name, src, crop, box, masks in JOBS:
        im = Image.open(SRC / src).convert("RGB")
        im = im.crop(crop)
        d = ImageDraw.Draw(im)
        for (x0, y0, x1, y1), fill in masks:
            d.rectangle([x0 - crop[0], y0 - crop[1], x1 - crop[0], y1 - crop[1]], fill=fill)
        if box:
            x0, y0, x1, y1 = box
            for i in range(BORDER):
                d.rectangle([x0 - crop[0] + i, y0 - crop[1] + i,
                             x1 - crop[0] - i, y1 - crop[1] - i], outline=RED)
        h = round(im.height * W / im.width)
        im = im.resize((W, h), Image.LANCZOS)
        if "--preview" in sys.argv:
            im.save(PREVIEW / f"{name}.png")
        else:
            im.save(OUT / f"{name}.webp", "WEBP", quality=86, method=6)
        rows.append((name, im.size, (OUT / f"{name}.webp").stat().st_size
                     if "--preview" not in sys.argv else 0))
    for r in rows:
        print(f"{r[0]:34s} {r[1][0]}x{r[1][1]:<5d} {r[2]/1024:.1f} KB" if r[2] else f"{r[0]:34s} {r[1][0]}x{r[1][1]}")


if __name__ == "__main__":
    build()
