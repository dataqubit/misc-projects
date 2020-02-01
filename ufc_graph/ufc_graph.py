import dash
import dash_cytoscape as cyto
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import pandas as pd
import numpy as np


app = dash.Dash("UFC graph")


# loading dataframe
df_ufc_total = pd.read_csv('ufcdata/data.csv', parse_dates=['date'])

df_ufc = df_ufc_total[(df_ufc_total.date.dt.year>2017) & (df_ufc_total.weight_class=='Heavyweight')]

nodes = [
    {
        'data': {'id': fighter_name, 'label': fighter_name}
    }
    for fighter_name in np.concatenate([df_ufc.R_fighter.unique(), df_ufc.B_fighter.unique()])]



edges = [
    {'data': {'source': r_fighter, 'target': b_fighter}}
    for r_fighter, b_fighter in zip(df_ufc.R_fighter, df_ufc.B_fighter)
]

elements = nodes + edges


app.layout = html.Div([

    dcc.Dropdown(
        id='dropdown-update-layout',
        value='grid',
        clearable=False,
        options=[
            {'label': name.capitalize(), 'value': name}
            for name in ['grid', 'random', 'circle', 'cose', 'concentric']
        ]
    ),
    cyto.Cytoscape(
        id='cytoscape-update-layout',
        layout={'name': 'grid'},
        style={'width': '100%', 'height': '550px'},
        elements=elements
    )
])


@app.callback(Output('cytoscape-update-layout', 'layout'),
              [Input('dropdown-update-layout', 'value')])
def update_layout(layout):
    return {
        'name': layout,
        'animate': True
    }


if __name__ == '__main__':
    app.run_server(debug=True)