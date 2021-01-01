import json
import argparse
import pandas as pd
import logging
from pathlib import Path

import requests
from tqdm import tqdm
from gummistiefel import GS_SERVER_ADDRESS
from gummistiefel import download_utils as du
from gummistiefel import preprocessing

logging.basicConfig(level=logging.INFO)


def main():
    parser = argparse.ArgumentParser(
        description='Gummistiefel downloader')
    parser.add_argument('save_path', help='Where to save all the event data')
    parser.add_argument('--si_filter', dest='si_filter', action='store_true')
    parser.add_argument('--no_si_filter', dest='si_filter', action='store_false')
    parser.set_defaults(si_filter=True)
    args = parser.parse_args()

    save_path = Path(args.save_path)

    # Set default values
    si_filter = args.si_filter
    start_date = "1979-01-01T00:00:00"
    end_date = "2018-01-01T00:00:00"
    logging.info(f"Download script with si_filter set to {si_filter} and dates from {start_date} to {end_date}.")
    query = "subset=start({},{}".format(start_date, end_date)

    logging.info(f"Collect all events.")
    if save_path.joinpath("regen_event_list.json").exists():
        events = pd.read_json(save_path.joinpath("regen_event_list.json"), lines=True).to_dict(orient="records")
    else:
        events = pd.DataFrame(du.query_events(query, with_time_series=False))
        events.to_json(save_path.joinpath("regen_event_list.json"),
                       orient="records", lines=True)

    if si_filter:
        filtered_events = [event for event in events if event["si"] > 0.0]
    else:
        filtered_events = events

    http = requests.Session()
    events_save_path = save_path.joinpath("regen_event_list_ts.json")
    with open(events_save_path, mode="w", encoding="utf-8") as f:
        for event in tqdm(filtered_events):
            url = du.get_event_url(event["id"], GS_SERVER_ADDRESS)
            response = http.get(url)
            response.raise_for_status()
            json_dict = json.loads(response.text)
            json.dump(json_dict, f)
            f.write("\n")
    events_df = pd.read_json(events_save_path, lines=True)
    events_df = preprocessing.add_datetime(events_df)
    events_df.to_json(events_save_path, orient="records", lines=True)
    ts_events_df = preprocessing.process_timeseries(events_df)
    ts_events_df.to_json(save_path.joinpath("regen_event_list_ts_expanded.json"), orient="records", lines=True)
    logging.info("Done.")


if __name__ == '__main__':
    main()
