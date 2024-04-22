# %% [markdown]
# ## BUILT LAYOUT

# %%
# import dependencies

from dash import Dash, html, dcc, Input, Output, callback, dash_table
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
from dash import dash_table as dt
import dash_bootstrap_components as dbc

# %%
# reading in my data
df = pd.read_csv('data.csv')

# %%
df.head()

# %%
stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css'] # load the CSS stylesheet

app = Dash(__name__, external_stylesheets=[dbc.themes.MINTY]) # initialize the app with my theme (green because Spotify)
server = app.server

# %%
# creating these variables to reference later in my code
genres = df.track_genre.unique().tolist()
num_columns = ['danceability', 'energy', 'key', 'loudness', 'speechiness', 'acousticness', 'instrumentalness', 'valence', 'tempo', 'time_signature']
artist_options = ['Olivia Rodrigo', 'Taylor Swift', 'Billie Eilish', 'Frank Ocean', 'Blondie', 'Lana Del Rey', 'Coldplay', 'Weezer']
blank_space = html.Div(style={'height': '50px'})
colors = ['#ABEBC6', '#82E0AA','#58D68D', '#2ECC71', '#28B463', '#239B56', '#1D8348' ]

app.layout = html.Div([
    html.Div(
        className="app-header",
        children=[
            html.Div("Mary Duffner's Spotify Dashboard", className="app-header--title") # creating the title of the page 
        ], style={'width': '48%', 'margin' : '10px'}
    ),
    html.Div(style={'height': '10px'}),
    html.Div([
        html.A(
            dbc.Button("Open Spotify", color="primary", className="mr-1"),
            href="https://www.spotify.com/", # button allowing user to go to Spotify website
            target="_blank",
        )
    ], style={'margin' : '10px'}),
    html.Div(style={'height': '10px'}),
    html.Div([
        html.A(
            dbc.Button("Open Github Repo", color="primary", className="mr-1"),
            href="https://github.com/maryduffner/Final-Project.git", # button linking to my GitHub
            target="_blank",
        )
    ], style={'margin' : '10px'}),
    html.Div(style={'height': '15px'}),
    html.Div(
        children=html.Div([
            html.H1('Spotify Data Center: Get to Know the Numbers Behind the Songs'), # header for our overview below
            html.Div('''
                This dashboard is an interactive interface
                     allowing users to learn more about their favorites of Spotify. The data of over 125 genres
                     was scraped from Spotify to provide useful insight on various artists, songs, and statistics behind the composition. This app
                     is designed for the both casual listeners and music professionals to interact with Spotify data and get to know a bit more behind
                     many different genres, artists, and songs.  
            ''')
        ], style={'text-align': 'center','width': '100%', 'margin' : '10px'})
    ),
    html.Div(style={'height': '10px'}),
    html.Hr(), # line to space out the page a bit 
    html.Div('Select a genre to explore! Here you can discover 5 new artists or songs to add to your playlists.', style={'margin':'10px'}),
    html.Div([
        dcc.Dropdown(
            id="genre-dropdown",
            options=[{"label": st, "value": st} for st in df['track_genre'].unique()],
            placeholder="-Select a Genre-",
            multi=True,
            value=[],
        )
    ],style={'margin': '10px'}),
    html.Div([
        dash_table.DataTable(
            id="table-container",
            columns=[{"name": i, "id": i} for i in df.columns[:3]], # only showing first 3 columns 
            page_size= 10,
        )
    ], style={'margin': '10px'}),
    html.Div(id='datatable-interactivity-container'),
    html.Div(style={'height': '10px'}),
    html.Hr(),
    html.Div('Below, you may pick any two numerical categories to compare. Use the dropdown to select genres and see how genres differ based on the variables selected.', style={'margin':'10px'}),
    html.Div([
        dcc.RadioItems(
                num_columns,
                'danceability',
                id='yaxis-column',
                inline=True, # makes them horizontally inline with each other 
                labelStyle={'display': 'block', 'margin-bottom': '2px'} # spacing out the radio buttons a bit
            )
    ],style={'width': '48%', 'display': 'inline-block', 'margin' : '10px'}),
    html.Div([
      dcc.RadioItems(
                num_columns,
                'energy',
                id='xaxis-column',
                inline=True, 
                labelStyle={'display': 'block', 'margin-bottom': '2px'}
            )
    ],style={'width': '48%', 'display': 'inline-block', 'margin' : '10px'}),
    html.Div([
        dcc.Dropdown(
            id='group-by-dropdown',
            options=[{'label': col, 'value': col} for col in df['track_genre'].unique()],
            value=['acoustic'],
            multi=True,
        )
    ],style={'width': '98%','margin':'10px'}),
    dcc.Graph(id='numeric-graphic'),
    html.Hr(),
    html.Div('Please select an artist from the dropdown, then any of their songs to compare popularity of their tracks.', style={'margin':'10px'}),
    html.Div([
        dcc.Dropdown(
            artist_options,
            'Billie Eilish',
            id='Artist-dropdown',
        )
    ],style={'width': '48%', 'display': 'inline-block', 'margin' : '10px'}),
    html.Div([
        dcc.Dropdown(
            id='track-dropdown',
            options=[],
            placeholder="-Select a Track-",
            multi=True,
            value=[],
        )
    ],style={'width': '48%', 'display': 'inline-block', 'margin' : '10px'}),  
    dcc.Graph(id='artist-graph')
])


