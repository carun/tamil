#!/usr/bin/env bash
# Build the site (HTML + PDFs) from the LAST COMMIT (HEAD), not the working
# tree, and deploy it as Cloudflare static assets (wrangler.jsonc, like
# kural.arunc.dev) to https://tamil.arunc.dev.
#
# Uncommitted edits are never published: commit to put them live. Pushing to
# main runs this script in GitHub Actions (.github/workflows/deploy.yml), so a
# manual run is only needed to deploy without pushing. To preview locally, run
# `make html` and open _build/html/index.html.
#
# The deployed site uses Sphinx's dirhtml builder (chapter-1/index.html, linked
# as chapter-1/) rather than `make html` (chapter-1.html): Cloudflare
# redirects every *.html URL to its extensionless form, so .html links would
# cost a redirect on every click.
#
# Requires: the Python deps from requirements.txt in $VENV (default
# ~/pyenv/tamil), pandoc 3.x, typst, curl, unzip and wrangler.
set -euo pipefail

VENV="${VENV:-$HOME/pyenv/tamil}"

REPO_ROOT="$(cd "$(dirname "$0")/.." && git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

if [[ ! -x "$VENV/bin/sphinx-build" ]]; then
  echo "sphinx-build not found in $VENV. Create it with:" >&2
  echo "  python3 -m venv $VENV && $VENV/bin/pip install -r requirements.txt" >&2
  exit 1
fi

# PDF fonts: the same Noto releases the Read the Docs build used. Downloaded
# once into fonts/ (gitignored) and reused after that.
if [[ ! -f fonts/NotoSansTamil-Regular.ttf || ! -f fonts/NotoSans-Regular.ttf ]]; then
  echo "Downloading PDF fonts into fonts/ ..."
  mkdir -p fonts
  DL="$(mktemp -d)"
  curl -fsSL "https://github.com/notofonts/tamil/releases/download/NotoSansTamil-v2.004/NotoSansTamil-v2.004.zip" -o "$DL/tamil.zip"
  unzip -jqo "$DL/tamil.zip" "NotoSansTamil/unhinted/ttf/*.ttf" -d fonts/
  curl -fsSL "https://github.com/notofonts/latin-greek-cyrillic/releases/download/NotoSans-v2.015/NotoSans-v2.015.zip" -o "$DL/sans.zip"
  unzip -jqo "$DL/sans.zip" "NotoSans/unhinted/ttf/NotoSans-Regular.ttf" "NotoSans/unhinted/ttf/NotoSans-Bold.ttf" -d fonts/
  rm -rf "$DL"
fi

# Build under _build/ (gitignored), not /tmp: snap packages such as typst get a
# private /tmp and can't see files there.
mkdir -p _build
TMP="$(mktemp -d "$REPO_ROOT/_build/deploy.XXXXXX")"
trap 'rm -rf "$TMP"' EXIT

# Export only committed files, build there, deploy that.
git archive HEAD | tar -x -C "$TMP"
cp -r fonts "$TMP/fonts"

# shellcheck disable=SC1091
source "$VENV/bin/activate"
sphinx-build -M dirhtml "$TMP" "$TMP/_build"
make -C "$TMP" pdf
mkdir -p "$TMP/_build/dirhtml/_static/pdf"
cp "$TMP"/_build/pdf/*.pdf "$TMP/_build/dirhtml/_static/pdf/"

# wrangler.jsonc (from HEAD) points at _build/dirhtml and pins the account.
( cd "$TMP" && wrangler deploy )
