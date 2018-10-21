import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import json
import plotly
import plotly.graph_objs as go
import pandas as pd
from sqlalchemy import create_engine
import yaml

#############
# ENV SETUP #
#############
config = yaml.safe_load(open("config.yaml"))

# postgresql db connection
CREATEENGINE = config['postgresql']['CREATEENGINE']

###################
# create connection
###################
engine = create_engine(CREATEENGINE)


df = pd.read_sql('SELECT * from public.lots_table order by lot;', con=engine)
df = df.fillna('')
df['sq_feet'] = df['sq_feet'].astype(int)

df_subset = df[['lot', 'sq_feet']]

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# app = dash.Dash(__name__, external_stylesheets=external_stylesheet)
app = dash.Dash()
app.scripts.config.serve_locally=True

app.layout = html.Div([
    html.H4('FPDCC Parking Lots'),

    dcc.Graph(
        id='graph-lots'
        ),

    dt.DataTable(
        rows=df_subset.to_dict('records'),
        columns=sorted(df_subset.columns),
        row_selectable=True,
        filterable=True,
        sortable=True,
        selected_row_indices=[],
        id='datatable-lots'
    ),
    html.Div(id='selected-indexes'),
], className="container")

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
    fig = plotly.tools.make_subplots(
        rows=2, cols=1,
        subplot_titles=('lot size 1', 'lot size 2',),
        shared_xaxes=True)
    marker = {'color': ['#0074D9']*len(dff)}
    for i in (selected_row_indices or []):
        marker['color'][i] = '#FF851B'
    fig.append_trace({
        'x': dff['lot'],
        'y': dff['sq_feet'],
        'type': 'bar',
        'marker': marker
    }, 1, 1)
    fig.append_trace({
        'x': dff['lot'],
        'y': dff['sq_feet'],
        'type': 'bar',
        'marker': marker
    }, 2, 1)
    fig['layout']['showlegend'] = False
    fig['layout']['height'] = 800
    fig['layout']['margin'] = {
        'l': 20,
        'r': 20,
        't': 20,
        'b': 20
    }
    fig['layout']['yaxis2']['type'] = 'linear'
    return fig


app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})


if __name__ == '__main__':
    app.run_server(debug=True)
