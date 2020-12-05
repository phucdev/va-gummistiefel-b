from download_utils import *
import time
import argparse
import json
from pathlib import Path
import pickle

from gummistiefel import GS_SERVER_ADDRESS


def main():
    parser = argparse.ArgumentParser(
        description='Gummistiefel downloader')
    parser.add_argument('save_path', help='Where to save all the event data')
    args = parser.parse_args()

    save_path = Path(args.save_path)

    start_date = "1979-01-01T00:00:00"
    end_date = "2018-01-01T00:00:00"
    query = "subset=start({},{}".format(start_date, end_date)

    events = query_events(query, with_time_series=False)
    pd.DataFrame(events).to_json(save_path.joinpath("event_list.json"),
                                 orient='records', lines=True)
    batch_size = 10000
    for num, i in enumerate(range(0, len(events), batch_size)):
        t0 = time.time()
        print("Working on batch {}".format(num))
        batch = events[i:min(i+batch_size, len(events))]
        event_ids = [event["id"] for event in batch]
        events_with_timeseries = get_events(event_ids, GS_SERVER_ADDRESS, geojson=True)
        pd.DataFrame(events_with_timeseries).to_json(save_path.joinpath("event_timeseries_batch{}.json".format(num)),
                                                     orient='records', lines=True)
        print("Time needed for `%s' called: %.2fs"
              % ("batch {}".format(num), time.time() - t0))
    print('Done.')


if __name__ == '__main__':
    main()
