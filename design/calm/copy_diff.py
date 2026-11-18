#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Diff the old copy tables (embed/index.html, untouched) against the new ones."""
import json, re

def esc(s):
    if s is None:
        return "—"
    return str(s).replace("\n", " ").replace("|", "\\|")

OLD = "index.pre-build.html"
ENGINE_RE = re.compile(r"var I18N = (\{.*?\n  \});", re.S)
raw = ENGINE_RE.search(open(OLD, encoding="utf-8").read()).group(1)
old = json.loads(raw)
new = json.load(open("_new_i18n.json", encoding="utf-8"))

out = ["# Copy changes — one line per string, both languages\n",
       "Source of the \"old\" column: `embed/index.html` (the delivered build, unmodified).",
       "Every key below changed in **both** tables. Keys are listed in the order they appear in the build.\n"]

changed = added = removed = 0
for key in new["en"]:
    o_en = old["en"].get(key); o_zh = old["zh-HK"].get(key)
    n_en = new["en"][key];  n_zh = new["zh-HK"][key]
    if o_en is None:
        added += 1
        out.append(f"### `{key}` — **new in both tables**\n")
    elif o_en == n_en and o_zh == n_zh:
        continue
    else:
        changed += 1
        out.append(f"### `{key}`\n")
    out.append("| | before | after |\n|---|---|---|\n"
               "| en | " + esc(o_en) + " | " + esc(n_en) + " |\n"
               "| zh-HK | " + esc(o_zh) + " | " + esc(n_zh) + " |\n")

for key in old["en"]:
    if key not in new["en"]:
        removed += 1
        out.append(f"### `{key}` — **removed (both tables)**\n"
                   f"| | before | after |\n|---|---|---|\n"
                   "| en | " + esc(old["en"][key]) + " | — |\n"
                   "| zh-HK | " + esc(old["zh-HK"][key]) + " | — |\n")

head = (f"**{changed} keys rewritten in both tables · {added} added · {removed} removed.** "
        f"Old table {len(old['en'])} keys, new table {len(new['en'])} keys.\n\n")
out.insert(3, head)
open("COPY-CHANGES.md", "w", encoding="utf-8").write("\n".join(out))
print(f"changed {changed}, added {added}, removed {removed}; old {len(old['en'])} keys, new {len(new['en'])}")
for k in old["en"]:
    if k not in new["en"]:
        print("removed:", k)
