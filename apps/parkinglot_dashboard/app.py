import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import json
import plotly
from plotly import graph_objs as go
from plotly.graph_objs import *
import pandas as pd
from sqlalchemy import create_engine
import yaml

mapbox_access_token = 'pk.eyJ1IjoiZ2x3IiwiYSI6IjdHTVp3eWMifQ.TXIsy6c3KnbqnUAeBawVsA'

#############
# ENV SETUP #
#############
# config = yaml.safe_load(open("config.yaml"))

# postgresql db connection
# CREATEENGINE = config['postgresql']['CREATEENGINE']

###################
# create connection
###################
# engine = create_engine(CREATEENGINE)
# sql = 'SELECT lot, sq_feet, geom from public.lots_table order by lot;'

# gdf = gpd.GeoDataFrame.from_postgis(sql, con=engine, geom_col='geom' )

df  = pd.read_csv('/home/garret/projects/fpdcc_apps/apps/parkinglot_dashboard/test_data/parkinglots_simplified_centroid_4326.csv')
site_lat = list(df['lat'])
site_lon = list(df['lon'])
locations_name = list(df['lot'])

external_stylesheet = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheet)
app = dash.Dash()
app.scripts.config.serve_locally=True

app.layout = html.Div([
    html.H4('FPDCC Parking Lots'),
    html.Div([
        html.Div([
            dcc.Graph(
            	id = 'map',
            	figure = dict(
            		data = [dict(
            			type = 'scattermapbox',
                        lat = site_lat,
            		    lon = site_lon,
                        mode = 'markers'
                        )],
            		layout = dict(
                        hovermode = "closest",
            			height = 800,
            			autosize = True,
            			mapbox = dict(
            				layers = [dict(
            					type = 'point',
            					color = '#265465'
            				)],
            				accesstoken = mapbox_access_token,
            				center = dict(
            		            lat = 41.808611,
            		            lon = -87.888889
            		        ),
            		        zoom = 9,
            		        style = 'light'
            			)
            		)
            	)
            )
        ], className = 'six columns'),
        html.Div([
            dcc.Graph(
                id = 'graph-lots'
            )
    ], className = 'six columns')
    ], className = 'row'),

    html.Div([
        dt.DataTable(
            rows = df.to_dict('records'),
            columns = sorted(df.columns.difference(['geom'])),
            row_selectable = True,
            filterable = True,
            sortable = True,
            selected_row_indices = [],
            id = 'datatable-lots'
        )
    ]),
    html.Div(id = 'selected-indexes'),
], className = "container")

@app.callback(
    Output('datatable-lots', 'selected_row_indices'),
    [Input('graph-lots', 'clickData')],
    [State('datatable-lots', 'selected_row_indices')])
def update_selected_row_indices(clickData, selected_row_indices):
    if clickData:
        for point in clickData['points']:
            if point['pointNumber'] in selected_row_indices:
                selected_row_indices.remove(point['pointNumber'])
            else:
                selected_row_indices.append(point['pointNumber'])
    return selected_row_indices


@app.callback(
    Output('graph-lots', 'figure'),
    [Input('datatable-lots', 'rows'),
     Input('datatable-lots', 'selected_row_indices')])
def update_figure(rows, selected_row_indices):
    dff = pd.DataFrame(rows)
    data = [go.Bar(
            x = dff['lot'],
            y = dff['sqft'],
            width = 1,
            name = 'Lot Square Feet'
            )
        ]
    fig = go.Figure(data=data)
    return fig


#app.css.append_css({
#    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
#})


if __name__ == '__main__':
    app.run_server(debug=True)
