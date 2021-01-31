# Import libraries
import dash
import dash_table
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import pandas as pd
from datetime import datetime
import utils

# Load the dataset
events_df = pd.read_json('data/regen_event_list_ts.json', lines=True)
heavy_precipitation_events = events_df[events_df["si"] > 0.0]
normal_precipitation_events = events_df[events_df["si"] == 0.0]
ts_events_df = pd.read_json('data/regen_event_list_ts_expanded.json', lines=True)
heavy_precipitation_events_ts = ts_events_df[ts_events_df["si"] > 0.0]
normal_precipitation_events_ts = ts_events_df[ts_events_df["si"] == 0.0]
stats_table = utils.get_stats(events_df, ts_events_df)

# Create the Dash app
external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"
                "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title = "Gummistiefel B: Temporal analysis of heavy precipitation events"

# Set up the app layout
app.layout = html.Div(children=[
    html.Div(
        children=[
            html.P(children="🌧️", className="header-emoji"),
            html.H1(
                children="Gummistiefel B", className="header-title"
            ),
            html.P(
                children="Temporal analysis of heavy precipitation events"
                " in Germany, Switzerland and Italy between 1979 and 2017",
                className="header-description",
            ),
        ],
        className="header",
    ),
    html.Div(
        children=[
            html.Div(
                children=[
                    dcc.Slider(
                        id="bin_size_slider",
                        min=1,
                        max=10,
                        step=1,
                        marks={
                            1: '1',
                            5: '5',
                            10: '10'
                        },
                        value=1
                    ),
                ],
                className="slider",
            ),
            html.Div(
                children=[
                    html.Div(children="Property", className="menu-title"),
                    dcc.Dropdown(
                        id="property_list",
                        options=[
                            {"label": prop, "value": prop}
                            for prop in ["si", "length", "area", "maxPrec", "meanPre"]
                        ],
                        value="si",
                        clearable=False,
                        className="dropdown",
                    ),
                ]
            ),
            html.Div(
                children=[
                    html.Div(children="Type", className="menu-title"),
                    dcc.Dropdown(
                        id="type_list",
                        options=[
                            {"label": prop, "value": prop}
                            for prop in ["All", "Heavy", "Normal"]
                        ],
                        value="Heavy",
                        clearable=False,
                        className="dropdown",
                    ),
                ]
            ),
            html.Div(
                children=[
                    html.Div(
                        children="Date Range", className="menu-title"
                    ),
                    dcc.DatePickerRange(
                        id="date_range",
                        min_date_allowed=events_df.datetime.min().date(),
                        max_date_allowed=events_df.datetime.max().date(),
                        start_date=events_df.datetime.min().date(),
                        end_date=events_df.datetime.max().date(),
                    ),
                ]
            ),
        ],
        className="menu",
    ),
    html.Div(
        children=[
            # html.Div(
            #     children=[
            #         dash_table.DataTable(
            #             id='stats_table',
            #             columns=[{"name": i, "id": i} for i in stats_table.columns],
            #             data=stats_table.to_dict("records"),
            #         ),
            #     ],
            #     className="card",
            # ),
            html.Div(
                children=[
                    dcc.Graph(
                        id='events_graph',
                        config={"displayModeBar": False},
                    ),
                ],
                className="card",
            ),
            html.Div(
                children=[
                    dcc.Graph(
                        id='property_graph',
                        config={"displayModeBar": False},
                    ),
                ],
                className="card",
            )
        ],
        className="wrapper",
    )
])


# Set up the callback function
@app.callback(
    # Output(component_id='stats_table', component_property='data'),
    Output(component_id='events_graph', component_property='figure'),
    Output(component_id='property_graph', component_property='figure'),
    Input(component_id='bin_size_slider', component_property='value'),
    Input(component_id='property_list', component_property='value'),
    Input(component_id='type_list', component_property='value'),
    Input(component_id='date_range', component_property='start_date'),
    Input(component_id='date_range', component_property='end_date'),
)
def update_graphs(bin_size, prec_property, prec_type, start_date, end_date):
    heavy_precipitation_filter = True if prec_type == "Heavy" else False
    filtered_df = events_df[events_df["si"] > 0.0] if heavy_precipitation_filter else events_df
    filtered_ts_df = ts_events_df[ts_events_df["si_ev"] > 0.0] if heavy_precipitation_filter else ts_events_df
    start_date_dt = datetime.combine(datetime.strptime(start_date, '%Y-%m-%d'), datetime.min.time())
    end_date_dt = datetime.combine(datetime.strptime(end_date, '%Y-%m-%d'), datetime.max.time())
    mask = (
        (filtered_df["datetime"] >= start_date_dt)
        & (filtered_df["datetime"] <= end_date_dt)
    )
    ts_mask = (
            (filtered_ts_df["datetime"] >= start_date_dt)
            & (filtered_ts_df["datetime"] <= end_date_dt)
    )
    filtered_df = filtered_df.loc[mask, :]
    filtered_ts_df = filtered_ts_df.loc[ts_mask, :]

    filtered_stats_table = utils.get_stats(filtered_df, filtered_ts_df).to_dict(orient="records")
    events_graph = utils.get_stacked_histogram(events_df, bin_size=bin_size)
    if prec_property in ["maxPrec", "meanPre"]:
        property_graph = utils.get_histogram(filtered_ts_df, bin_size=bin_size, column_name=prec_property,
                                             hist_func="avg")
    else:
        property_graph = utils.get_histogram(filtered_df, bin_size=bin_size, column_name=prec_property,
                                             hist_func="avg")
    # return filtered_stats_table, events_graph, property_graph
    return events_graph, property_graph


# Run local server
if __name__ == '__main__':
    app.run_server(debug=True)
