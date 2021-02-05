from typing import List

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import scipy.stats
import math

months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
          "November", "December"]

lat_min = 34.9099998474
lat_max = 56.4199981689
long_min = 2.6099998951
long_max = 20.9799995422


def get_ceil_with_digits(num, digits=0):
    assert digits >= 0, "The number of decimals to use when rounding the number. Has to be >= 0."
    float_num = float(num)
    float_num = math.ceil(float_num*(10**digits))/(10**digits)
    return float(float_num)


def mean_confidence_interval(data, confidence=0.95):
    a = 1.0 * np.array(data)
    n = len(a)
    m, se = np.mean(a), scipy.stats.sem(a)
    h = se * scipy.stats.t.ppf((1 + confidence) / 2., n - 1)
    return m, m - h, m + h


def get_grouped_events(df):
    return pd.DataFrame(df.groupby(["year"]).id.count().reset_index(name='events')) \
        .sort_values(["year"], ascending=True)


def get_time_frame(df, start: int = None, end: int = None):
    time_frame = df
    if start:
        time_frame = time_frame[time_frame["year"] >= start]
    if end:
        time_frame = time_frame[time_frame["year"] <= end]
    return time_frame


def get_stacked_histogram(df, bin_size=1):
    heavy_precipitation_events = df[df["si"] > 0.0]
    normal_precipitation_events = df[df["si"] == 0.0]

    fig = go.Figure()
    if len(normal_precipitation_events) > 0:
        fig.add_trace(go.Histogram(
            name="Normal precipitation events",
            x=list(normal_precipitation_events["year"]),
            histfunc="count",
            autobinx=False,
            opacity=0.75,
            xbins=dict(
                start=min(list(normal_precipitation_events["year"])),
                end=max(list(normal_precipitation_events["year"]))+1,
                size=bin_size),
            marker=dict(color="blue")
        )),
    fig.add_trace(go.Histogram(
        name="Heavy precipitation events",
        x=list(heavy_precipitation_events["year"]),
        histfunc="count",
        autobinx=False,
        opacity=0.75,
        xbins=dict(
            start=min(list(heavy_precipitation_events["year"])),
            end=max(list(heavy_precipitation_events["year"]))+1,
            size=bin_size),
        marker=dict(color="red")
    ))

    if len(normal_precipitation_events) > 0:
        # The two histograms are drawn on top of another
        fig.update_layout(barmode='relative')
    return fig


def get_histogram(df, column_name="si", heavy_precipitation_filter=False, bin_size=1):
    if column_name:
        assert column_name in df, f"{column_name} not in df"
    filtered_df = df
    if heavy_precipitation_filter:
        filtered_df = filtered_df[filtered_df["si"] > 0.0]
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=[
            f"Average {column_name}",
            f"Max {column_name}"
        ]
    )
    max_filtered_df = filtered_df.loc[filtered_df.groupby("year")["si"].idxmax()]
    fig.add_trace(
        go.Histogram(
            name=f"avg {column_name}",
            x=list(filtered_df["year"]),
            y=list(filtered_df[column_name]),
            histfunc="avg",
            autobinx=False,
            opacity=0.75,
            xbins=dict(
                start=min(list(filtered_df["year"])),
                end=max(list(filtered_df["year"]))+1,
                size=bin_size),
        ),
        row=1, col=1
    )
    fig.add_trace(
        go.Histogram(
            name=f"max {column_name}",
            x=list(max_filtered_df["year"]),
            y=list(max_filtered_df[column_name]),
            histfunc="max",
            autobinx=False,
            opacity=0.75,
            xbins=dict(
                start=min(list(max_filtered_df["year"])),
                end=max(list(max_filtered_df["year"]))+1,
                size=bin_size),
        ),
        row=1, col=2
    )
    # TODO add trend line?
    return fig


