"""
Sphinx Documentation Generator
"""

from datetime import datetime
from pathlib import Path

from mlflow_export_import._version import __mlflow_export_import__ as package_name  # noqa
from mlflow_export_import._version import __version__  # noqa

_this_dir = Path(__file__).resolve().parent
source_code_dir = _this_dir.parent.parent.joinpath("mlflow_export_import")

_author = "amesar"
project = package_name
copyright = f"{datetime.now().year}, {_author}"
author = _author
release = __version__

extensions = [
    "sphinx.ext.napoleon",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.coverage",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx.ext.autosectionlabel",

    "sphinxcontrib.apidoc",

    "autodocsumm",
    "myst_parser",
    "autoclasstoc",
    "sphinx_copybutton",
    "sphinx_autodoc_typehints",
    "sphinx_autodoc_defaultargs",
    "sphinx_click",
]

templates_path = ["_templates"]
html_static_path = ["_static"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "sphinx_rtd_theme"
html_show_sphinx = False
html_show_sourcelink = False

source_suffix = {
    ".rst": "restructuredtext",
    ".txt": "markdown",
    ".md": "markdown",
}

autosummary_generate = True
apidoc_module_dir = str(source_code_dir)
apidoc_output_dir = str(source_code_dir.parent.joinpath("docs", "source", "api"))
apidoc_excluded_paths = ["tests"]
apidoc_separate_modules = True

rst_prolog = """
.. |default| raw:: html

    <div class="default-value-section">""" + \
             ' <span class="default-value-label">Default:</span>'
