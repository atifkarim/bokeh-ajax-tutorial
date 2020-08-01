"""
The flask application package.
"""

from flask import Flask
app = Flask(__name__)

import bokeh_ajax_tutorial.views