@app.callback( # creating my callbacks for my 2 interactive graphs...was getting an error with mutliple callbacks so combined into one large one
    [Output("table-container", "data"),
     Output('numeric-graphic', 'figure'),
     Output('track-dropdown', 'options'),
     Output('track-dropdown', 'value'),
     Output('artist-graph', 'figure')],
    [Input("genre-dropdown", "value"),
     Input('yaxis-column', 'value'),
     Input('xaxis-column', 'value'),
     Input('group-by-dropdown', 'value'),
     Input('Artist-dropdown', 'value'),
     Input('track-dropdown', 'value')],
     allow_duplicate=True, # allowing there to be duplicated in my outputs 
     prevent_initial_call='initial_duplicate' # prevent callback from firing before user inserts their selections 
)
def update_data_and_graph(selected_genres, yaxis_column_name, xaxis_column_name, selected_genres_graph, selected_artist, selected_tracks):
    if not selected_genres:
        table_data = [] # making sure my selected genres fall within the options
    else:
        filtered_data = pd.concat([df[df['track_genre'] == genre].sample(5) for genre in selected_genres]) # showing 5 rows for each genre selected 
        table_data = filtered_data.to_dict("records") # making a dictionary for my table

    if not selected_genres_graph:
        indicator_graph_figure = {'data': [], 'layout': {}} # output if not in our graph options
    else:
        indicator_graph_figure = px.scatter(df[df['track_genre'].isin(selected_genres_graph)], x=xaxis_column_name, y=yaxis_column_name, color='track_genre',
                                            color_discrete_sequence=colors, # colors defined at beginning to be on theme
                                            labels={'x': xaxis_column_name, 'y': yaxis_column_name})
        indicator_graph_figure.layout.plot_bgcolor = '#686C6A' # making background of graphs darker 
         
    track_dropdown_options = [{'label': i, 'value': i} for i in df[df['artists'] == selected_artist]['track_name']] # assigning the tracks from each selected artist
    track_dropdown_value = selected_tracks # assigning the dropdown of tracks to the selected tracks 
    
    if not selected_tracks:
        artist_graph_figure = {'data': [], 'layout': {}} # making sure the selected options are within the given values to then show graph
    else:
        filtered_df = df[(df['artists'] == selected_artist) & (df['track_name'].isin(selected_tracks))] # making sure each option is in the options presented to user
        artist_graph_figure = px.bar(filtered_df, x='track_name', y='popularity', color='track_name', color_discrete_sequence=colors)
        artist_graph_figure.layout.plot_bgcolor = '#686C6A' # making background of graph dark (match theme)
    
    
    return table_data, indicator_graph_figure, track_dropdown_options, track_dropdown_value, artist_graph_figure

if __name__ == "__main__":
    app.run_server(jupyter_mode = 'tab', debug=True)


