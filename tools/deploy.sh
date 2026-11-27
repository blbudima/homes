#!/usr/bin/env bash
# Rebuild the locked map from a fresh satellite edition, then commit and push.
# Usage: HH_PASSWORD=... tools/deploy.sh /path/to/Home-Hunt-Map-Satellite.html "Nov 24, 2026, 1:50pm PT"
# The unlocked page is only ever written to a temp folder, never into this repo.
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"; repo="$(dirname "$here")"
src="$1"; when="${2:-}"
[ -n "${HH_PASSWORD:-}${HH_KEY:-}" ] || { echo "set HH_PASSWORD (or HH_KEY)"; exit 1; }
[ -d "$here/node_modules/staticrypt" ] || (cd "$here" && npm install --silent)
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
python3 "$here/mkweb.py" "$src" "$tmp/inner.html"
node "$here/encrypt.js" "$tmp/inner.html" "$repo/index.html" "$repo/.staticrypt.json"
if grep -q '"homes": \[' "$repo/index.html"; then echo "STOP: unlocked data found in index.html"; exit 1; fi
cd "$repo"
git add -A
git diff --cached --quiet && { echo "no changes"; exit 0; }
git commit -q -m "Update map${when:+ (sheet data as of $when)}

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01FY5VeVtdXoEwj1t1Hbru9d"
git -c push.negotiate=true push -q origin HEAD:main
echo "pushed"