def get_rose_chart_data(df):
    heavy_precipitation_events = df[df["si"] > 0.0]
    normal_precipitation_events = df[df["si"] == 0.0]
    heavy_data = pd.DataFrame(
        heavy_precipitation_events.groupby(['month']).id.count().reset_index(name='events')
    ).set_index("month")
    normal_data = pd.DataFrame(
        normal_precipitation_events.groupby(['month']).id.count().reset_index(name='events')
    ).set_index("month")
    for i in range(len(months)):
        month = i+1
        if month not in heavy_data.index:
            heavy_data.loc[month] = {"events": 0}
        if month not in normal_data.index:
            normal_data.loc[month] = {"events": 0}
    heavy_data.sort_values(["month"], ascending=True, inplace=True)
    normal_data.sort_values(["month"], ascending=True, inplace=True)

    heavy_data["month_str"] = months
    reversed_num_of_events_heavy = heavy_data.sort_values(["month"], ascending=False)
    normal_data["month_str"] = months
    reversed_num_of_events_normal = normal_data.sort_values(["month"], ascending=False)
    return reversed_num_of_events_normal, reversed_num_of_events_heavy


def get_bar_polar(num_of_events_normal, num_of_events_heavy):
    normal_barpolar = None
    if len(num_of_events_normal) > 0:
        normal_barpolar = go.Barpolar(
            r=list(num_of_events_normal["events"]),
            theta=num_of_events_normal["month_str"],
            name="Number of normal precipitation events",
            marker=dict(
                color="blue",
                line_color="black"
            ),
            hoverinfo=["all"],
            opacity=0.75
        )
    heavy_barpolar = go.Barpolar(
        r=list(num_of_events_heavy["events"]),
        theta=num_of_events_heavy["month_str"],
        name="Number of heavy precipitation events",
        marker=dict(
            color="red",
            line_color="black"
        ),
        hoverinfo=["all"],
        opacity=0.75
    )
    return normal_barpolar, heavy_barpolar


def get_max_radius(df):
    num_of_events_normal, num_of_events_heavy = get_rose_chart_data(df)
    max_radius = max(num_of_events_heavy["events"])
    if num_of_events_normal is not None and len(num_of_events_normal) > 0:
        max_radius_n = max(num_of_events_normal["events"])
        if not math.isnan(max_radius_n):
            max_radius += max_radius_n
    return max_radius


def get_rose_chart(df, max_radius=None):
    num_of_events_normal, num_of_events_heavy = get_rose_chart_data(df)
    normal_barpolar, heavy_barpolar = get_bar_polar(num_of_events_normal, num_of_events_heavy)

    fig = go.Figure()
    if normal_barpolar is not None:
        fig.add_trace(normal_barpolar)
    fig.add_trace(heavy_barpolar)

    if not (max_radius and type(max_radius) == int):
        max_radius = get_max_radius(df)
    fig.update_layout(
        polar=dict(
            bgcolor="rgb(223,223,223)",
            angularaxis=dict(
                linewidth=3,
                showline=True,
                linecolor='black',
                rotation=90
            ),
            radialaxis=dict(
                showline=True,
                linewidth=2,
                gridcolor="white",
                gridwidth=2,
                range=(0, max_radius),
            )
        )
    )
    return fig


def get_line_plot(df, column_name):
    grouped_df = df.groupby(["year"])[column_name].apply(list)
    years = grouped_df.index
    cd_array = [np.array(e) for e in grouped_df.values]
    mci = np.array([mean_confidence_interval(e) for e in cd_array])
    means = mci[:, 0]
    ci_lower = mci[:, 1]
    ci_upper = mci[:, 2]
    fig = go.Figure([
        go.Scatter(
            name=f"{column_name} Mean",
            x=years,
            y=means,
            line=dict(color='rgb(0,100,80)'),
            mode='lines'
        ),
        go.Scatter(
            name="Upper Bound",
            x=years,
            y=ci_upper,
            mode='lines',
            marker=dict(color="#444"),
            line=dict(width=0),
            showlegend=False
        ),
        go.Scatter(
            name="Lower Bound",
            x=years,
            y=ci_lower,
            marker=dict(color="#444"),
            line=dict(width=0),
            mode='lines',
            fillcolor='rgba(68, 68, 68, 0.3)',
            fill='tonexty',
            showlegend=False
        )
    ])
    return fig


