import os
import sys

sys.path.insert(0, os.path.abspath('../'))

project = 'QuESO'
copyright = '2026, Sarah Riley'
author = 'Sarah Riley'
version = 'mild'
release = ''

# -- General configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.coverage',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
]

# -- Options for HTML output
html_title = 'QuESO Documentation'
html_logo = 'assets/img/banner.png'
html_favicon = 'assets/img/icon.png'

html_css_files = [
    'css/custom.css',
]
html_copy_source = False

html_theme = 'sphinx_rtd_theme'

html_static_path = ["assets"]

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
 ('index', 'queso.tex', u'QuESO Official Manual', u'Sarah Riley', 'manual'),
]
# latex_logo = 'banner_icon.png'
latex_domain_indices = True
latex_show_urls = 'footnote'
latex_use_xindy = False
# -- Options for EPUB output
epub_show_urls = 'footnote'
