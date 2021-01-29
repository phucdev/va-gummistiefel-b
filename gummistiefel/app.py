# Import libraries
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import utils

# Load the dataset
events_df = pd.read_json('data/regen_event_list_ts.json', lines=True)
heavy_precipitation_events = events_df[events_df["si"] > 0.0]
normal_precipitation_events = events_df[events_df["si"] == 0.0]
ts_events_df = pd.read_json('data/regen_event_list_ts_expanded.json', lines=True)
heavy_precipitation_events_ts = ts_events_df[ts_events_df["si"] > 0.0]
normal_precipitation_events_ts = ts_events_df[ts_events_df["si"] == 0.0]

# Create the Dash app
app = dash.Dash()

# Set up the app layout
app.layout = html.Div(children=[
    html.H1(children='Gummistiefel B Dashboard'),
    dcc.Slider(
        id="bin_size_slider",
        min=1,
        max=10,
        step=1,
        marks={
            1: '1',
            3: '3',
            5: '5',
            10: '10'
        },
        value=1
    ),
    dcc.Graph(id='events_graph')
])


# Set up the callback function
@app.callback(
    Output(component_id='events_graph', component_property='figure'),
    Input(component_id='bin_size_slider', component_property='value')
)
def update_graph(bin_size):
    return utils.get_stacked_histogram(events_df, bin_size=bin_size)


# Run local server
if __name__ == '__main__':
    app.run_server(debug=True)
