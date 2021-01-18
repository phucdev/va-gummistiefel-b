from typing import List

import plotly.graph_objects as go
import pandas as pd
import numpy as np
import scipy.stats

months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
          "November", "December"]


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


def get_stacked_bar_chart(df):
    heavy_precipitation_events = df[df["si"] > 0.0]
    normal_precipitation_events = df[df["si"] == 0.0]

    heavy_data = pd.DataFrame(
        heavy_precipitation_events.groupby(['year']).id.count().reset_index(name='events')
    ).sort_values(['year'], ascending=True)
    normal_data = pd.DataFrame(
        normal_precipitation_events.groupby(['year']).id.count().reset_index(name='events')
    ).sort_values(['year'], ascending=True)
    fig = go.Figure(data=[
        go.Bar(name='Normal Precipitation Events', x=list(normal_data["year"]), y=list(normal_data["events"])),
        go.Bar(name='Heavy Precipitation Events', x=list(heavy_data["year"]), y=list(heavy_data["events"]))
    ])
    # Change the bar mode
    fig.update_layout(barmode='stack')
    return fig


def get_bar_chart(df, heavy_precipitation_filter=False):
    filtered_df = df
    if heavy_precipitation_filter:
        filtered_df = filtered_df[filtered_df["si"] > 0.0]
    grouped_df = pd.DataFrame(
        filtered_df.groupby(['year']).id.count().reset_index(name='events')
    ).sort_values(['year'], ascending=True)
    fig = go.Figure(data=[go.Bar(
        x=list(grouped_df["year"]),
        y=list(grouped_df["events"]),
        text=list(grouped_df["events"]),
        textposition="auto"
    )])
    # TODO add trend line?
    return fig


def get_rose_chart(df):
    num_of_events = pd.DataFrame(
        df.groupby(['month']).id.count().reset_index(name='events')
    )
    num_of_events["month_str"] = months
    reversed_num_of_events = num_of_events.sort_values(["month"], ascending=False)
    fig = go.Figure()
    fig.add_trace(go.Barpolar(
        r=list(reversed_num_of_events["events"]),
        theta=reversed_num_of_events["month_str"],
        name="Number of events",
        marker_color="rgb(46,109,255)",
        marker_line_color="black",
        hoverinfo=["all"],
        opacity=0.7
    ))

    fig.update_layout(
        title="Number of heavy precipitation events",
        width=900,
        height=900,
        polar_angularaxis_rotation=90,
        polar=dict(
            bgcolor="rgb(223,223,223)",
            angularaxis=dict(
                linewidth=3,
                showline=True,
                linecolor='black'
            ),
            radialaxis=dict(
                showline=True,
                linewidth=2,
                gridcolor="white",
                gridwidth=2
            )
        )
    )
    return fig


def get_line_plot(df, column_name):
    grouped_df = df.groupby(["year"])["si"].apply(list)
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


def get_event_on_map(df, column_name="si", event_ids: List[int] = None):
    filtered_df = df
    if event_ids:
        filtered_df = filtered_df[filtered_df["id"].isin(event_ids)]
    fig = go.Figure(data=go.Scattergeo(
        lon=filtered_df['lonMax'],
        lat=filtered_df['latMax'],
        text=filtered_df['si'],
        mode='markers',
        marker_color=filtered_df[column_name],
    ))

    fig.update_layout(
        title=f'Heavy precipitation events ({column_name})',
        geo_scope='europe',
    )
    return fig


def get_boxplot(df, column_name):
    fig = go.Figure()
    fig.add_trace(
        go.Box(y=list(df[column_name]), name=column_name)
    )
    return fig
