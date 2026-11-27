#!/usr/bin/env bash
# Publish ONLY what the client's pages load: /embed/ + the images it uses.
#
# Why this exists (27 Nov 2026): Pages served the whole `main` tree, so
# /preview/ ("POC PREVIEW", "PLACEHOLDER — CLIENT-BUILT"), /harness/, /setup/,
# /qa/ and /docs/ were all public on the same hostname as the widget the client
# embeds. The client embeds exactly two URLs, both under /embed/:
#
#   https://2skdigitals.github.io/fhf-taxcalc-poc/embed/            (zh, part=all)
#   https://2skdigitals.github.io/fhf-taxcalc-poc/embed/?lang=en    (en, part=all)
#
# So the published branch carries embed/ + assets/ + .nojekyll + robots.txt and
# nothing else: no index page, no bench, no mock, no docs. `main` keeps the full
# history and every working file — this script only builds the published tree.
#
# The paths are identical to the old layout, so switching the Pages source to
# gh-pages does NOT change either embed URL.
#
# Usage (from the repo root, on main, tree committed):
#   bash ops/publish-clean.sh            # build + force-push gh-pages
#   bash ops/publish-clean.sh --dry-run  # list what would be published
set -euo pipefail

BRANCH=gh-pages
PATHS=(embed assets .nojekyll robots.txt)
DRY=0
[[ "${1:-}" == "--dry-run" ]] && DRY=1

cd "$(git rev-parse --show-toplevel)"
[[ -z "$(git status --porcelain --untracked-files=no)" ]] || {
  echo "working tree is dirty — commit first (published bytes must match a commit)" >&2; exit 1; }

# One guard that matters: embed/ must not reference anything outside the
# published set, or the live page 404s an asset.
stray=$(grep -oE '(src|href)="\.\./[^"]+"' embed/index.html | grep -vE '"\.\./assets/' || true)
[[ -z "$stray" ]] || { echo "embed/ references paths outside the publish set:" >&2; echo "$stray" >&2; exit 1; }

IDX=$(mktemp)
export GIT_INDEX_FILE=$IDX
git read-tree --empty
git add -A -- "${PATHS[@]}"
TREE=$(git write-tree)
unset GIT_INDEX_FILE

echo "published tree contains:"
git ls-tree -r --name-only "$TREE" | sed 's/^/  /' | head -40
echo "  … $(git ls-tree -r --name-only "$TREE" | wc -l | tr -d ' ') files total"

[[ $DRY -eq 1 ]] && { echo "(dry run — nothing pushed)"; exit 0; }

COMMIT=$(git commit-tree "$TREE" -m "publish: embed + assets only

The client embeds exactly two URLs, both under /embed/ (zh bare, en ?lang=en).
Everything else in this repo (preview, harness, setup, qa, docs, design, shots)
is internal and must not be reachable on the public host.")
git push --force origin "$COMMIT:refs/heads/$BRANCH"
echo "pushed $COMMIT -> $BRANCH"
