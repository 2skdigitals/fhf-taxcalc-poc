#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Design review pass — vertical rhythm, alignment, type scale. 23 Nov 2026.

Kevin: "the page works but it does not yet read as a designed document."
This pass is correction, not restyle: no new colour, no new face, no shadow,
no gradient, no decoration, no copy change. Every number below was measured in
the browser first (see docs/DESIGN-REVIEW-20261123.md).

Three classes of change:

  1 · ONE INVERSION. The "2 · your assessable income" heading sat 0px under the
      card above it and 16px above its own card — the only place in the document
      where a heading was closer to the previous block than to its content.
  2 · ONE SCALE. Block gaps were 0/2/6/8/10/12/14/16/18/20/22/26/36 — fourteen
      values, no ratio. They collapse onto a 4px scale (8/12/16/20/24) with one
      block-to-block step (36 desktop / 32 phone) that is now always larger than
      any gap inside a block, including at 390px where 26 == 26.
  3 · TWO MEASURES. `--measure` was a fixed 34rem, so the 13px notes ran to 103ch
      while the 17px lede ran to 64ch. Measured in `em`, the token resolves to
      68ch at every size. And the consent line, which alone had no measure,
      ran the full 832px (≈128ch).

Every replacement asserts its old string occurs EXACTLY once.

    /Library/Developer/CommandLineTools/usr/bin/python3 qa/apply_design_review_20261123.py
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
        sys.exit(f"ABORT  {label}: expected {want} occurrence(s), found {n}\n---\n{old[:240]}")
    src = src.replace(old, new)
    rows.append((label, n))


# ── 1 · tokens: one 4px scale + a measure that follows the type size ─────────
sub("root · spacing scale + em measure",
    '  --gut:clamp(18px,4.6vw,32px);\n'
    '  --measure:34rem;\n',
    '  --gut:clamp(18px,4.6vw,32px);\n'
    '  /* One 4px scale for the gaps BETWEEN blocks. Measured on 23 Nov: the\n'
    '     document used 0/2/6/8/10/12/14/16/18/20/22/26/36 — fourteen values and\n'
    '     no ratio, which is what made the rhythm read as assembled. Optical\n'
    '     values inside one surface (a caption under its figure) stay as they are. */\n'
    '  --s2:8px; --s3:12px; --s4:16px; --s5:20px; --s6:24px; --s7:32px;\n'
    '  /* 34em, not 34rem: the var is substituted where it is used, so the measure\n'
    '     resolves against each element\'s own size — 68ch at 17px and at 13px alike.\n'
    '     As a fixed 544px it gave the 17px lede 64ch and the 13px note 103ch. */\n'
    '  --measure:34em;\n')


# ── 2 · block rhythm ────────────────────────────────────────────────────────
sub("rhythm · the section step is always a step above any internal gap",
    'section.panel + section.panel{margin-top:clamp(26px,4.4vw,36px)}',
    '/* 32px at the narrow end, where 26px used to equal the 26px inside the FAQ\n'
    '   cluster — the section boundary was not distinguishable from a sub-gap. */\n'
    'section.panel + section.panel{margin-top:clamp(32px,4.4vw,36px)}')

sub("rhythm · a card followed by a new heading gets a top margin (was 0)",
    '.step{display:flex;align-items:center;gap:11px;margin:0 0 16px}',
    '.step{display:flex;align-items:center;gap:11px;margin:0 0 16px}\n'
    '/* A heading must sit closer to its own block than to the one above it. The\n'
    '   calculator\'s second heading followed a card at 0px and its own card at\n'
    '   16px — the one inversion in the document, and the reason block 2 read as\n'
    '   a caption on block 1. 24px above, 16px below. */\n'
    '.card + .step{margin-top:var(--s6)}')

sub("rhythm · lede 10 → 12", '.lede{font-size:var(--t-body);line-height:1.5;color:var(--ink-2);margin:10px 0 0;max-width:var(--measure)}',
    '.lede{font-size:var(--t-body);line-height:1.5;color:var(--ink-2);margin:var(--s3) 0 0;max-width:var(--measure)}')

