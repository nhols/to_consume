import logging
from requests import request
import os
import json
from to_consume.cache import persist_to_file
from to_consume.utils import recurse_through_dict
import logging

BASE_URL = "https://streaming-availability.p.rapidapi.com/v2/"

HEADERS = {"X-RapidAPI-Key": os.getenv("RAPID_API_KEY"), "X-RapidAPI-Host": "streaming-availability.p.rapidapi.com"}


class StreamingInfoTitle:
    def __init__(self, imdb_id: str) -> None:
        self.imdb_id = imdb_id
        self.basic_resp = self.get_streaming_availability(self.imdb_id)


def get_streaming_availability_list(imdb_id: str, country: str = "gb") -> list[str] | None:
    streaming_info = get_streaming_availability(imdb_id, country)
    streaming_info_dict = recurse_through_dict(streaming_info, ["streamingInfo", "gb"])
    if streaming_info_dict:
        return list(streaming_info_dict.keys())


@persist_to_file("streaming_info_get_basic.json")
def get_streaming_availability(imdb_id: str, country: str = "gb") -> dict | None:
    logging.info(f"Getting streaming availability for {imdb_id}")
    url = BASE_URL + "get/basic"
    querystring = {"country": country, "imdb_id": imdb_id}
    response = request("GET", url, headers=HEADERS, params=querystring)
    if response.status_code == 200:
        result = response.json()["result"]
        return result
    logging.warning(f"Failed to get streaming availability for {imdb_id} with response: {response.text}")
