#!/usr/bin/env python3
"""Render docs/*.md into a styled, self-contained HTML page under the POC.

usage: build-doc.py <source.md> <out.html> "<Title>"
Keeps one canonical source: the markdown in docs/.
"""
import sys, re, html
import markdown

SRC, OUT, TITLE = sys.argv[1], sys.argv[2], sys.argv[3]
body = markdown.markdown(open(SRC, encoding="utf-8").read(),
                         extensions=["tables", "fenced_code", "toc", "sane_lists", "attr_list"])

# clickable block URLs inside <code> stay code; nothing to do
TPL = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>{title}</title>
<link rel="icon" href="data:,">
<style>
:root{{--bg:#f4f5f7;--panel:#fff;--line:#e2e5ea;--ink:#1c2128;--muted:#68707b;--accent:#e97824;--navy:#01014E;
  --sans:system-ui,-apple-system,"Segoe UI",Helvetica,Arial,sans-serif;--mono:ui-monospace,SFMono-Regular,Menlo,monospace}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);font-family:var(--sans);line-height:1.65;font-size:15px}}
.doc{{max-width:860px;margin:0 auto;padding:34px 22px 90px}}
h1{{font-size:clamp(1.5rem,3vw,2rem);letter-spacing:-.02em;line-height:1.2;margin:0 0 8px}}
h2{{font-size:1.12rem;margin:38px 0 10px;padding-top:16px;border-top:1px solid var(--line);letter-spacing:-.01em}}
h3{{font-size:.98rem;margin:22px 0 8px}}
p,li{{color:#2c333c}}
ul,ol{{padding-left:22px}}
li{{margin-bottom:5px}}
code{{font-family:var(--mono);font-size:.86em;background:#eef0f3;border:1px solid var(--line);border-radius:4px;padding:1px 5px}}
pre{{background:#0f1b2d;color:#d8e6f5;padding:14px 16px;border-radius:8px;overflow:auto;font-size:12.5px;line-height:1.55}}
pre code{{background:none;border:0;color:inherit;padding:0;font-size:inherit}}
table{{width:100%;border-collapse:collapse;font-size:13.5px;background:var(--panel);border:1px solid var(--line);
  border-radius:8px;overflow:hidden;margin:14px 0}}
th,td{{text-align:left;padding:8px 12px;border-bottom:1px solid var(--line);vertical-align:top}}
th{{font-size:11px;letter-spacing:.05em;text-transform:uppercase;color:var(--muted);font-weight:600;background:#fafbfc}}
tr:last-child td{{border-bottom:0}}
blockquote{{margin:14px 0;padding:12px 16px;background:#fff8f1;border:1px solid #f0dcc4;border-radius:8px;color:#7a4f1f}}
blockquote p{{margin:0;color:inherit}}
hr{{border:0;border-top:1px solid var(--line);margin:30px 0}}
strong{{color:#12161b}}
a{{color:var(--navy);text-underline-offset:3px}}
.tag{{display:inline-block;font:600 10.5px/1 var(--mono);letter-spacing:.08em;text-transform:uppercase;color:var(--accent);margin-bottom:10px}}
@media print{{body{{background:#fff}}.doc{{max-width:none;padding:0}}h2{{page-break-after:avoid}}table,pre{{page-break-inside:avoid}}}}
</style>
</head>
<body><div class="doc">
<div class="tag">2SK · implementation guide</div>
{body}
</div></body></html>"""

open(OUT, "w", encoding="utf-8").write(TPL.format(title=html.escape(TITLE), body=body))
print("wrote", OUT, len(body), "chars of body")
