#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rebuild the AlipayHK receipt tooltip so it teaches BOTH of the client's flows.

Denise reviewed the single-flow tooltip (慈善捐款 → 我的捐款 → 捐款記錄 → find the
gift → 申請收據) and sent two distinct routes a donor can take. Both are real, and
the easier one was missing:

  Option 1 — at donation time: tick 「需要收據」 under the amount and the
             「捐款人資料」 form opens. Two steps. LED FIRST, because it is the
             path that avoids a claim later.
  Option 2 — after giving: the old five-step route, now four steps, from the
             donation records.

Shape kept: ONE dialog, the same .helpbtn/.helppop contract (role=dialog,
aria-expanded, Escape, focus return, upward opening from 720px), a 420px width
and the same max-height behaviour. No tabs and no second popover — the panel
scrolls, and Option 1 must be read first. Two headed sections inside it; the
heading is 13px bold navy (the --t-cap step) against step labels at 12px
uppercase muted (the --t-eyebrow step), so the hierarchy is legible with no new
size, colour, face or shadow.

Images: the six supplied 320×529 WebP crops (~67 KB total). The first is
loading="eager" (a lazy image in a hidden panel paints blank on open); the rest
are lazy, and warmed on first open so the panel is never an empty box. The five
superseded crops are deleted once nothing references them.

Strings are character-for-character the client's table; the Chinese app labels
(需要收據, 捐款人資料, 我的捐款, 捐款記錄, 申請收據, 慈善捐款) stay in Chinese inside
the English sentences on purpose — a reader matches what the app shows them.

Run from the repo root:  python3 qa/apply_alipay_two_options_20261124.py
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HTML = ROOT / "embed" / "index.html"
ASSETS = ROOT / "assets" / "help"

src = HTML.read_bytes().decode("utf-8")
orig = src


def must(hay, needle, what):
    n = hay.count(needle)
    if n != 1:
        raise SystemExit(f"anchor {what!r}: found {n} times, expected 1 — file already changed?")
    return hay.index(needle)


def replace_between(text, start, end, new, what):
    i = must(text, start, what + " (start)")
    j = text.index(end, i)
    j += len(end)
    return text[:i] + new + text[j:]


# ───────────────────────────────────────────────────────────── 1 · CSS
CSS_ANCHOR = (".hsteps p{font-size:var(--t-cap);line-height:1.55;color:var(--ink-2);margin:0}\n")
CSS_NEW = CSS_ANCHOR + """/* Two flows, one panel (24 Nov 2026). The client sent both routes a donor can
   take — ticking the receipt box while giving, or claiming it afterwards — and
   the tooltip only taught the second. Two headed sections, still ONE dialog: no
   tabs and no second popover, because Option 1 must be read first and the panel
   already scrolls inside its own max-height.

   The heading is the 13px --t-cap step in bold navy; the step labels under it
   stay 12px uppercase letterspaced muted (--t-eyebrow). Two roles, no new size,
   colour, face or shadow. The hairline is the same --line the panel border
   uses, so the sections separate without a card. */
.hsec{margin:var(--s4) 0 0;padding-top:var(--s3);border-top:1px solid var(--line)}
.hsec-h{margin:0;font-size:var(--t-cap);line-height:1.5;font-weight:700;color:var(--navy)}
.hsec-sub{margin:6px 0 0;font-size:var(--t-cap);line-height:1.55;color:var(--muted)}
.houtro{margin:var(--s4) 0 0;font-size:var(--t-cap);line-height:1.55;color:var(--muted)}
"""
src = src.replace(CSS_ANCHOR, CSS_NEW, 1)

# The crops are 320px wide now (they were 400px), and they fill the column: a
# 320px figure inside a 420px panel left a 68px empty band on the desktop, which
# reads as a mistake rather than a measure. The 320 source is itself a downscale
# of a phone capture, so filling 388px is still under the original resolution.
IMG_OLD = ".hsteps img{width:100%;max-width:400px;height:auto;"
IMG_NEW = ".hsteps img{width:100%;height:auto;"
if src.count(IMG_OLD) != 1:
    raise SystemExit("the .hsteps img rule moved — read it before editing")
src = src.replace(IMG_OLD, IMG_NEW, 1)

# ───────────────────────────────────────────────────────────── 2 · the comment above the panel
CMT_START = "      <!-- Phase 1: the receipt route for an AlipayHK gift."
CMT_END = "Chinese, which is why the outro says so for an English reader. -->\n"
CMT_NEW = """      <!-- Phase 1: the receipt route for an AlipayHK gift. AlipayHK issues the
           receipt inside its own app, so the rail carries the instruction plus
           six crops that walk a donor through BOTH routes Denise sent (24 Nov):
           ticking 「需要收據」 while giving (two steps, led first — it is the
           easier path), or claiming afterwards from the donation records (four
           steps). The copy deliberately stops short of promising an issued
           receipt: it names where to apply.

           The crops are the client's own donor-side screens at 320x529 (67 KB
           for all six). AlipayHK's UI is Chinese, which is why the app labels
           stay in Chinese inside the English sentences — a donor matches what
           they see — and why the outro says the interface is Chinese. -->
"""
src = replace_between(src, CMT_START, CMT_END, CMT_NEW, "panel comment")

