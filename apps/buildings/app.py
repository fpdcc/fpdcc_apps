import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_table as dt
from dash_table.Format import Format
import plotly
from plotly import graph_objs as go
from plotly.graph_objs import *
import modin.pandas as pd
import numpy as np
from sqlalchemy import create_engine
import yaml
import json

mapbox_access_token = 'pk.eyJ1IjoiZ2x3IiwiYSI6IjdHTVp3eWMifQ.TXIsy6c3KnbqnUAeBawVsA'

app = dash.Dash()
app.scripts.config.serve_locally=True

PLOTLY_LOGO = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"

df  = pd.read_csv('/media/sf_garretwais/projects/fpdcc_apps/apps/buildings/data/buildings.csv')

df = df.sort_values(by=['buildings_id'])
df_sort_sqft = df.sort_values(by=['sqft'])
df_sort_building_type = df.sort_values(by=['building_type'])
df_sort_complex = df.sort_values(by=['complex'])
df_sort_managing_dept = df.sort_values(by=['managing_department'])

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Buildings", href="#")),
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("Data Sets", header=True),
                dbc.DropdownMenuItem("Trails", href="#"),
                dbc.DropdownMenuItem("Parking Lots", href="#"),
                dbc.DropdownMenuItem("Picnic Groves", href="#"),
            ],
            nav=True,
            in_navbar=True,
            label="More",
        ),
    ],
    brand="FPCC Data",
    brand_href="#",
    color="green",
    dark=True,
)

body = dbc.Container(
    [
        # Row for dropdown menus
        dbc.Row([
                dbc.Col(
                    html.Div(
                        dcc.Dropdown(
                            options=
                            [{"label": i, "value": i} for i in df_sort_building_type.building_type.unique()], placeholder="Select Building Type", multi=True
                        ),className="mt-2"),md=4
                    ),
                dbc.Col(
                    html.Div(
                        dcc.Dropdown(
                            options=[{"label": i, "value": i} for i in df_sort_complex.complex.unique()], placeholder="Select Complex", multi=True
                        ),className="mt-2"),md=4
                    ),
                dbc.Col(
                    html.Div(
                        dcc.Dropdown(
                            options=[{"label": i, "value": i} for i in df_sort_managing_dept.managing_department.unique()], placeholder="Select Managing Dept", multi=True
                        ),className="mt-2"),md=4
                    ),
        ]),

        # Row for mini charts
        #dbc.Row([])

        # Row for Building Details, Main graph, and Table
        dbc.Row([
                dbc.Col([
                    html.Div([
                            dcc.Graph(
                                figure={
                                    "data": [{"x": [1, 2, 3], "y": [1, 4, 9], 'type': 'bar'}],
                                    'layout' : {'title': 'Building Details'}
                                }),

                            dbc.Button("More Details", id="collapse-button", className="m-2",size="sm"),
                            dbc.Collapse(
                                #dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True),
                                dbc.Card([
                                        dbc.CardImg(
                                            src=(
                                                "https://fpdccfilestore.nyc3.cdn.digitaloceanspaces.com/danryan_visitorcenter.jpg"
                                                ),top=True
                                        ),
                                        dbc.CardBody(
                                            [
                                                dbc.CardText(
                                                    "Building Id: 32"
                                                ),
                                                dbc.CardText(
                                                    "Wastewater: City of Chicago"
                                                ),
                                                dbc.CardText(
                                                    "Address: 2318 West 87th Street, Chicago, Il 60620"
                                                ),
                                                dbc.CardLink("Doc A", href="#"),
                                                dbc.CardLink("Doc B", href="#"),
                                            ]
                                        ),
                                    ], style={"width":"auto"}),
                                    id="collapse", className="m-3"
                            )
                    ]),
                ], width={"size":4, "order": "last"}, className="p-3"),

                dbc.Col([
                        # Main Graph
                        dbc.Row(
                                dcc.Graph(
                                            id='sqft_bargraph',
                                            style={
                                                'margin': '0'
                                                },
                                            figure={
                                                'data': [
                                                {"x": df_sort_sqft['sqft'].max(), "y": df_sort_sqft['sqft'], 'type': 'bar'}
                                                ],
                                                'layout' : {
                                                    'title': 'Building Square Feet',
                                                }
                                            }
                                        )
                        ),
                        # Data Table
                        dbc.Row(
                            dt.DataTable(
                                id='table',
                                data=df.to_dict("rows"),
                                columns=[{
                                    'id': 'buildings_id',
                                    'name': 'Building ID',
                                    'type': 'text'
                                    },{
                                    'id': 'building_name',
                                    'name': 'Building Name',
                                    'type': 'text'
                                    }, {
                                    'id': 'sqft',
                                    'name': 'Square Feet',
                                    'type': 'numeric',
                                    'format': Format(precision=6)
                                    }, {
                                    'id': 'building_type',
                                    'name': 'Building Type',
                                    'type': 'text'
                                    }, {
                                    'id': 'managing_department',
                                    'name': 'Managing Department',
                                    'type': 'text'
                                    }
                                ],
                                style_table={
                                    'height': '300',
                                    'width': 'auto',
                                    'overflowY': 'auto'
                                },
                                style_cell={
                                    'minWidth': '0px',
                                    'maxWidth': '220px',
                                    'whiteSpace': 'normal',
                                    'textAlign': 'left'
                                },
                                sorting=True,
                                filtering=True,
                                sorting_type="multi",
                                row_selectable="multi",
                                selected_rows=[],
                                pagination_mode="fe",
                                pagination_settings={
                                    "displayed_pages": 1,
                                    "current_page": 0,
                                    "page_size": 20,
                                },
                                navigation="page",
                            )
                        )

                    ],width={"size":"auto", "order": "first"}),

        ], className="p-0", no_gutters=True),
    ], fluid=True
)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([navbar, body])


#collapse-button
@app.callback(
    Output("collapse", "is_open"),
    [Input("collapse-button", "n_clicks")],
    [State("collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open



# run app.py
if __name__ == "__main__":
    app.run_server(debug=True)
