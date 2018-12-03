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
import numpy as np
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

df  = pd.read_csv('/home/garret/projects/fpdcc_apps/apps/parkinglot_dashboard/test_data/parkinglots_simplified_centroid_4326_v2.csv')
site_lat = list(df['lat'])
site_lon = list(df['lon'])
locations_name = list(df['lot_id'])
zones = df['zone'].unique()
zones = np.append(zones, ['All'])

#external_stylesheet = ['https://codepen.io/glw/pen/Mzxpax.css']

#app = dash.Dash(__name__, external_stylesheets=external_stylesheet)
app = dash.Dash()
app.scripts.config.serve_locally=True

layout = dict(
    autosize=True,
    height=800,
    font=dict(color='#fffcfc'),
    titlefont=dict(color='#fffcfc', size='14'),
    margin=dict(
        l=35,
        r=35,
        b=35,
        t=45
    ),
    hovermode="closest",
    plot_bgcolor="#191A1A",
    paper_bgcolor="#020202",
    legend=dict(font=dict(size=10), orientation='h'),
    title='Parking Lots',
    mapbox = dict(
        accesstoken = mapbox_access_token,
        center = dict(
            lat = 41.808611,
            lon = -87.888889
        ),
        zoom = 9,
        style = 'light'
    )
)

def gen_map(map_data):
    # groupby returns a dictionary mapping the values of the first field
    # 'classification' onto a list of record dictionaries with that
    # classification value.
    return {
        "data": [
                {
                    "type": "scattermapbox",
                    "lat": list(map_data['lat']),
                    "lon": list(map_data['lon']),
                    "text": list(map_data['lot']),
                    "mode": "markers",
                    "name": list(map_data['sqft']),
                    "marker": {
                        "size": 4,
                        "opacity": 0.8,
                        "color": '#265465'
                    }
                }
            ],
        "layout": layout
    }

app.layout = html.Div([
    html.H4('FPDCC Parking Lots'),
    html.Div([
        dcc.Dropdown(
            id='yaxis',
            options=[{'label': i.title(), 'value': i} for i in zones],
            value='South'
        )
    ],style={'width': '48%', 'float': 'left', 'display':'inline-block'}),
    html.Button(
        id='submit-button',
        n_clicks=0,
        children='Submit',
        style={'fontSize':20, 'display':'inline-block'}
    ),
    html.Div([
        dcc.Graph(
        	id = 'map',
        	figure = dict(
        		data = [dict(
        			type = 'scattermapbox',
                    text = list(df[df['zone']=='South']['lot_id']),
                    lat = df[df['zone']=='South']['lat'],
        		    lon = df[df['zone']=='South']['lon'],
                    mode = 'markers'
                    )],
        		layout = dict(
                    hovermode = "closest",
        			height = 800,
        			autosize = True,
        			mapbox = dict(
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
    ], className = 'twelve columns'),
        html.Div([
            dcc.Graph(
                id = 'graph-lots'
            )
    ], className = 'twelve columns'),
    html.Div([
        dt.DataTable(
            #rows = [],
            rows = df[df['zone'] == 'South'].to_dict('records'),
            #rows = df.to_dict('records'),
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

# Dropdown and submit button callback to DataTable
@app.callback(
    Output('datatable-lots', 'rows'),
    [Input('submit-button', 'n_clicks')],
    [State('yaxis', 'value')])
def zone_parkinglots(submitbutton, value):
    if value == 'All':
        rows = df.to_dict('records')
    else:
        dff = df[df['zone'] == value]
        rows = dff.to_dict('records')
    return rows


#
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

# Update bar graph based on DataTable
@app.callback(
    Output('graph-lots', 'figure'),
    [Input('datatable-lots', 'rows'),
     Input('datatable-lots', 'selected_row_indices')])
def update_figure(rows, selected_row_indices):
    dff = pd.DataFrame(rows)
    data = [go.Bar(
            x = dff['lot_id'],
            y = dff['sqft'],
            width = 1,
            name = 'Lot Square Feet'
            )
        ]
    fig = go.Figure(data=data)
    return fig


app.css.append_css({
    'external_url': 'https://codepen.io/glw/pen/Mzxpax.css'
})


if __name__ == '__main__':
    app.run_server(debug=True)