# ───────────────────────────────────────────────────────────── 3 · the panel itself
PANEL_START = '        <div class="helppop" id="alipay-help-panel" role="dialog"'
PANEL_END = ("          <p data-i18n=\"s3.rcpt.outro\">The AlipayHK app is shown in Chinese; "
             "the buttons sit in the same place on your screen.</p>\n        </div>\n")


def step(base, label_en, img, eager, alt, text):
    """One <li>. `base` is the step-text key, e.g. s3.rcpt.o1.s2 — the label key
    is base+"t" and the alt key is the option prefix + ".alt" + the same number."""
    prefix, n = base.rsplit(".", 1)          # "s3.rcpt.o1" , "s2"
    load = 'loading="eager"' if eager else 'loading="lazy"'
    return f"""              <li>
                <span class="n" data-i18n="{base}t">{label_en}</span>
                <img {load} src="../assets/help/{img}" width="320" height="529"
                     alt="{alt}" data-i18n-alt="{prefix}.alt{n[1:]}">
                <p data-i18n="{base}">{text}</p>
              </li>
"""


PANEL_NEW = f"""        <div class="helppop" id="alipay-help-panel" role="dialog"
             aria-labelledby="alipay-help-title" hidden>
          <button type="button" class="hclose" data-help-close
                  aria-label="Close" data-i18n-aria="s3.rcpt.close">&#10005;</button>
          <h3 id="alipay-help-title" data-i18n="s3.rcpt.title">Getting a receipt from AlipayHK</h3>
          <p data-i18n="s3.rcpt.intro">Two ways. The first is easiest: tick the box while you give.</p>

          <div class="hsec" data-opt="1" role="group" aria-labelledby="alipay-o1-h">
            <h4 class="hsec-h" id="alipay-o1-h" data-i18n="s3.rcpt.o1head">Option 1 — when you donate</h4>
            <p class="hsec-sub" data-i18n="s3.rcpt.o1sub">Request a donation receipt and enter your personal details when donating.</p>
            <ol class="hsteps">
{step("s3.rcpt.o1.s1", "Step 1", "alipay-receipt-o1-step-1.webp", True,
      "AlipayHK donation detail screen: the charity, the suggested amounts and, at the foot, the unticked 「需要收據」 box",
      "Tick 「需要收據」 (need a receipt) under the amount.")}
{step("s3.rcpt.o1.s2", "Step 2", "alipay-receipt-o1-step-2.webp", False,
      "The same screen with 「需要收據」 ticked and the 「捐款人資料」 form open below it: name in English, email, phone and address",
      "The donor form appears — name in English, email, phone. Fill it in, then confirm the gift.")}
            </ol>
          </div>

          <div class="hsec" data-opt="2" role="group" aria-labelledby="alipay-o2-h">
            <h4 class="hsec-h" id="alipay-o2-h" data-i18n="s3.rcpt.o2head">Option 2 — after you give</h4>
            <p class="hsec-sub" data-i18n="s3.rcpt.o2sub">If you forgot to tick the box, you can still claim it from your donation records.</p>
            <ol class="hsteps">
{step("s3.rcpt.o2.s1", "Step 1", "alipay-receipt-o2-step-1.webp", False,
      "AlipayHK home screen with 慈善捐款 in the shortcut grid, fourth in the first row",
      "Open AlipayHK and go to 慈善捐款.")}
{step("s3.rcpt.o2.s2", "Step 2", "alipay-receipt-o2-step-2.webp", False,
      "The 慈善捐款 page with its menu of donation options, including the 捐款記錄 row",
      "Tap 我的捐款 at the bottom, then 捐款記錄.")}
{step("s3.rcpt.o2.s3", "Step 3", "alipay-receipt-o2-step-3.webp", False,
      "The 交易記錄 list showing one gift to 護瞳行動 with its date and amount",
      "Find the gift: the charity, the date and the amount identify it.")}
{step("s3.rcpt.o2.s4", "Step 4", "alipay-receipt-o2-step-4.webp", False,
      "The 捐款結果 screen with the blue 申請收據 button at the foot, above the return link",
      "Tap 申請收據 and submit your details.")}
            </ol>
          </div>

          <p class="houtro" data-i18n="s3.rcpt.outro">The app is shown in Chinese; the buttons sit in the same place on your screen.</p>
        </div>
"""
src = replace_between(src, PANEL_START, PANEL_END, PANEL_NEW, "the help panel")

