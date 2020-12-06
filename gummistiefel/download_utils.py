import asyncio
import math
import logging
import aiohttp
import json
import requests
import time

from typing import Union, List, Dict
from gummistiefel import GS_SERVER_ADDRESS

logger = logging.getLogger('gummistiefel')
logger.setLevel(logging.INFO)


async def download_site(url, session):
    async with session.get(url) as response:
        return await response.read()


async def download_all_sites(sites):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in sites:
            task = asyncio.ensure_future(download_site(url, session))
            tasks.append(task)
        return await asyncio.gather(*tasks, return_exceptions=True)


def get_event_url(event_id: Union[str, int],
                  webserver_address: str = GS_SERVER_ADDRESS,
                  geojson: bool = True) -> str:
    url = webserver_address + "get?id=" + str(event_id)
    if geojson:
        url += "&format=geojson"
    return url


def get_event(event_id: Union[str, int],
              webserver_address: str = GS_SERVER_ADDRESS,
              geojson: bool = True) -> Dict:
    """
        Takes an id and retrieves the corresponding precipitation event from
        the web server. Simple implementation with requests for single event
        retrieval.

        Parameters
        ----------
        event_id: Document containing events
        webserver_address: Address of the web server
        geojson: Whether to request in geojson format

        Returns
        -------
        Event as json dictionary
    """
    url = get_event_url(event_id, webserver_address, geojson)
    f = requests.get(url)  # TODO handle invalid urls
    json_dict = json.loads(f.text)
    return json_dict


def get_events(event_ids: List[Union[str, int]],
               webserver_address: str = GS_SERVER_ADDRESS,
               geojson: bool = True) -> List[Dict]:
    """
        Takes a list of event ids and retrieves the corresponding precipitation events
        from the web server. Uses asyncio, aiohttp stuff for faster asynchronous
        retrieval.

        Parameters
        ----------
        event_ids: List of event ids
        webserver_address: Address of the web server
        geojson: Whether to request in geojson format

        Returns
        -------
        Events as a list of json dictionaries
    """
    urls = [get_event_url(event_id, webserver_address, geojson) for event_id in event_ids]
    loop = asyncio.get_event_loop()
    events = loop.run_until_complete(download_all_sites(urls))
    return [json.loads(event) for event in events]


def batched_get_events(event_ids: List[Union[str, int]],
                       webserver_address: str = GS_SERVER_ADDRESS,
                       geojson: bool = True,
                       batch_size: int = 1000) -> List[Dict]:
    """
        Takes a list of event ids and retrieves the corresponding precipitation events
        from the web server in batches. Uses asyncio, aiohttp stuff for faster asynchronous
        retrieval.

        Parameters
        ----------
        event_ids: List of event ids
        webserver_address: Address of the web server
        geojson: Whether to request in geojson format
        batch_size: Size of batches

        Returns
        -------
        Events as a list of json dictionaries
    """
    batches = math.ceil(len(event_ids) / batch_size)
    logger.info("Processing {} batches".format(batches))
    merge_list = []
    for num, i in enumerate(range(0, len(event_ids), batch_size)):
        t0 = time.time()
        batch = event_ids[i:min(i + batch_size, len(event_ids))]
        events_with_timeseries = get_events(batch, webserver_address, geojson)
        merge_list += events_with_timeseries
        logger.info("Time needed for `%s': %.2fs"
                    % ("batch {}".format(num), time.time() - t0))
    return merge_list


def query_events(query: str,
                 webserver_address: str = GS_SERVER_ADDRESS,
                 geojson: bool = True,
                 with_time_series: bool = True,
                 si_filter: bool = False,
                 batch_size: int = -1) -> List[Dict]:
    """
        Takes a string query and retrieves the corresponding precipitation events
        from the web server.

        Parameters
        ----------
        query: String query
        webserver_address: Address of the web server
        geojson: Whether to request in geojson format
        with_time_series: Whether to send get requests for each event to retrieve time series data
        si_filter: Only keep events with si > 0.0
        batch_size: If provided, request events with time series in batches

        Returns
        -------
        Events as a list of json dictionaries
    """
    url = webserver_address + "query?" + query
    f = requests.get(url)
    json_dict = json.loads(f.text)
    if with_time_series:
        event_ids = [event["id"] for event in json_dict if (not si_filter) or (event["si"] > 0.0)]
        if batch_size > 0:
            logger.info("Process in batches of size {}".format(batch_size))
            return batched_get_events(event_ids, webserver_address, geojson, batch_size)
        else:
            return get_events(event_ids, webserver_address, geojson)
    else:
        return json_dict
