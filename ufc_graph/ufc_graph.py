import dash
import dash_cytoscape as cyto
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import pandas as pd
import numpy as np
import json


w_class_color_map = {'Lightweight': 'darkred', 'Welterweight': 'darkgreen', 
'Middleweight': 'darkblue', 'Heavyweight': 'black', 
'Light Heavyweight': 'orange', 'Featherweight': 'gray',
'Bantamweight': 'white', 'Flyweight': 'AntiqueWhite',
"Women's Strawweight": 'Beige', "Women's Bantamweight": 'CadetBlue',
'Open Weight': 'Chocolate', "Women's Flyweight": 'DarkSlateGrey',
"Catch Weight": 'DeepPink', "Women's Featherweight": 'Tomato'}


# columns we are interested in for a fight
fight_features = ['R_fighter', 'B_fighter', 'Referee', 'date', 'location', 'Winner', 'title_bout',
 'weight_class','no_of_rounds', 'R_age', 'R_Height_cms', 'R_Reach_cms', 'R_Weight_lbs', 
 'B_age','B_Height_cms', 'B_Reach_cms', 'B_Weight_lbs']

# stylesheet for cytoscape objects
my_stylesheet = [
    # Group selectors
    {
        'selector': 'node',
        'selectable': True,
        'style': {
            'content': 'data(label)'
        }
    },
    {
        "selector": "edge",
        "selectable": True,
        "style": {
          "curve-style": "bezier",
          'target-arrow-color': 'blue',
          'target-arrow-shape': 'vee',
          'arrow-scale': 2
          #"line-color": "#999999",
          #"line-style": "solid",
        },

    }]

# Class selectors
for color_name in w_class_color_map.values():
    if color_name == 'white':
        my_stylesheet.append({
        'selector': '.%s' %color_name,
        'style': {
            'background-color': color_name,
            'line-color': color_name,
            'border-paint': 'black',
            "border-width": 1,
            "border-style": "solid"
        }
        })
    else:
        my_stylesheet.append({
            'selector': '.%s' %color_name,
            'style': {
                'background-color': color_name,
                'line-color': color_name
            }
        })


my_stylesheet.append({
        'selector': '.jonjones',
        'style': {
            'background-image': 'data(url)',
            'background-fit': 'cover'
        }
        })

my_stylesheet.extend([{
        'selector': '.triangle',
        'style': {
            'shape': 'triangle'
        }
    },

    {
        'selector': '.square',
        'style': {
            'shape': 'square'
        }
    },

    {
        'selector': '.diamond',
        'style': {
            'shape': 'diamond'
        }
    }
])





# define colors 
colors = {
    'text': '#e1e1e3',
    'background': '#030324',
    'plotBackground': '#ffffff',
    'plotText': '#eeffb7',
    'headerBackground': '#000000',#'#14113f',
    'line': '#fc810f',
    'line_fill': '#dddddb',
    'topHeader': '#800f0f',
    'secondHeader': '#fffbd3'
}



fontFamily = 'Oswald'




# loading dataframe
df_ufc_total = pd.read_csv('ufcdata/data.csv', parse_dates=['date'])

year_list = df_ufc_total.date.dt.year.unique()
weight_class_list = list(df_ufc_total.weight_class.value_counts().index)

# loading most frequent weight class 
with open('ufcdata/most_frequent_weight_class.json', 'r') as f:
    fighter_weight_class_most_frequent = json.load(f)


def get_nodes_edges(df_partial):
    nodes = [
    {
        'data': {'id': fighter_name, 'label': fighter_name},
        'classes': w_class_color_map[fighter_weight_class_most_frequent[fighter_name]]
    }
    if fighter_name!="Jon Jones" else 
    {
        'data': {'id': fighter_name, 'label': fighter_name, 'url': "https://www.gameonlivesports.com.au/TeamLogo/JONES_JON.png"},
        'classes': 'jonjones'
    }
    for fighter_name in np.unique(np.concatenate([df_partial.R_fighter, df_partial.B_fighter]))]

    edges = [
    {'data': {'source': r_fighter, 'target': b_fighter,
              'df_ix': ix}} 
    if winner=='Red' else {'data': {'source': b_fighter, 'target': r_fighter,
              'df_ix': ix}}
    for r_fighter, b_fighter, winner, ix in zip(df_partial.R_fighter, df_partial.B_fighter, df_partial.Winner, df_partial.index)]

    return nodes + edges