def get_event_on_map(df, column_name="si", event_ids: List[int] = None, scaling_factor: int = 5):
    filtered_df = df
    if event_ids:
        filtered_df = filtered_df[filtered_df["id"].isin(event_ids)]
    fig = go.Figure(data=go.Scattergeo(
        lon=filtered_df['lonMax'],
        lat=filtered_df['latMax'],
        text=filtered_df['si'],
        mode='markers',
        marker=dict(
            size=filtered_df['area'] * scaling_factor,
            opacity=0.8,
            reversescale=True,
            autocolorscale=False,
            colorscale='Blues_r',
            cmin=0,
            color=filtered_df[column_name],
            cmax=filtered_df[column_name].max(),
            colorbar_title=f"{column_name}"
        )
    ))

    fig.update_layout(
        title=f'Heavy precipitation events ({column_name})',
        geo_scope='europe',
        geo=dict(
            # Add coordinates limits on a map
            lataxis=dict(range=[lat_min, lat_max]),
            lonaxis=dict(range=[long_min, long_max])
        )
    )
    return fig


def get_extreme_events_on_map(df, column_name="si", scaling_factor: int = 5):
    df_copy = df.copy()
    df_copy["text"] = df_copy["id"].astype(str) + " si(" + df_copy["si"].astype(str) + "), length(" \
                      + df_copy["length"].astype(str) + "), area(" + df_copy["area"].astype(str) + ")"
    max_si_event_id, max_si = get_max_id(df_copy, "si_ev", return_value=True)
    max_length_event_id, max_length = get_max_id(df_copy, "length", return_value=True)
    max_area_event_id, max_area = get_max_id(df_copy, "area", return_value=True)
    fig = make_subplots(
        rows=1, cols=3,
        specs=[[{"type": "scattergeo"}, {"type": "scattergeo"}, {"type": "scattergeo"}]],
        subplot_titles=[
            "Event with max si of {:.3f}".format(max_si),
            "Event with max length of {}".format(max_length),
            "Event with max area of {:.3f}".format(max_area)
        ],
    )
    event_ids = [max_si_event_id, max_length_event_id, max_area_event_id]
    geo_dict = dict(
        scope="europe",
        # Add coordinates limits on a map
        lataxis=dict(range=[lat_min, lat_max]),
        lonaxis=dict(range=[long_min, long_max])
    )

    for i, event_id in enumerate(event_ids):
        filtered_df = df_copy[df_copy["id"].isin([event_id])]
        fig.add_trace(
            go.Scattergeo(
                lon=filtered_df['lonMax'],
                lat=filtered_df['latMax'],
                text=filtered_df['text'],
                mode='markers',
                marker=dict(
                    size=filtered_df['area'] * scaling_factor,
                    opacity=0.8,
                    color=filtered_df[column_name],
                    coloraxis="coloraxis"
                ),
                geo=f"geo{i + 1}"
            ),
            row=1, col=i + 1
        )
    fig.update_layout(
        title=f'Extreme precipitation events',
        coloraxis=dict(
            reversescale=True,
            autocolorscale=False,
            colorscale='Blues_r',
            cmin=0,
            cmax=df_copy[column_name].max(),
            colorbar_title=f"{column_name}"
        ),
        showlegend=False,
        geo=geo_dict,
        geo2=geo_dict,
        geo3=geo_dict
    )
    return fig


def get_boxplot(df, column_name):
    fig = go.Figure()
    fig.add_trace(
        go.Box(y=list(df[column_name]), name=column_name)
    )
    return fig


