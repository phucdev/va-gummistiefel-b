import time
import argparse
import math
import pandas as pd
import logging
from pathlib import Path
from gummistiefel import GS_SERVER_ADDRESS
from gummistiefel import download_utils as du

logger = logging.getLogger('gummistiefel')
logger.setLevel(logging.INFO)


def get_year(row):
    return int(row['start'][:4])


def main():
    parser = argparse.ArgumentParser(
        description='Gummistiefel downloader')
    parser.add_argument('save_path', help='Where to save all the event data')
    args = parser.parse_args()

    save_path = Path(args.save_path)

    # Set default values
    si_filter = True
    save_batches = True
    batch_size = 10000
    start_date = "1979-01-01T00:00:00"
    end_date = "2018-01-01T00:00:00"
    query = "subset=start({},{}".format(start_date, end_date)

    events = du.query_events(query, with_time_series=False)
    pd.DataFrame(events).to_json(save_path.joinpath("regen_event_list.json"),
                                 orient='records', lines=True)

    if si_filter:
        filtered_events = [event for event in events if event["si"] > 0.0]
    else:
        filtered_events = events

    batches = math.ceil(len(filtered_events) / batch_size)
    merge_list = []
    for num, i in enumerate(range(0, len(filtered_events), batch_size)):
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
                    % ("batch {}".format(num), time.time() - t0))
    merge_list_df = pd.concat(merge_list)
    merge_list_df = merge_list_df.sort_values(by=["start"])
    merge_list_df['year'] = merge_list_df.apply(lambda row: get_year(row), axis=1)
    merge_list_df.to_json(save_path.joinpath("regen_event_list_ts.json"), orient='records', lines=True)
    logger.info('Done.')


if __name__ == '__main__':
    main()