app = dash.Dash("UFC graph")

app.layout = html.Div([


    html.Div([

    # Row 1: Header

        html.Div([

                    html.Div([      
                        html.H3('All UFC fights in one graph', style={'color':  colors['topHeader'],
                            'textAlign': 'center', 'fontSize': 54, 'font-family': fontFamily}),
                        html.H4('Exploring UFC stats', style={'color':  colors['secondHeader'],
                            'textAlign': 'center', 'font-family': fontFamily},),
                        ], style={'backgroundColor': colors['headerBackground'], 'align': 'center'}),

                ], style={'backgroundColor': colors['headerBackground'], 'align': 'center'}),

        html.Br([], style={'lineHeight': 5}),

        html.H5('UFC Graph:', style={'color':  colors['text'],
                            'textAlign': 'center'},),

            dcc.Dropdown(
            id='dropdown-year',
            value=[year_list[0]],
            multi=True,
            options=[
                {'label': str(year), 'value': year}
                for year in year_list],
            style={'margin': 'auto', 'width': '60%'},
            ),

            dcc.Dropdown(
            id='dropdown-weight-class',
            #value=[weight_class_list[0]],
            multi=True,
            #options=[
            #    {'label': w_class, 'value': w_class}
            #    for w_class in weight_class_list],
            style={'margin': 'auto', 'width': '60%'},
            ),

            dcc.Dropdown(
            id='dropdown-update-layout',
            value='cose',
            options=[
                {'label': name.capitalize(), 'value': name}
                for name in ['cose', 'breadthfirst', 'circle', 'grid', 'random', 'concentric']],
            style={'margin': 'auto', 'width': '40%'},
            ),

            html.Br([], style={'lineHeight': 3}),

        html.Div([
            html.Div([


            cyto.Cytoscape(
            id='cytoscape-ufc-graph',
            layout={'name': 'cose'},
            style={'margin': 'auto', 'maxWidth': '100%', 'height': '750px',
                    'backgroundColor': colors['plotBackground']},
            #stylesheet=my_stylesheet,
            minZoom=0.1,
            maxZoom=10
            ),
            ], style={'margin': 'auto'}, className='nine columns'),

        html.Div([

                dcc.Markdown(id='cytoscape-tapNodeData-output'),

                html.A(id='youtube-link', target='_blank'),


                dcc.Markdown(id='cytoscape-tapEdgeData-output'),

                ], style={'margin': 'auto', 'color':  colors['secondHeader'],
                           'font-family': "Roboto"}, className='three columns')


        ], className="row"),


        html.Br([], style={'lineHeight': 5}),



        html.Div([
            ],
            style={'margin': 'auto'}
            ),

        html.Br([], style={'lineHeight': 5}),

        html.Br([], style={'lineHeight': 50}),

        html.Br([], style={'lineHeight': 50}),

        html.Div([
            html.P("""This app is developed by DataQubit.com.""",
                                        style={'textAlign': 'center', 'color':  colors['text']})],
            style={'margin': 'auto'}
            ),

        html.Br([], style={'lineHeight': 5})



    ], 
    style={'backgroundColor': colors['background'], 'margin': 'auto', 'width': '80%'})

],
style={'backgroundColor': '#cfcfcf'})

##### CALLBACK FUNCTIONS #####

## UPDATE DEPENDENT DROPDOWNS

@app.callback(
    [dash.dependencies.Output('dropdown-weight-class', 'value'),
    dash.dependencies.Output('dropdown-weight-class', 'options')],
    [dash.dependencies.Input('dropdown-year', 'value')])