# ───────────────────────────────────────────────────────────── 4 · the Chinese string table
ZH_NEW = """      "s3.rcpt.title": "在 AlipayHK 索取捐款收據",
      "s3.rcpt.intro": "兩種方法。最簡單是第一種：捐款時直接勾選。",
      "s3.rcpt.o1head": "方法一：捐款時",
      "s3.rcpt.o1sub": "捐款時直接選擇需要捐款收據並填寫您的個人資料。",
      "s3.rcpt.o1.s1t": "第 1 步",
      "s3.rcpt.o1.s1": "在金額下方勾選「需要收據」。",
      "s3.rcpt.o1.s2t": "第 2 步",
      "s3.rcpt.o1.s2": "畫面展開「捐款人資料」：英文姓名、電郵、電話。填妥後確認捐款。",
      "s3.rcpt.o1.alt1": "AlipayHK 捐款詳情畫面：受惠機構護瞳行動、建議捐款金額，以及畫面底部尚未勾選的「需要收據」方格",
      "s3.rcpt.o1.alt2": "同一畫面已勾選「需要收據」，下方展開「捐款人資料」表格：英文姓名、電郵、電話及郵寄地址",
      "s3.rcpt.o2head": "方法二：捐款後補領",
      "s3.rcpt.o2sub": "如捐款時忘記勾選，仍可在捐款記錄中補領。",
      "s3.rcpt.o2.s1t": "第 1 步",
      "s3.rcpt.o2.s1": "開啟 AlipayHK，進入「慈善捐款」。",
      "s3.rcpt.o2.s2t": "第 2 步",
      "s3.rcpt.o2.s2": "點按底部「我的捐款」，再點按「捐款記錄」。",
      "s3.rcpt.o2.s3t": "第 3 步",
      "s3.rcpt.o2.s3": "找到該筆捐款：受惠機構、日期與金額足以辨認。",
      "s3.rcpt.o2.s4t": "第 4 步",
      "s3.rcpt.o2.s4": "點按「申請收據」，填寫個人資料並提交。",
      "s3.rcpt.o2.alt1": "AlipayHK 首頁，捷徑列第一行第四個為「慈善捐款」圖示",
      "s3.rcpt.o2.alt2": "「慈善捐款」頁面及其捐款選項清單，當中包括「捐款記錄」一列",
      "s3.rcpt.o2.alt3": "「交易記錄」清單顯示一筆護瞳行動的捐款，附日期與金額",
      "s3.rcpt.o2.alt4": "「捐款結果」畫面，底部為藍色的「申請收據」按鈕，下方有返回機構頁的連結",
      "s3.rcpt.outro": "截圖為 AlipayHK 的中文介面；您手機上的按鈕位置相同。",
      "s3.rcpt.close": "關閉",
"""
zh_start = '      "s3.rcpt.title": "在 AlipayHK 內申請收據",'
zh_end = '      "s3.rcpt.alt5": "捐款結果頁底部的藍色「申請收據」按鈕",\n'
src = replace_between(src, zh_start, zh_end, ZH_NEW, "the zh string table")

EN_NEW = """      "s3.rcpt.title": "Getting a receipt from AlipayHK",
      "s3.rcpt.intro": "Two ways. The first is easiest: tick the box while you give.",
      "s3.rcpt.o1head": "Option 1 — when you donate",
      "s3.rcpt.o1sub": "Request a donation receipt and enter your personal details when donating.",
      "s3.rcpt.o1.s1t": "Step 1",
      "s3.rcpt.o1.s1": "Tick 「需要收據」 (need a receipt) under the amount.",
      "s3.rcpt.o1.s2t": "Step 2",
      "s3.rcpt.o1.s2": "The donor form appears — name in English, email, phone. Fill it in, then confirm the gift.",
      "s3.rcpt.o1.alt1": "AlipayHK donation detail screen: the charity, the suggested amounts and, at the foot, the unticked 「需要收據」 box",
      "s3.rcpt.o1.alt2": "The same screen with 「需要收據」 ticked and the 「捐款人資料」 form open below it: name in English, email, phone and address",
      "s3.rcpt.o2head": "Option 2 — after you give",
      "s3.rcpt.o2sub": "If you forgot to tick the box, you can still claim it from your donation records.",
      "s3.rcpt.o2.s1t": "Step 1",
      "s3.rcpt.o2.s1": "Open AlipayHK and go to 慈善捐款.",
      "s3.rcpt.o2.s2t": "Step 2",
      "s3.rcpt.o2.s2": "Tap 我的捐款 at the bottom, then 捐款記錄.",
      "s3.rcpt.o2.s3t": "Step 3",
      "s3.rcpt.o2.s3": "Find the gift: the charity, the date and the amount identify it.",
      "s3.rcpt.o2.s4t": "Step 4",
      "s3.rcpt.o2.s4": "Tap 申請收據 and submit your details.",
      "s3.rcpt.o2.alt1": "AlipayHK home screen with 慈善捐款 in the shortcut grid, fourth in the first row",
      "s3.rcpt.o2.alt2": "The 慈善捐款 page with its menu of donation options, including the 捐款記錄 row",
      "s3.rcpt.o2.alt3": "The 交易記錄 list showing one gift to 護瞳行動 with its date and amount",
      "s3.rcpt.o2.alt4": "The 捐款結果 screen with the blue 申請收據 button at the foot, above the return link",
      "s3.rcpt.outro": "The app is shown in Chinese; the buttons sit in the same place on your screen.",
      "s3.rcpt.close": "Close",
"""
en_start = '      "s3.rcpt.title": "Applying for a receipt in AlipayHK",'
en_end = '      "s3.rcpt.alt5": "The blue Apply for receipt button at the foot of the donation result",\n'
src = replace_between(src, en_start, en_end, EN_NEW, "the en string table")

