# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------
# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath.
import os
import sys
# Assuming your 'src' directory is one level up and then 'src'
# e.g., project_root/src/oso/framework
# and conf.py is in project_root/docs/
# Adjust this path as necessary!
sys.path.insert(0, os.path.abspath('../../src'))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'IBM Offline Signing Orchestrator Framework'
copyright = '2025, IBM'
author = 'IBM'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',  # <--- ADD THIS
    'sphinx.ext.viewcode',    # Recommended for "View Source" links
    'sphinx.ext.todo',        # If you use .. todo:: directives
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Intersphinx configuration ------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html#configuration
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'flask': ('https://flask.palletsprojects.com/en/latest/', None),
    # Add other external libraries if you reference their types and want them linked
    # e.g., 'pathlib' types are typically covered by 'python' mapping
}


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
# html_static_path = ['_static']

# -- Autodoc configuration ---------------------------------------------------
# Custom function to skip 'model_config' members during autodoc


def autodoc_skip_model_config(app, what, name, obj, skip, options):
    return skip or name in ('model_config')


def setup(app):
    app.connect('autodoc-skip-member', autodoc_skip_model_config)
