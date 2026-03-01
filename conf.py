# Configuration file for the Sphinx documentation builder.
# This is the top-level config used by ReadTheDocs to build the unified site.

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
    "sphinx_design",
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
html_static_path = ["_static"]
html_css_files = ["custom.css"]

# -- Options for EPUB output
epub_show_urls = "footnote"