def update_weight_class_list(selected_years):
    options = [{'label': i, 'value': i} 
    for i in df_ufc_total[(df_ufc_total.date.dt.year.isin(selected_years))].weight_class.value_counts().index]
    if len(options)==0:
        return [None, options]
    return [[options[0]['value']], options]


## update stylesheet
@app.callback(Output('cytoscape-ufc-graph', 'stylesheet'),
              [Input('cytoscape-ufc-graph', 'tapNode')])
def generate_stylesheet(node):
    if not node:
        return my_stylesheet

    stylesheet = [{
            "selector": 'node[id = "{}"]'.format(node['data']['id']),
            "style": {
                'background-color': 'lightgreen',
                "border-color": "black",
                "border-width": 2,
                "border-opacity": 1,
                "opacity": 1,
    
                "label": "data(label)",
                "color": "darkblue",
                "text-opacity": 1,
                "font-size": 27,
                'z-index': 9999}
            }]

    for edge in node['edgesData']:
        stylesheet.append({
                "selector": 'edge[id= "{}"]'.format(edge['id']),
                "style": {
                    "line-color": "lightgreen",
                    'opacity': 1.0,
                    'z-index': 5000
                }
            })

    return my_stylesheet + stylesheet

## Regular Callback Functions

@app.callback(Output('cytoscape-ufc-graph', 'layout'),
              [Input('dropdown-update-layout', 'value')])
def update_layout(layout):
    return {
        'name': layout,
        'animate': True,
        'fit': True
    }

@app.callback(Output('cytoscape-ufc-graph', 'elements'),
              [Input('dropdown-year', "value"),
               Input('dropdown-weight-class', "value")
              ],
              [State('cytoscape-ufc-graph', 'elements')])
def update_ufc_graph(years, w_classes, elements):
    if w_classes is None:
        w_classes = []

    elements = get_nodes_edges(df_ufc_total[(df_ufc_total.date.dt.year.isin(years)) & (df_ufc_total.weight_class.isin(w_classes))])
    return elements

@app.callback([Output('youtube-link', 'children'),
            Output('youtube-link', 'href'),
            Output('cytoscape-tapEdgeData-output', 'children')],
            [Input('cytoscape-ufc-graph', 'tapEdgeData')])
def displayTapEdgeData(data):
    if data:
        fight_dict = dict(df_ufc_total.loc[data['df_ix']][fight_features])
        search_query = "%s and %s %d" %(fight_dict['R_fighter'], fight_dict['B_fighter'], fight_dict['date'].year)
        youtube_search = "https://www.youtube.com/results?search_query=%s" %('+'.join(search_query.split(' ')))
        return ['Search on YouTube', youtube_search, 
                "\n* " + "\n* ".join([feat_name + ' : ' + str(feat) if feat_name!="date" else feat_name + ' : ' + str(feat.date())
                     for feat_name, feat in fight_dict.items()])]
    return [None, None, None]

@app.callback(Output('cytoscape-tapNodeData-output', 'children'),
              [Input('cytoscape-ufc-graph', 'tapNodeData')])
def displayTapNodeData(data):
    if data:
        return data['label']

### Loading External CSS  ###  

external_css = [ "https://cdnjs.cloudflare.com/ajax/libs/normalize/7.0.0/normalize.min.css",
        "https://cdnjs.cloudflare.com/ajax/libs/skeleton/2.0.4/skeleton.min.css",
        #"//fonts.googleapis.com/css?family=Raleway", 
        "https://fonts.googleapis.com/css?family=Oswald",
        "https://fonts.googleapis.com/css?family=Roboto",# try Teko
        "https://codepen.io/plotly/pen/KmyPZr.css",
        "https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css",
        "https://codepen.io/chriddyp/pen/bWLwgP.css"
        ]

for css in external_css: 
    app.css.append_css({ "external_url": css })

if __name__ == '__main__':
    app.run_server(debug=True)