sub("rhythm · fine print 14 → 16", '.fine{font-size:var(--t-cap);line-height:1.55;color:var(--muted);margin:14px 0 0;max-width:var(--measure)}',
    '.fine{font-size:var(--t-cap);line-height:1.55;color:var(--muted);margin:var(--s4) 0 0;max-width:var(--measure)}\n'
    '/* The legal line closes the document, so it stands off the last block by more\n'
    '   than the 8px that separates a paragraph from its own caption. At 14px it\n'
    '   read as the last line of the receipt form. */\n'
    '.wrap > p.fine{margin-top:var(--s6)}')

sub("rhythm · hint 8 → var", '.hint{font-size:var(--t-cap);line-height:1.55;color:var(--muted);margin:8px 0 0;max-width:var(--measure)}',
    '.hint{font-size:var(--t-cap);line-height:1.55;color:var(--muted);margin:var(--s2) 0 0;max-width:var(--measure)}')

sub("rhythm · note 12 → var", '.note{font-size:var(--t-cap);line-height:1.6;color:var(--muted);margin:12px 0 0;max-width:var(--measure)}',
    '.note{font-size:var(--t-cap);line-height:1.6;color:var(--muted);margin:var(--s3) 0 0;max-width:var(--measure)}')

sub("rhythm · card + card 14 → 16", '.card + .card{margin-top:14px}', '.card + .card{margin-top:var(--s4)}')
sub("rhythm · field 20 → var", '.field{margin-top:20px}', '.field{margin-top:var(--s5)}')
sub("rhythm · quick 12 → var", '.quick{display:flex;flex-wrap:wrap;align-items:center;gap:8px;margin:12px 0 0}',
    '.quick{display:flex;flex-wrap:wrap;align-items:center;gap:8px;margin:var(--s3) 0 0}')
sub("rhythm · gotoline 20 → var", '.gotoline{display:flex;align-items:center;gap:16px;flex-wrap:wrap;margin-top:20px}',
    '.gotoline{display:flex;align-items:center;gap:16px;flex-wrap:wrap;margin-top:var(--s5)}')
sub("rhythm · bands 14 → 16", '.bands{display:grid;margin-top:14px;border-top:1px solid var(--line)}',
    '.bands{display:grid;margin-top:var(--s4);border-top:1px solid var(--line)}')
sub("rhythm · band select 14 → 16", '.band-select{display:none;margin-top:14px}', '.band-select{display:none;margin-top:var(--s4)}')
sub("rhythm · disclosure inside a card 10 → 12", 'details.q.inset{margin-top:10px;padding-top:2px}',
    'details.q.inset{margin-top:var(--s3);padding-top:2px}')
sub("rhythm · disclosure 16 → var", 'details.q{margin-top:16px;border-top:1px solid var(--line)}',
    'details.q{margin-top:var(--s4);border-top:1px solid var(--line)}')
sub("rhythm · faq cluster 26 → 24", '.faq{margin-top:26px;padding-top:16px;border-top:1px solid var(--line-2)}',
    '.faq{margin-top:var(--s6);padding-top:var(--s4);border-top:1px solid var(--line-2)}')
sub("rhythm · global disclosure 16/10 → 16/12", '.disc-global{border-top:1px solid var(--line);margin-top:16px;padding-top:10px}',
    '.disc-global{border-top:1px solid var(--line);margin-top:var(--s4);padding-top:var(--s3)}')
sub("rhythm · ledger 22 → 24 inside the result panel", '.result .hint{color:var(--on-navy-2);margin:10px 0 0;font-size:var(--t-cap);line-height:1.5}',
    '.result .hint{color:var(--on-navy-2);margin:var(--s3) 0 0;font-size:var(--t-cap);line-height:1.5;max-width:none}\n'
    '/* The monthly caption is ONE sentence of 75 characters (see #net-caption). At\n'
    '   13px that is 79ch on a single line; pushed into the 68ch measure it breaks\n'
    '   into two lines of ~37ch — shorter than the 45ch floor, so the fix trades one\n'
    '   defect for another and costs 19px of the block\'s declared height. It keeps\n'
    '   the panel measure instead, and the sentence is flagged for a copy trim. */')
sub("rhythm · figs 22 → 24", '.figs{\n  display:grid;grid-template-columns:1fr;\n  margin:22px 0 0;border-top:1px solid var(--hair-inv);\n}',
    '.figs{\n  display:grid;grid-template-columns:1fr;\n  margin:var(--s6) 0 0;border-top:1px solid var(--hair-inv);\n}')
