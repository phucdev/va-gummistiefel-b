from typing import List

import plotly.graph_objects as go
import pandas as pd
import numpy as np
import scipy.stats

months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
          "November", "December"]

lat_min = 34.9099998474
lat_max = 56.4199981689
long_min = 2.6099998951
long_max = 20.9799995422


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
    fig.add_trace(go.Histogram(
        name="Normal precipitation events",
        x=list(normal_precipitation_events["year"]),
        histfunc="count",
        autobinx=False,
        xbins=dict(
            start=min(list(normal_precipitation_events["year"])),
            end=max(list(normal_precipitation_events["year"])),
            size=bin_size)))
    fig.add_trace(go.Histogram(
        name="Heavy precipitation events",
        x=list(heavy_precipitation_events["year"]),
        histfunc="count",
        autobinx=False,
        xbins=dict(
            start=min(list(heavy_precipitation_events["year"])),
            end=max(list(heavy_precipitation_events["year"])),
            size=bin_size)))

    # The two histograms are drawn on top of another
    fig.update_layout(barmode='relative')
    return fig


def get_histogram(df, column_name=None, heavy_precipitation_filter=False, bin_size=1, hist_func="count"):
    assert hist_func in ["count", "sum", "avg", "min", "max"], f"{hist_func} not a valid hist_func"
    if column_name:
        assert column_name in df, f"{column_name} not in df"
    filtered_df = df
    if heavy_precipitation_filter:
        filtered_df = filtered_df[filtered_df["si"] > 0.0]
    fig = go.Figure()
    if hist_func == "count":
        fig.add_trace(go.Histogram(
            name=hist_func,
            x=list(filtered_df["year"]),
            histfunc=hist_func,
            autobinx=False,
            xbins=dict(
                start=min(list(filtered_df["year"])),
                end=max(list(filtered_df["year"])),
                size=bin_size)
        ))
    elif column_name:
        if hist_func in ["avg", "min", "max"]:
            fig.add_trace(go.Histogram(
                name=f"avg {column_name}",
                x=list(filtered_df["year"]),
                y=list(filtered_df[column_name]),
                histfunc="avg",
                autobinx=False,
                opacity=0.75,
                xbins=dict(
                    start=min(list(filtered_df["year"])),
                    end=max(list(filtered_df["year"])),
                    size=bin_size)
            ))
            if hist_func == "avg":
                alt_hist_func = "max"
            else:
                alt_hist_func = hist_func
            fig.add_trace(go.Histogram(
                name=f"{alt_hist_func} {column_name}",
                x=list(filtered_df["year"]),
                y=list(filtered_df[column_name]),
                histfunc=alt_hist_func,
                autobinx=False,
                opacity=0.75,
                xbins=dict(
                    start=min(list(filtered_df["year"])),
                    end=max(list(filtered_df["year"])),
                    size=bin_size),
                yaxis="y2"
            ))
            fig.update_layout(
                yaxis=dict(
                    title=f"avg {column_name}",
                    titlefont=dict(
                        color="#1f77b4"
                    ),
                    tickfont=dict(
                        color="#1f77b4"
                    )
                ),
                yaxis2=dict(
                    title=f"{alt_hist_func} {column_name}",
                    titlefont=dict(
                        color="#ff7f0e"
                    ),
                    tickfont=dict(
                        color="#ff7f0e"
                    ),
                    anchor="x",
                    overlaying="y",
                    side="right",
                )
            )

    # TODO add trend line?
    return fig


def get_rose_chart(df, max_radius=40000):
    heavy_precipitation_events = df[df["si"] > 0.0]
    normal_precipitation_events = df[df["si"] == 0.0]

    heavy_data = pd.DataFrame(
        heavy_precipitation_events.groupby(['month']).id.count().reset_index(name='events')
    ).sort_values(['month'], ascending=True)
    normal_data = pd.DataFrame(
        normal_precipitation_events.groupby(['month']).id.count().reset_index(name='events')
    ).sort_values(['month'], ascending=True)

    heavy_data["month_str"] = months
    reversed_num_of_events_heavy = heavy_data.sort_values(["month"], ascending=False)

    normal_data["month_str"] = months
    reversed_num_of_events_normal = normal_data.sort_values(["month"], ascending=False)
    fig = go.Figure()
    fig.add_trace(go.Barpolar(
        r=list(reversed_num_of_events_normal["events"]),
        theta=reversed_num_of_events_normal["month_str"],
        name="Number of normal precipitation events",
        marker_color="blue",
        marker_line_color="black",
        hoverinfo=["all"],
        opacity=0.7
    ))

    fig.add_trace(go.Barpolar(
        r=list(reversed_num_of_events_heavy["events"]),
        theta=reversed_num_of_events_heavy["month_str"],
        name="Number of heavy precipitation events",
        marker_color="red",
        marker_line_color="black",
        hoverinfo=["all"],
        opacity=0.7
    ))

    fig.update_layout(
        title="Number of precipitation events per month",
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


def get_event_on_map(df, column_name="si", event_ids: List[int] = None):
    filtered_df = df
    if event_ids:
        filtered_df = filtered_df[filtered_df["id"].isin(event_ids)]
    fig = go.Figure(data=go.Scattergeo(
        lon=filtered_df['lonMax'],
        lat=filtered_df['latMax'],
        text=filtered_df['si'],
        mode='markers',
        marker=dict(
            size=filtered_df['area']*10,
            opacity=0.8,
            reversescale=True,
            autocolorscale=False,
            colorscale='Blues',
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


def get_boxplot(df, column_name):
    fig = go.Figure()
    fig.add_trace(
        go.Box(y=list(df[column_name]), name=column_name)
    )
    return fig


def get_max_id(df, column_name):
    assert column_name in df, f"{column_name} not in df"
    max_length_event_id = df.iloc[df[column_name].argmax()]["id"]
    return max_length_event_id


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
    si_per_day = si_sum/num_of_days
    si_per_event = si_sum/num_of_events
    si_per_ts_event = si_ts_sum/num_of_ts_events
    length_per_day = filtered_df["length"].sum()/num_of_days
    length_per_event = filtered_df["length"].sum()/num_of_events
    area_per_day = filtered_df["area"].sum() / num_of_days
    area_per_event = filtered_df["area"].sum() / num_of_events
    max_si = filtered_df["si"].max()
    max_si_event_id = filtered_df.sort_values(by="si", ascending=False).iloc[0]["id"]
    max_length = filtered_df["length"].max()
    max_length_event_id = filtered_df.sort_values(by="length", ascending=False).iloc[0]["id"]
    max_area = filtered_df["area"].max()
    max_area_event_id = filtered_df.sort_values(by="area", ascending=False).iloc[0]["id"]

    stats_dict = {
        "si_sum": si_sum,
        "si_ts_sum": si_ts_sum,
        "Average si_per_day": si_per_day,
        "Average si_per_event": si_per_event,
        "Average si_per_ts_event": si_per_ts_event,
        "Average length_per_day": length_per_day,
        "Average length_per_event": length_per_event,
        "Average area_per_day": area_per_day,
        "Average area_per_event": area_per_event,
        "Max si": max_si,
        "Event id with max SI": max_si_event_id,
        "Max length": max_length,
        "Event id with max length": max_length_event_id,
        "Max area": max_area,
        "Event id with max area": max_area_event_id
    }
    return pd.DataFrame([stats_dict])
