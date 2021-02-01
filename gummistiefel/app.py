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

# Get options and range
si_min = 0  # float(min(events_df["si"].min(), ts_events_df["si"].min()))
si_max = float(max(events_df["si"].max(), ts_events_df["si"].max()))
length_min = int(ts_events_df["length"].min())
length_max = int(ts_events_df["length"].max())
area_min = 0  # float(ts_events_df["area"].min())
area_max = float(ts_events_df["area"].max())
min_date = events_df.datetime.min().date()
max_date = events_df.datetime.max().date()

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
                    html.Div(children="Bin size", className="menu-title"),
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
                        value=1,
                        tooltip={"always_visible": True, "placement": "right"}
                    ),
                ],
                className="slider",
            )
        ],
        className="menu",
    ),
    html.Div(
        children=[
            html.Div(
                children=[
                    html.Div(children="SI range", className="menu-title"),
                    dcc.RangeSlider(
                        id="si_range_slider",
                        min=si_min,
                        max=si_max,
                        step=0.1,
                        marks={
                            si_min: f'{si_min}',
                            si_max: f'{si_max}'
                        },
                        value=[si_min, si_max],
                        tooltip={"always_visible": True, "placement": "right"}
                    ),
                ],
                className="slider",
            )
        ],
        className="menu",
    ),
    html.Div(
        children=[
            html.Div(
                children=[
                    html.Div(children="Length range", className="menu-title"),
                    dcc.RangeSlider(
                        id="length_range_slider",
                        min=length_min,
                        max=length_max,
                        step=1,
                        marks={
                            length_min: f'{length_min}',
                            length_max: f'{length_max}'
                        },
                        value=[length_min, length_max],
                        tooltip={"always_visible": True, "placement": "right"}
                    ),
                ],
                className="slider",
            )
        ],
        className="menu",
    ),
    html.Div(
        children=[
            html.Div(
                children=[
                    html.Div(children="Area range", className="menu-title"),
                    dcc.RangeSlider(
                        id="area_range_slider",
                        min=area_min,
                        max=area_max,
                        step=0.1,
                        marks={
                            area_min: f'{area_min}',
                            area_max: f'{area_max}'
                        },
                        value=[area_min, area_max],
                        tooltip={"always_visible": True, "placement": "right"}
                    ),
                ],
                className="slider",
            )
        ],
        className="menu",
    ),
    html.Div(
        children=[
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
                            for prop in ["All", "Heavy"]
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
                children=[dcc.Graph(id='events_graph')],
                className="card",
            ),
            html.Div(
                children=[dcc.Graph(id='rose_graph')],
                className="card",
            ),
            html.Div(
                children=[dcc.Graph(id='property_graph')],
                className="card",
            ),
            html.Div(
                children=[dcc.Graph(id='box_graph')],
                className="card",
            ),
            html.Div(
                children=[dcc.Graph(id='map_graph')],
                className="card",
            ),
        ],
        className="wrapper",
    )
])


# Set up the callback function
# TODO maybe use State instead of Input and use Button to initiate update
@app.callback(
    [
        # Output(component_id='stats_table', component_property='data'),
        Output(component_id='events_graph', component_property='figure'),
        Output(component_id='rose_graph', component_property='figure'),
        Output(component_id='property_graph', component_property='figure'),
        Output(component_id='box_graph', component_property='figure'),
        Output(component_id='map_graph', component_property='figure'),
    ],
    [
        Input(component_id='bin_size_slider', component_property='value'),
        Input(component_id='si_range_slider', component_property='value'),
        Input(component_id='length_range_slider', component_property='value'),
        Input(component_id='area_range_slider', component_property='value'),
        Input(component_id='property_list', component_property='value'),
        Input(component_id='type_list', component_property='value'),
        Input(component_id='date_range', component_property='start_date'),
        Input(component_id='date_range', component_property='end_date')
    ]
)
def update_graphs(bin_size,
                  si_range, length_range, area_range,
                  prec_property, prec_type, start_date, end_date):
    heavy_precipitation_filter = True if prec_type == "Heavy" else False
    filtered_df = events_df[events_df["si"] > 0.0] if heavy_precipitation_filter else events_df
    filtered_ts_df = ts_events_df[ts_events_df["si_ev"] > 0.0] if heavy_precipitation_filter else ts_events_df
    start_date_dt = datetime.combine(datetime.strptime(start_date, '%Y-%m-%d'), datetime.min.time())
    end_date_dt = datetime.combine(datetime.strptime(end_date, '%Y-%m-%d'), datetime.max.time())
    mask = (
            (filtered_df["datetime"] >= start_date_dt)
            & (filtered_df["datetime"] <= end_date_dt)
            & (filtered_df["si"] >= si_range[0])
            & (filtered_df["si"] <= si_range[1])
            & (filtered_df["length"] >= length_range[0])
            & (filtered_df["length"] <= length_range[1])
            & (filtered_df["area"] >= area_range[0])
            & (filtered_df["area"] <= area_range[1])
    )
    ts_mask = (
            (filtered_ts_df["datetime"] >= start_date_dt)
            & (filtered_ts_df["datetime"] <= end_date_dt)
            & (filtered_ts_df["si_ev"] >= si_range[0])
            & (filtered_ts_df["si_ev"] <= si_range[1])
            & (filtered_ts_df["length"] >= length_range[0])
            & (filtered_ts_df["length"] <= length_range[1])
            & (filtered_ts_df["area"] >= area_range[0])
            & (filtered_ts_df["area"] <= area_range[1])
    )
    filtered_df = filtered_df.loc[mask, :]
    filtered_ts_df = filtered_ts_df.loc[ts_mask, :]

    u_events_graph = utils.get_stacked_histogram(filtered_df, bin_size=bin_size)
    u_events_graph.update_layout(title=f"Number of {prec_type.lower()} precipitation events (bin size: {bin_size})")
    u_rose_graph = utils.get_rose_chart(filtered_df)
    filtered_stats_table = utils.get_stats(filtered_df, filtered_ts_df).to_dict(orient="records")

    if prec_property in ["maxPrec", "meanPre"]:
        u_property_graph = utils.get_histogram(filtered_ts_df, bin_size=bin_size, column_name=prec_property,
                                               hist_func="avg")
    else:
        u_property_graph = utils.get_histogram(filtered_df, bin_size=bin_size, column_name=prec_property,
                                               hist_func="avg")
    u_property_graph.update_layout(title=f"Average {prec_property} of {prec_type.lower()} precipitation events")
    u_box_graph = utils.get_boxplots(filtered_df, filtered_ts_df)
    u_box_graph.update_layout(title="Distribution of precipitation events")
    u_map_graph = utils.get_extreme_events_on_map(filtered_ts_df)  # specify col or keep default?
    return u_events_graph, u_rose_graph, u_property_graph, u_box_graph, u_map_graph
    # return filtered_stats_table, u_events_graph, u_property_graph, u_map_graph


# Run local server
if __name__ == '__main__':
    app.run_server(debug=True)