sub("rhythm · assumption rule 22/14 → 24/16", '#assumption{margin-top:22px;padding-top:14px;border-top:1px solid var(--line)}',
    '#assumption{margin-top:var(--s6);padding-top:var(--s4);border-top:1px solid var(--line)}')
sub("rhythm · scope 14 → 16", '.scope{font-size:var(--t-cap);line-height:1.55;color:var(--ink-2);margin:14px 0 0;max-width:var(--measure)}',
    '.scope{font-size:var(--t-cap);line-height:1.55;color:var(--ink-2);margin:var(--s4) 0 0;max-width:var(--measure)}')
sub("rhythm · rails 18 → 20", '.rails{display:grid;border-top:var(--rule);margin-top:18px}',
    '.rails{display:grid;border-top:var(--rule);margin-top:var(--s5)}')
sub("rhythm · paygrid 18/26 → 20/24", '           border-top:var(--rule);margin-top:18px;padding-top:26px;align-items:start}',
    '           border-top:var(--rule);margin-top:var(--s5);padding-top:var(--s6);align-items:start}')
sub("rhythm · receipt form gap 18 → 20", '.rform{display:grid;gap:18px;margin-top:18px}', '.rform{display:grid;gap:var(--s5);margin-top:var(--s5)}')
sub("rhythm · the form's own gap governs its rows (child margins were doubling it)",
    '.rrow{display:grid;gap:18px}',
    '.rrow{display:grid;gap:var(--s5)}\n'
    '/* Inside a grid the gap and a child margin ADD: the disclaimer caveat sat 36px\n'
    '   from the consent while every other form row sat 20px, and the closing hint\n'
    '   28px under the button. One gap, no per-child margins. */\n'
    '.rform > *{margin-top:0}')
sub("rhythm · alt 16 → var", '.alt{margin:16px 0 0;font-size:var(--t-sm)}', '.alt{margin:var(--s4) 0 0;font-size:var(--t-sm)}')
sub("rhythm · min-note 16 → var", '.min-note{\n  margin:16px 0 0;padding:14px 16px;border:1px solid var(--line-2);',
    '.min-note{\n  margin:var(--s4) 0 0;padding:var(--s4) 16px;border:1px solid var(--line-2);')


# ── 3 · type scale ──────────────────────────────────────────────────────────
sub("type · the income band label back on the 13px token",
    '  font-size:.8125rem;color:var(--ink-2);cursor:pointer;white-space:nowrap;',
    '  font-size:var(--t-cap);color:var(--ink-2);cursor:pointer;white-space:nowrap;')
sub("type · the band rate was 11px, under the 12px floor the rest of the system uses",
    '  font-size:.6875rem;color:var(--muted);font-weight:400;',
    '  font-size:var(--t-eyebrow);color:var(--muted);font-weight:400;')
sub("type · the consent line had no measure and ran the full 832px column",
    '.rform .consent{\n  display:grid;grid-template-columns:20px minmax(0,1fr);gap:12px;align-items:start;\n'
    '  min-height:44px;padding:6px 0;cursor:pointer;\n'
    '  font-size:var(--t-cap);line-height:1.55;color:var(--ink-2);font-weight:400;\n}',
    '.rform .consent{\n  display:grid;grid-template-columns:20px minmax(0,1fr);gap:12px;align-items:start;\n'
    '  min-height:44px;padding:6px 0;cursor:pointer;max-width:var(--measure);\n'
    '  font-size:var(--t-cap);line-height:1.55;color:var(--ink-2);font-weight:400;\n}')

# ── 4 · a hover state that pointed at a colour that does not exist ──────────
sub("css · .swap:hover referenced --orange-ink, which is defined nowhere",
    '.swap:hover{color:var(--orange-ink)}',
    '/* was color:var(--orange-ink) — an undefined var, so the declaration was\n'
    '   invalid at computed-value time and the button had no hover state at all.\n'
    '   Orange on white is 3.6:1 at 15px, so the cue is weight, not colour. */\n'
    '.swap:hover{text-decoration-thickness:2px}')

SRC.write_text(src, encoding="utf-8")
print(f"{len(rows)} edits applied to {SRC}")
for label, n in rows:
    print(f"  ok  {label}")
