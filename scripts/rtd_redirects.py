#!/usr/bin/env python3
"""Build the Read the Docs output: redirect stubs pointing at tamil.arunc.dev.

The site moved from tamil.rtfd.io to https://tamil.arunc.dev (Cloudflare static
assets, deployed by scripts/deploy.sh). Read the Docs still builds on every push, but
it now publishes only these stubs, so old links land on the same page at the
new address. The new site uses clean URLs (Sphinx dirhtml), so:

    tamil.readthedocs.io/ta/latest/glossary/index.html
      -> https://tamil.arunc.dev/glossary/
    tamil.readthedocs.io/ta/latest/glossary/02-glossary.html
      -> https://tamil.arunc.dev/glossary/02-glossary/

Every page gets a stub with an instant meta refresh and a canonical link, which
search engines treat as a permanent move. Anything else (PDFs, images, typos)
hits Read the Docs' 404 page, which redirects by rewriting the path in JS.

Usage: rtd_redirects.py OUTPUT_DIR   (on RTD: "$READTHEDOCS_OUTPUT/html")
"""

import html
import json
import sys
from pathlib import Path

NEW_BASE = "https://tamil.arunc.dev/"
ROOT = Path(__file__).resolve().parent.parent

# Directories that hold no published pages, and files Sphinx excludes
# (see exclude_patterns in conf.py).
SKIP_DIRS = {"_build", "_templates", "_static", "_extra", "scripts", "typst", "fonts"}
SKIP_FILES = {"README.rst"}

# Pages Sphinx generates without a source file.
GENERATED = ["genindex.html", "search.html"]

STUB = """<!doctype html>
<html lang="ta">
<head>
<meta charset="utf-8">
<title>புதிய முகவரி: tamil.arunc.dev</title>
<link rel="canonical" href="{url}">
<meta http-equiv="refresh" content="0; url={url}">
<script>location.replace({url_js} + location.search + location.hash);</script>
</head>
<body>
<p>இந்தப் பக்கம் புதிய முகவரிக்கு மாற்றப்பட்டுள்ளது: <a href="{url}">{url}</a></p>
<p>This page has moved to <a href="{url}">{url}</a></p>
</body>
</html>
"""

# Served by RTD for any missing path. RTD paths look like /<lang>/<version>/rest,
# so drop the first two segments, then map *.html to clean URLs as clean_url()
# does. Other files (PDFs, images) keep their path.
NOT_FOUND = """<!doctype html>
<html lang="ta">
<head>
<meta charset="utf-8">
<meta name="robots" content="noindex">
<title>புதிய முகவரி: tamil.arunc.dev</title>
<script>
var p = location.pathname.replace(/^\\/[^\\/]+\\/[^\\/]+\\/?/, "");
p = p.replace(/(^|\\/)index\\.html$/, "$1").replace(/\\.html$/, "/");
location.replace({base_js} + p + location.search + location.hash);
</script>
</head>
<body>
<p>இந்தத் தளம் புதிய முகவரிக்கு மாற்றப்பட்டுள்ளது: <a href="{base}">{base}</a></p>
<p>This site has moved to <a href="{base}">{base}</a></p>
</body>
</html>
"""


def clean_url(page):
    """Map an html-builder path to its dirhtml URL on the new site."""
    if page == "index.html":
        return NEW_BASE
    if page.endswith("/index.html"):
        return NEW_BASE + page[: -len("index.html")]
    return NEW_BASE + page[: -len(".html")] + "/"


def pages():
    for rst in sorted(ROOT.rglob("*.rst")):
        rel = rst.relative_to(ROOT)
        if rel.parts[0] in SKIP_DIRS or rel.parts[0].startswith(".") or rel.name in SKIP_FILES:
            continue
        yield rel.with_suffix(".html").as_posix()
    yield from GENERATED


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    out = Path(sys.argv[1])
    count = 0
    for page in pages():
        url = clean_url(page)
        dest = out / page
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(
            STUB.format(url=html.escape(url), url_js=json.dumps(url)), encoding="utf-8"
        )
        count += 1
    (out / "404.html").write_text(
        NOT_FOUND.format(base=html.escape(NEW_BASE), base_js=json.dumps(NEW_BASE)),
        encoding="utf-8",
    )
    print(f"Wrote {count} redirect stubs and 404.html to {out}")


if __name__ == "__main__":
    main()
