# app.py
#import main Flask class and request object

from flask import Flask, request, render_template
#from flask_sqlalchemy import SQLAlchemy
import plotly
import plotly.graph_objs as go
import numpy as np
import json
import pandas as pd

app = Flask(__name__)


@app.route('/showLineChart')
def line():
    count = 500
    xScale = np.linspace(0, 100, count)
    yScale = np.random.randn(count)

    # Create a trace
    trace = go.Scatter(
        x=xScale,
        y=yScale
    )

    data = [trace]
    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('index.html', graphJSON=graphJSON)

@app.route('/')
def index():
    feature = 'Bar'
    bar = create_plot(feature)
    return render_template('index.html', plot=bar)

def create_plot(feature):
    if feature == 'Bar':
        N = 40
        x = np.linspace(0, 1, N)
        y = np.random.randn(N)
        df = pd.DataFrame({'x': x, 'y': y}) # creating a sample dataframe
        data = [
            go.Bar(
                x=df['x'], # assign x as the dataframe column 'x'
                y=df['y']
            )
        ]
    else:
        N = 1000
        random_x = np.random.randn(N)
        random_y = np.random.randn(N)

        # Create a trace
        data = [go.Scatter(
            x = random_x,
            y = random_y,
            mode = 'markers'
        )]

    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON

@app.route('/bar', methods=['GET', 'POST'])
def change_features():

    feature = request.args['selected']
    graphJSON= create_plot(feature)

    return graphJSON

@app.route('/form-example')
def formexample():
    return '<h1>Hello There</h1>'

@app.route('/home', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':  # this block is only entered when the form is submitted
        address = request.form.get('address')
        #return render_template('index.html', address=address)
        return '''<h1>The address value is: {}</h1>'''.format(address)

    return '''<form method="POST">
                  Address: <input type="text" name="address"><br>
                  <input type="submit" value="Submit"><br>
              </form>'''


if __name__ == '__main__':
    app.run(debug=True)