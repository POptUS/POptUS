# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import json

from poptus import __version__

project   = "POptUS"
copyright = (
    "2025, The Regents of the University of California, through "
    "Lawrence Berkeley National Laboratory and UChicago Argonne LLC through "
    "Argonne National Laboratory (subject to receipt of any required approvals "
    "from the U.S. Dept. of Energy).  All rights reserved"
)
author    = "Jeffrey Larson, Matt Menickelly, Jared O'Neal, and Stefan M. Wild"
version   = __version__
release   = version

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.autodoc',
              'sphinx.ext.autosectionlabel',
              'sphinx.ext.todo']
numfig = True

# https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html#substitutions
rst_prolog = ""
with open("sphinx_macros.json", "r") as fptr:
    macro_configs = json.load(fptr)
for key, value in macro_configs.items():
    rst_prolog += f".. |{key}| replace:: {value}\n"

# Extensions
autoclass_content = "init"
autodoc_member_order = "bysource"

autosectionlabel_prefix_document = True

todo_include_todos = True

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'

# -- LaTeX configuration -----------------------------------------------------
# Some of this configuration is from
# https://stackoverflow.com/questions/9728292/creating-latex-math-macros-within-sphinx

latex_engine = "pdflatex"
latex_elements = {
    "papersize": "letterpaper",
    "pointsize": "10pt",
    "preamble": ""
}
