from download_utils import *
import time
import argparse
from pathlib import Path
import math

from gummistiefel import GS_SERVER_ADDRESS


def main():
    parser = argparse.ArgumentParser(
        description='Gummistiefel downloader')
    parser.add_argument('save_path', help='Where to save all the event data')
    args = parser.parse_args()

    save_path = Path(args.save_path)

    # Set default values
    si_filter = True
    batch_size = 1000
    start_date = "1979-01-01T00:00:00"
    end_date = "2018-01-01T00:00:00"
    query = "subset=start({},{}".format(start_date, end_date)

    events = query_events(query, with_time_series=False)
    pd.DataFrame(events).to_json(save_path.joinpath("regen_event_list.json"),
                                 orient='records', lines=True)

    if si_filter:
        filtered_events = [event for event in events if event["si"] > 0.0]
    else:
        filtered_events = events

    batches = math.ceil(len(filtered_events)/batch_size)
    merge_list = []
    for num, i in enumerate(range(0, len(filtered_events), batch_size)):
        t0 = time.time()
        print("Working on batch {} of {}".format(num, batches))
        batch = filtered_events[i:min(i+batch_size, len(filtered_events))]
        event_ids = [event["id"] for event in batch]
        events_with_timeseries = get_events(event_ids, GS_SERVER_ADDRESS, geojson=True)
        save_file = save_path.joinpath("event_timeseries_batch{}.json".format(num))
        events_with_timeseries_df = pd.DataFrame(events_with_timeseries)
        events_with_timeseries_df.to_json(save_file, orient='records', lines=True)
        merge_list.append(events_with_timeseries_df)
        print("Time needed for `%s': %.2fs"
              % ("batch {}".format(num), time.time() - t0))
    pd.concat(merge_list).to_json(save_path.joinpath("regen_event_list_ts.json"))
    print('Done.')


if __name__ == '__main__':
    main()
