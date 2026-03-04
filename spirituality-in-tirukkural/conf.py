# Configuration file for the Sphinx documentation builder.
# This conf.py is for standalone local builds of this book only.
# ReadTheDocs uses the top-level conf.py.

# -- Project information

project = "Spirituality in Tirukkural"
copyright = "Arun Chandrasekaran"
author = "Arun Chandrasekaran"

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

templates_path = ["../_templates"]

exclude_patterns = ["_build", "README.rst"]

# -- Options for HTML output
html_theme = "shibuya"
html_static_path = ["../_static"]
html_css_files = ["custom.css"]

# -- Options for EPUB output
epub_show_urls = "footnote"