def get_boxplots(df, ts_df):
    df_copy = df.copy()
    ts_df_copy = ts_df.copy()
    df_copy["text"] = df["id"].astype(str) + " si(" + df["si"].astype(str) + "), length(" + df["length"].astype(str) \
                 + "), area(" + df["area"].astype(str) + ")"

    ts_df_copy["text"] = ts_df["id"].astype(str) + " si(" + ts_df["si"].astype(str) \
                    + "), length(" + ts_df["length"].astype(str) + "), area(" + ts_df["area"].astype(str) + ")"
    fig = make_subplots(rows=1, cols=5)
    fig.add_trace(
        go.Box(y=list(df_copy["si"]), name="si (event)", text=df_copy["text"]), row=1, col=1
    )
    fig.add_trace(
        go.Box(y=list(ts_df_copy["si"]), name="si (timeseries)", text=ts_df_copy["text"]), row=1, col=2
    )
    fig.add_trace(
        go.Box(y=list(df_copy["length"]), name="length", text=df_copy["text"]), row=1, col=3
    )
    fig.add_trace(
        go.Box(y=list(df_copy["area"]), name="area", text=df_copy["text"]), row=1, col=4
    )
    fig.add_trace(
        go.Box(y=list(ts_df_copy["meanPre"]), name="meanPre", text=ts_df_copy["text"]), row=1, col=5
    )
    return fig


def get_max_id(df, column_name, return_value=False):
    assert column_name in df, f"{column_name} not in df"
    max_event = df.iloc[df[column_name].argmax()]
    if return_value:
        return max_event["id"], max_event[column_name]
    else:
        return max_event["id"]


def get_stats(df, ts_df, heavy_precipitation_filter=False, use_si_ev=True):
    # expect a df with timeseries
    filtered_df: pd.DataFrame = df
    filtered_ts_df: pd.DataFrame = ts_df
    if heavy_precipitation_filter:
        filtered_df = df[df["si"] > 0]
        filter_category = "si_ev" if use_si_ev else "si"
        filtered_ts_df = ts_df[ts_df[filter_category] > 0]

    delta = df["datetime"].max() - df["datetime"].min()
    num_of_days = delta.days
    num_of_events = len(filtered_df)
    num_of_ts_events = len(filtered_ts_df)

    si_sum = filtered_df["si"].sum()
    si_ts_sum = filtered_ts_df["si"].sum()
    si_per_day = 0 if num_of_days <= 0 else si_sum / num_of_days
    si_per_event = 0 if num_of_days <= 0 else si_sum / num_of_events
    si_per_ts_event = 0 if num_of_days <= 0 else si_ts_sum / num_of_ts_events
    length_per_day = 0 if num_of_days <= 0 else filtered_df["length"].sum() / num_of_days
    length_per_event = 0 if num_of_days <= 0 else filtered_df["length"].sum() / num_of_events
    area_per_day = 0 if num_of_days <= 0 else filtered_df["area"].sum() / num_of_days
    area_per_event = 0 if num_of_days <= 0 else filtered_df["area"].sum() / num_of_events
    max_si, max_si_event_id = get_max_id(filtered_df, "si", return_value=True)
    max_length, max_length_event_id = get_max_id(filtered_df, "length", return_value=True)
    max_area, max_area_event_id = get_max_id(filtered_df, "area", return_value=True)

    stats_dict = {
        # "si_sum": si_sum,
        # "si_ts_sum": si_ts_sum,
        # "Average si_per_day": si_per_day,
        # "Average si_per_event": si_per_event,
        # "Average si_per_ts_event": si_per_ts_event,
        # "Average length_per_day": length_per_day,
        # "Average length_per_event": length_per_event,
        # "Average area_per_day": area_per_day,
        # "Average area_per_event": area_per_event,
        "Max si": max_si,
        "Event id with max SI": max_si_event_id,
        "Max length": max_length,
        "Event id with max length": max_length_event_id,
        "Max area": max_area,
        "Event id with max area": max_area_event_id
    }
    return pd.DataFrame([stats_dict])
