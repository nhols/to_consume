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
        basic_resp = get_streaming_availability(self.imdb_id)
        self.basic_resp = basic_resp if basic_resp else {}
        self._get_info()
        self._get_streaming_availability()

    def _get_info(self) -> None:
        self.title = self.basic_resp.get("title")
        self.type = self.basic_resp.get("type")
        self.overview = self.basic_resp.get("overview")
        self.tagline = self.basic_resp.get("tagline")

    def _get_streaming_availability(self):
        streaming_info = recurse_through_dict(self.basic_resp, ["streamingInfo", "gb"])
        self.streaming_platforms = [] if not streaming_info else list(streaming_info.keys())


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


t = StreamingInfoTitle("tt0111161")
