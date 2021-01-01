import time
import argparse
import math
import pandas as pd
import logging
from pathlib import Path
from gummistiefel import GS_SERVER_ADDRESS
from gummistiefel import download_utils as du
from gummistiefel import preprocessing

logger = logging.getLogger('gummistiefel')
logger.setLevel(logging.INFO)


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
    save_batches = True
    batch_size = 10000
    start_date = "1979-01-01T00:00:00"
    end_date = "2018-01-01T00:00:00"
    logging.info(f"Download script with si_filter set to {si_filter} and dates from {start_date} to {end_date}.")
    query = "subset=start({},{}".format(start_date, end_date)

    logger.info(f"Collect all events.")
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

    batches = math.ceil(len(filtered_events) / batch_size)
    merge_list = []
    logger.info(f"Download each event with timeseries.")
    for num, i in enumerate(range(0, len(filtered_events), batch_size)):
        if num < 48:
            continue
        t0 = time.time()
        logger.info("Working on batch {} of {}".format(num + 1, batches))
        batch = filtered_events[i:min(i + batch_size, len(filtered_events))]
        event_ids = [event["id"] for event in batch]
        events_with_timeseries = du.get_events(event_ids, GS_SERVER_ADDRESS, geojson=True)
        events_with_timeseries_df = pd.DataFrame(events_with_timeseries)
        if save_batches:
            save_file = save_path.joinpath("event_timeseries_batch{}.json".format(num))
            events_with_timeseries_df.to_json(save_file, orient='records', lines=True)
        merge_list.append(events_with_timeseries_df)
        logger.info("Time needed for `%s': %.2fs"
                     % ("batch {}".format(num + 1), time.time() - t0))
    merge_list_df = pd.concat(merge_list)
    merge_list_df = merge_list_df.sort_values(by=["start"])
    merge_list_df["datetime"] = merge_list_df.apply(lambda row: preprocessing.convert_date_string(row["start"]), axis=1)
    merge_list_df.to_json(save_path.joinpath("regen_event_list_ts.json"), orient='records', lines=True)
    logger.info("Done.")


if __name__ == '__main__':
    main()
