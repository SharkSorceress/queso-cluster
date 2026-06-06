import os
import sys

sys.path.insert(0, os.path.abspath('./'))

project = 'QuESO'
copyright = '2026, Sarah Riley'
author = 'Sarah Riley'
version = 'v0.1.0'
release = 'v0.1.0'

# -- General configuration

extensions = [
    'sphinx.ext.autodoc',
    'numpydoc',
    "myst_nb",
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.viewcode',
    'sphinx.ext.githubpages'
]

#autodoc_preserve_defaults = True
numpydoc_show_class_members = False
#autodoc_typehints = "none"

add_module_names = False

html_static_path = ["_static"]

# -- Options for HTML output
html_title = 'QuESO Documentation'
html_short_title = 'QuESO'
html_logo = '_static/img/iconTeal_small.png'
html_favicon = '_static/img/iconTeal_small.png'

html_css_files = [
    'css/custom.css',
]
html_copy_source = False

html_theme = 'sphinx_rtd_theme'

html_theme_options = {
    'logo_only': True,
}

# -- Options for LaTeX output
latex_engine = 'pdflatex'
latex_elements = {
    'papersize': 'a4paper',
    'pointsize': '11pt',
    }
latex_documents = [
 ('index', 'queso.tex', u'queso-cluster Official Manual', u'Sarah Riley', 'manual'),
]
latex_logo = '_static/img/iconTeal.png'
latex_domain_indices = True
latex_show_urls = 'footnote'
latex_use_xindy = False
# -- Options for EPUB output
epub_show_urls = 'footnote'
