#!/usr/bin/env bash
# Publish the widget at two individual github.io paths, with no repo-name layer.
#
#   https://2skdigitals.github.io/zh/     Chinese (part=all)
#   https://2skdigitals.github.io/en/     English  (part=all)
#
# Why: a *project* page always lives at /<repo>/, so the campaign repo's name
# ("fhf-taxcalc-poc") was permanently in the URL. The only way to drop that layer
# is the *user* site repo — 2skdigitals.github.io — whose root IS the domain, so
# any directory under it is a first-class path.
#
# One source file, two generated copies: /en/index.html is embed/index.html with
# a single line changed (the language default), produced on every publish, so the
# two paths can never drift apart. Both live at depth 1, so the widget's own
# "../assets/…" references resolve to /assets/ unchanged.
#
# Usage:
#   bash ops/publish-sitelinks.sh --dry-run   # build the tree, list it, push nothing
#   bash ops/publish-sitelinks.sh             # build + push to the user-site repo
set -euo pipefail

REPO=2skdigitals/2skdigitals.github.io
REMOTE="https://github.com/${REPO}.git"
DRY=0
[[ "${1:-}" == "--dry-run" ]] && DRY=1

cd "$(git rev-parse --show-toplevel)"
[[ -z "$(git status --porcelain --untracked-files=no)" ]] || {
  echo "working tree is dirty — commit first (published bytes must match a commit)" >&2; exit 1; }

SRC=embed/index.html
OUT=$(mktemp -d)
trap 'rm -rf "$OUT"' EXIT

# zh — the file as-is (no ?lang= means zh-HK)
mkdir -p "$OUT/zh"
cp "$SRC" "$OUT/zh/index.html"

# en — same file, language default flipped; ?lang= still wins if a host passes it
mkdir -p "$OUT/en"
python3 - "$SRC" "$OUT/en/index.html" <<'PY'
import sys
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding="utf-8").read()
old = '    lang: normLang(qs.get("lang")),'
new = '    lang: qs.get("lang") ? normLang(qs.get("lang")) : "en",   /* /en/ default */'
assert s.count(old) == 1, f"anchor found {s.count(old)} times"
open(dst, "w", encoding="utf-8").write(s.replace(old, new))
PY

# only the assets the widget asks for
ASSETS=()
while IFS= read -r a; do ASSETS+=("$a"); done \
  < <(grep -oE 'assets/[A-Za-z0-9_./-]+' "$SRC" | sort -u)
while IFS= read -r a; do
  mkdir -p "$OUT/$(dirname "$a")"; cp "$a" "$OUT/$a"
done < <(printf '%s\n' "${ASSETS[@]}")
cp .nojekyll robots.txt "$OUT/"

# the two paths must not have drifted: one line differs, nothing else
diff <(sed 's|lang: qs.get("lang") ? normLang(qs.get("lang")) : "en",   /\* /en/ default \*/|lang: normLang(qs.get("lang")),|' "$OUT/en/index.html") "$OUT/zh/index.html" >/dev/null \
  || { echo "generated /en/ differs from /zh/ by more than the language line" >&2; exit 1; }

echo "tree:"
(cd "$OUT" && find . -type f | sed 's|^\./|  |' | sort)
echo "  $(cd "$OUT" && find . -type f | wc -l | tr -d ' ') files"

if [[ $DRY -eq 1 ]]; then echo "(dry run — nothing pushed)"; exit 0; fi

cd "$OUT"
git init -q -b main
git add -A
git -c user.name=Zero -c user.email=zero@2sksolutionslimited.com \
    commit -q -m "publish: /zh/ and /en/ — the widget at two individual paths

Generated from embed/index.html by ops/publish-sitelinks.sh; /en/ differs by one
line (the language default). Both paths live at depth 1, so ../assets/ resolves
as before. Nothing else is published: no index page, no bench, no docs."
git push -f "$REMOTE" main
echo "pushed to $REPO"
