# Configuration file for the Sphinx documentation builder.
# This is the top-level config for the unified site, hosted at
# https://tamil.arunc.dev (Cloudflare static assets, deployed by scripts/deploy.sh).

# -- Project information

project = "தமிழில் தியான நூல்கள்"
copyright = "See individual book attributions"
author = "Various"

release = "0.1"
version = "0.1.0"

# -- General configuration

extensions = [
    "sphinx.ext.duration",
    "sphinx.ext.intersphinx",
    "sphinx_new_tab_link",
    "sphinxcontrib.mermaid",
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "sphinx": ("https://www.sphinx-doc.org/en/master/", None),
}
intersphinx_disabled_domains = ["std"]

templates_path = ["_templates"]

exclude_patterns = ["_build", "_templates", "README.rst", "*/README.rst", "*/TODO.md", "*/_build"]

# -- Options for HTML output
html_theme = "shibuya"
html_baseurl = "https://tamil.arunc.dev/"
html_theme_options = {
    "discussion_url": "https://github.com/carun/tamil/discussions",
}
html_context = {
    "source_type": "github",
    "source_user": "carun",
    "source_repo": "tamil",
    "source_docs_path": "/",
}
html_static_path = ["_static"]
# Copied as-is to the output root. Cloudflare serves 404.html for missing
# paths (not_found_handling in wrangler.jsonc).
html_extra_path = ["_extra"]
html_favicon = "_static/dharma-wheel.png"
html_logo = "_static/dharma-wheel.png"
html_css_files = ["custom.css"]

# -- Mermaid diagrams
mermaid_output_format = "raw"

# -- Options for EPUB output
epub_show_urls = "footnote"


# -- Canonical URL fix for the dirhtml build (what scripts/deploy.sh publishes)
# Sphinx 8.0's dirhtml builder gives the root page a canonical URL of
# <html_baseurl>/index/, which does not exist. The root page is <html_baseurl>.


def _fix_root_canonical(app, pagename, templatename, context, doctree):
    if pagename == "index" and context.get("pageurl"):
        context["pageurl"] = html_baseurl


def setup(app):
    app.connect("html-page-context", _fix_root_canonical)
