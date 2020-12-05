import asyncio
import aiohttp
import json
import requests
import pandas as pd

from typing import Union, List, Dict
from gummistiefel import GS_SERVER_ADDRESS


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
        Takes an id and retrieves the corresponding precipiation event from
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
        Takes a list of event ids and retrieves the corresponding precipiation events
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


def query_events(query: str,
                 webserver_address: str = GS_SERVER_ADDRESS,
                 geojson: bool = True,
                 with_time_series: bool = True) -> List[Dict]:
    """
        Takes a string query and retrieves the corresponding precipiation events
        from the web server.

        Parameters
        ----------
        query: String query
        webserver_address: Address of the web server
        geojson: Whether to request in geojson format
        with_time_series: Whether to send get requests for each event to retrieve time series data

        Returns
        -------
        Events as a list of json dictionaries
    """
    url = webserver_address + "query?" + query
    f = requests.get(url)  # TODO handle invalid urls
    json_dict = json.loads(f.text)
    if with_time_series:
        event_ids = [event["id"] for event in json_dict]
        return get_events(event_ids, webserver_address, geojson)
    else:
        return json_dict
