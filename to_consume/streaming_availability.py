import logging
from requests import request
import os
import json
from to_consume.utils import recurse_through_dict
import logging

BASE_URL = "https://streaming-availability.p.rapidapi.com/v2/"

HEADERS = {"X-RapidAPI-Key": os.getenv("RAPID_API_KEY"), "X-RapidAPI-Host": "streaming-availability.p.rapidapi.com"}


def get_streaming_availability_list(imdb_id: str, country: str = "gb") -> list[str] | None:
    streaming_info = get_streaming_availability(imdb_id, country)
    streaming_info_dict = recurse_through_dict(streaming_info, ["streamingInfo", "gb"])
    if streaming_info_dict:
        return list(streaming_info_dict.keys())


def get_streaming_availability(imdb_id: str, country: str = "gb") -> dict | None:
    logging.info(f"Getting streaming availability for {imdb_id}")

    with open("streaming_info_get_basic.json") as r:
        streaming_info = json.load(r)

    if imdb_id in streaming_info:
        return streaming_info[imdb_id]

    url = BASE_URL + "get/basic"
    querystring = {"country": country, "imdb_id": imdb_id}
    response = request("GET", url, headers=HEADERS, params=querystring)
    if response.status_code == 200:
        result = response.json()["result"]
        streaming_info[imdb_id] = result
        with open("streaming_info_get_basic.json", "w") as w:
            json.dump(streaming_info, w)
        return result
    logging.warning(f"Failed to get streaming availability for {imdb_id} with response: {response.text}")
