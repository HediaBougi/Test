# app.py

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

@app.route('/home')
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

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':  # this block is only entered when the form is submitted
        address = request.form.get('address')
        
        #return render_template('index.html', address=address)
        #return '''<h1>The address value is: {}</h1>'''.format(address)
        # Tiff files path
        data_dsm_path = "/home/becode/3D House Project/Data/DSM/GeoTIFF/"
        data_dtm_path = "/home/becode/3D House Project/Data/DTM/GeoTIFF/"

        # Request the formatted address
        # Request BBox of the address
        # Raise an error msg if the address doesn't exist
        try:

            req = requests.get(f"http://loc.geopunt.be/geolocation/location?q={address}&c=1").json()

            formattedaddress = req["LocationResult"][0]["FormattedAddress"]

            # Get Bounding Box of the entered address
            bb_addr = BBox(req["LocationResult"][0]["BoundingBox"]["LowerLeft"]["X_Lambert72"],
                           req["LocationResult"][0]["BoundingBox"]["LowerLeft"]["Y_Lambert72"],
                           req["LocationResult"][0]["BoundingBox"]["UpperRight"]["X_Lambert72"],
                           req["LocationResult"][0]["BoundingBox"]["UpperRight"]["Y_Lambert72"])

        except IndexError:
            print(address, " :Address doesn't exist")
        except:
            print("Something else went wrong")
            exit()

        polygon = PolygonRequest(address)

        # List all tiff files in directory using Path
        # Search for the matched tiff
        # Compare the BBox address to the BBox tiff file
        files_in_data_dsm = (entry for entry in Path(data_dsm_path).iterdir() if entry.is_file())
        for item in files_in_data_dsm:
            tiff_dsm = rasterio.open(data_dsm_path + item.name)
            if bb_addr.isIn(
                    BBox(tiff_dsm.bounds.left, tiff_dsm.bounds.bottom, tiff_dsm.bounds.right, tiff_dsm.bounds.top)):
                tiff_dtm = rasterio.open(data_dtm_path + item.name.replace("DSM", "DTM"))
                break

        # Crop tiff files
        crop_dsm_img, crop_dsm_transform = mask(dataset=tiff_dsm, shapes=polygon, crop=True, indexes=1)
        crop_dtm_img, crop_dtm_transform = mask(dataset=tiff_dtm, shapes=polygon, crop=True, indexes=1)
        crop_chm_img = crop_dsm_img - crop_dtm_img

        # 3D plot
        # fliplr: Reverse the order of elements in 'crop_chm_img' array horizontally
        fig = go.Figure(data=go.Surface(z=np.fliplr(crop_chm_img), colorscale='plotly3'))
        fig.update_layout(scene_aspectmode='manual', scene_aspectratio=dict(x=1, y=1, z=0.5))
        fig.update_layout(
            title={
                'text': "3D Building at " + formattedaddress,
                'y': 0.9,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
            title_font_color="green")

        fig.show()
        
    return '''<form method="POST">
                  Address: <input type="text" name="address"><br>
                  <input type="submit" value="Submit"><br>
              </form>'''


if __name__ == '__main__':
    app.run(debug=True)