# ───────────────────────────────────────────────────────────── 5 · warm the lazy crops on open
OPEN_OLD = """    function helpOpen(on){
      pop.hidden = !on;
      btn.setAttribute("aria-expanded", on ? "true" : "false");
      scheduleHeight();
    }
"""
OPEN_NEW = """    /* A lazy image inside a hidden panel starts its request at open time, so the
       first paint can be an empty box — it reads as a missing asset. Four of the
       six crops are lazy on purpose (a donor who never opens the panel never pays
       for them), so start their fetches the moment the panel is revealed. */
    var warmed = false;
    function warmCrops(){
      if (warmed) return;
      warmed = true;
      $$("img[loading=lazy]", pop).forEach(function (im) {
        var preload = new Image(); preload.src = im.getAttribute("src");
      });
    }
    function helpOpen(on){
      pop.hidden = !on;
      btn.setAttribute("aria-expanded", on ? "true" : "false");
      if (on) warmCrops();
      scheduleHeight();
    }
"""
src = src.replace(OPEN_OLD, OPEN_NEW, 1)
if OPEN_NEW not in src:
    raise SystemExit("the helpOpen body moved — read the popover block before editing")

# ── the markup's own defaults must be the English copy, character for character.
# Two copies of one sentence ship otherwise, and only the table's is ever reviewed.
markup = src.split("<script>")[0]
tbl = src[src.index('"s3.rcpt.title": "Getting'):]
tbl = tbl[:tbl.index('"s3.rcpt.close"')]
TABLE = dict(re.findall(r'"(s3\.rcpt\.[a-z0-9.]+)": "((?:[^"\\]|\\.)*)"', tbl))
seen = {}
for key, val in re.findall(r'data-i18n="(s3\.rcpt\.[a-z0-9.]+)"[^>]*>([^<]*)<', markup):
    seen[key] = val
for val, key in re.findall(r'alt="([^"]*)" data-i18n-alt="(s3\.rcpt\.[a-z0-9.]+)"', markup):
    seen[key] = val
drift = [(k, seen.get(k), TABLE.get(k)) for k in sorted(set(seen) | set(TABLE))
         if seen.get(k) != TABLE.get(k)]
if drift:
    raise SystemExit("markup defaults and the English table disagree:\n" +
                     "\n".join(f"  {k}: {a!r} vs {b!r}" for k, a, b in drift))
print(f"  {len(seen)} panel strings: markup default == English table")

if src == orig:
    raise SystemExit("nothing changed")

HTML.write_bytes(src.encode("utf-8"))

# ───────────────────────────────────────────────────────────── 6 · checks that can actually fail
# A string-table edit is a JS edit: a missing comma kills the whole IIFE and every
# page silently falls back to the markup defaults.
script = re.search(r"<script>(.*)</script>", src, re.S).group(1)
tmp = ROOT / "qa" / "_alipay_two_options_check.js"
tmp.write_text(script, encoding="utf-8")
r = subprocess.run(["node", "--check", str(tmp)], capture_output=True, text=True)
tmp.unlink()
if r.returncode:
    raise SystemExit("node --check failed — the string table is broken:\n" + r.stderr)

for f in ("alipay-receipt-o1-step-1.webp", "alipay-receipt-o1-step-2.webp",
          "alipay-receipt-o2-step-1.webp", "alipay-receipt-o2-step-2.webp",
          "alipay-receipt-o2-step-3.webp", "alipay-receipt-o2-step-4.webp"):
    if not (ASSETS / f).exists():
        raise SystemExit(f"missing asset: {f}")
if "alipay-receipt-step-" in src:
    raise SystemExit("a superseded crop is still referenced")

print("embed/index.html rebuilt: two options, six crops, strings replaced")
print(f"  bytes {len(orig)} -> {len(src)}")
