import pandas as pd
import datetime
from tqdm import tqdm


def convert_date_string(date_string):
    return datetime.datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S')


def add_datetime(df: pd.DataFrame):
    df["datetime"] = df.apply(lambda x: convert_date_string(x["start"]), axis=1)
    df["year"] = df.apply(lambda x: x["datetime"].year, axis=1)
    df["month"] = df.apply(lambda x: x["datetime"].month, axis=1)
    return df


def process_timeseries(df: pd.DataFrame):
    """
    Assuming geojson format and that we did not find a more clever way to work with geopandas
    this creates a data frame with rows for every element in an event time series
    :param df:
    :return:
    """
    df_list = []
    if "start" in df and "datetime" not in df:
        df = add_datetime(df)
    for idx, row in tqdm(df.iterrows()):
        for i, elem in enumerate(row["timeseries"]["features"]):
            new_elem = elem["properties"]
            new_elem["id"] = row["id"]
            # new_elem["raw"] = elem
            new_elem["datetime"] = row["datetime"] + datetime.timedelta(hours=i)
            new_elem["year"] = row["year"]
            new_elem["month"] = row["month"]
            df_list.append(new_elem)
    return pd.DataFrame(df_list)
