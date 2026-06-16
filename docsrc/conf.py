import os
import sys

sys.path.insert(0, os.path.abspath('./'))

from queso_cluster import __version__

#from queso_cluster import __version__

project = 'QuESO'
copyright = '2026, Sarah Riley'
author = 'Sarah Riley'
version = __version__
release = __version__

# -- General configuration

extensions = [
    "autoapi.extension",
    "sphinx.ext.napoleon",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx.ext.graphviz",
    "sphinx_design",
    "sphinx_copybutton",
    #"_extension.gallery_directive",
    "sphinx.ext.githubpages",
    'numpydoc',
    "myst_nb",
    'sphinx.ext.coverage',
]

autosummary_generate = True
autodoc_typehints = "description"
autodoc_member_order = "groupwise"

autoapi_type = "python"
# Use absolute path to ensure AutoAPI can find the source code in all environments
_autoapi_source = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "queso_cluster")
)
autoapi_dirs = [_autoapi_source]
autoapi_keep_files = True
autoapi_root = "api"
autoapi_add_toctree_entry = True
autoapi_options = ["members", "undoc-members", "show-inheritance", "show-module-summary"]
autoapi_member_order = "groupwise"

#autodoc_preserve_defaults = True
numpydoc_show_class_members = False
#autodoc_typehints = "none"

add_module_names = False

html_static_path = ["_static"]
templates_path = ["_templates"]

#master_doc = 'homeIndex'

# -- Options for HTML output
html_title = 'QuESO Documentation'
html_short_title = 'QuESO'
html_logo = '_static/img/iconTeal_small.png'
html_favicon = '_static/img/iconTeal_small.png'

html_css_files = [
    'css/custom.css',
    'https://cdn.jsdelivr.net/gh/devicons/devicon@latest/devicon.min.css'
]
html_copy_source = False

html_theme = 'pydata_sphinx_theme' #'sphinx_rtd_theme'

# html_theme_options = {
#     'logo_only': True,
# }

# html_additional_pages = {
# 	"index": "landing.html"
# }


html_theme_options = {
    "navbar_start": ["navbar-logo"],
    "navbar_align": 'left',
    "icon_links": [{
        "name": "GitHub",
        "url": "https://github.com/SharkSorceress/queso-cluster",
        "icon": "devicon-github-original",
        },
        {
         "name": "PyPI",
         "url": "https://pypi.org/project/queso-cluster/",
         "icon": "devicon-pypi-plain",
      }],
    "logo": {
         'image_dark': '_static/img/quesoBanner_small.png',
         'image_light': '_static/img/iconTeal_small.png'
    },
    "show_nav_level": 2,
    "show_toc_level": 2,
    "navbar_center": ["navbar-nav"],
    "header_links_before_dropdown": 3,
    #"navbar_center": ["contributors"],
    #"navbar_end": ["navbar-icon-links"],
    "navbar_end": ["theme-switcher", "navbar-icon-links"],
    "back_to_top_button": True,
    "collapse_navigation": True,
    "announcement": "queso-cluster v{} is out now! Have it with chips.".format(version),
}

html_sidebars = {
    "getting-started/**": [],
    "contributors/**": [],
    "tutorials/**": ["sidebar-collapse", "sidebar-nav-bs"],
    "api/**": ["sidebar-collapse", "sidebar-nav-bs"],
}

autosummary_generate = True
autodoc_typehints = "description"
autodoc_member_order = "groupwise"

# -- Options for LaTeX output
# latex_engine = 'pdflatex'
# latex_elements = {
#     'papersize': 'a4paper',
#     'pointsize': '11pt',
#     }
# latex_documents = [
#  ('index', 'queso.tex', u'queso-cluster Official Manual', u'Sarah Riley', 'manual'),
# ]
# latex_logo = '_static/img/iconTeal.png'
# latex_domain_indices = True
# latex_show_urls = 'footnote'
# latex_use_xindy = False
# # -- Options for EPUB output
# epub_show_urls = 'footnote'
