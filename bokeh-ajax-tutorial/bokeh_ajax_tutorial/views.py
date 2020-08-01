"""
Routes and views for the flask application.
"""

from datetime import datetime
from bokeh_ajax_tutorial import app
import numpy as np

from flask import Flask,make_response, render_template, jsonify, request
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import AjaxDataSource, CustomJS


def crossdomain(f):
    def wrapped_function(*args, **kwargs):
        resp = make_response(f(*args, **kwargs))
        h = resp.headers
        h['Access-Control-Allow-Origin'] = '*'
        h['Access-Control-Allow-Methods'] = "GET, OPTIONS, POST"
        h['Access-Control-Max-Age'] = str(21600)
        requested_headers = request.headers.get('Access-Control-Request-Headers')
        if requested_headers:
            h['Access-Control-Allow-Headers'] = requested_headers
        return resp
    return wrapped_function

@app.route('/')
@app.route('/dashboard/')
def show_dashboard():
    plots = []    
    plots.append(make_plot())
    plots.append(make_ajax_plot())
    return render_template('dashboard.html',plot_width=800, plots=plots)

x = list(np.arange(0, 6, 0.1))
y = list(np.sin(x) + np.random.random(len(x)))
@app.route('/data/', methods=['GET', 'OPTIONS', 'POST'])
@crossdomain
def data():
    x.append(x[-1]+0.1)
    y.append(np.sin(x[-1])+np.random.random())
    return jsonify(points=list(zip(x,y)))

def make_plot():
    plot = figure(plot_height=300, plot_width=800)
    x = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    y = [2**v for v in x]
    plot.line(x, y, line_width=4)    
    script, div = components(plot)
    return script, div

def make_ajax_plot():    
    adapter = CustomJS(code="""
        const result = {x: [], y: []}
        const pts = cb_data.response.points
        for (let i=0; i<pts.length; i++) {
            result.x.push(pts[i][0])
            result.y.push(pts[i][1])
        }
        return result
    """)
    source = AjaxDataSource(data_url=request.url_root + 'data/',
                            polling_interval=2000, 
                            adapter=adapter)
    plot = figure(plot_height=300, plot_width=800, background_fill_color="lightgrey",
               title="Streaming Noisy sin(x) via Ajax")
    plot.line('x', 'y', source=source)
    plot.x_range.follow = "end"
    plot.x_range.follow_interval = 10
    script, div = components(plot)
    return script, div