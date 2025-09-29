
project = 'Tkinter GUI – Lab 3'
author = 'Hassan Khalil'
copyright = '2025, Hassan Khalil'
release = '1.0'
version = release
#

import os
import sys
sys.path.insert(0, os.path.abspath('..'))

extensions = [
    'sphinx.ext.autodoc', 
    'sphinx.ext.napoleon',  
    'sphinx.ext.viewcode',  
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

