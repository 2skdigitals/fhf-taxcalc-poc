#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Splice the calm redesign into index.html without touching the tax engine.

Always starts from ../../embed/index.html, so the build is idempotent.

Guards:
  · the FHF_TAX_ENGINE_START..END block is extracted before and after and compared
  · the wiring <script> (everything after the engine) is replaced only for the
    I18N table; all other JS is copied through untouched
"""
import json, re, sys, hashlib

SRC = "index.html"
ORIG_SRC = "../../embed/index.html"   # always rebuild from the pristine original
ENGINE_RE = re.compile(r"(/\* FHF_TAX_ENGINE_START \*/.*?/\* FHF_TAX_ENGINE_END \*/)", re.S)
I18N_RE = re.compile(r"\n  var I18N = \{\n.*?\n  \};\n", re.S)

html = open(ORIG_SRC, encoding="utf-8").read()
style = open("_new_style.css", encoding="utf-8").read()
body = open("_new_body.html", encoding="utf-8").read()
i18n = json.load(open("_new_i18n.json", encoding="utf-8"))

engine_before = ENGINE_RE.search(html).group(1)
h_before = hashlib.sha256(engine_before.encode()).hexdigest()

# 1 · stylesheet
html = re.sub(r"<style>\n.*?\n</style>", lambda m: "<style>\n" + style.rstrip() + "\n</style>",
              html, count=1, flags=re.S)

# 2 · body: from <div class="wrap" id="root"> to the closing </div> before <script>
start = html.index('<div class="wrap" id="root">')
end = html.index('<script>')
html = html[:start] + body.rstrip() + "\n\n" + html[end:]

# 3 · the two copy tables
dump = json.dumps(i18n, ensure_ascii=False, indent=2)
# indent the object body to sit inside the IIFE at 2 spaces
lines = dump.split("\n")
indented = "\n".join(("  " + lines[0]) if i == 0 else ("  " + l if l else l) for i, l in enumerate(lines))
new_i18n = "\n  var I18N = " + indented.strip() + ";\n"
html = I18N_RE.sub(lambda m: new_i18n, html, count=1)

engine_after = ENGINE_RE.search(html).group(1)
h_after = hashlib.sha256(engine_after.encode()).hexdigest()
assert h_before == h_after, "TAX ENGINE CHANGED — aborting"

open(SRC, "w", encoding="utf-8").write(html)
print("engine sha256 before/after:", h_before[:16], h_after[:16], "OK")
print("bytes:", len(html.encode()))
