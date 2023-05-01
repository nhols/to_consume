import logging
from requests import request
import os
from to_consume.cache import cache_db

logger = logging.getLogger(__name__)

BASE_URL = "https://streaming-availability.p.rapidapi.com/v2/"

HEADERS = {"X-RapidAPI-Key": os.getenv("RAPID_API_KEY"), "X-RapidAPI-Host": "streaming-availability.p.rapidapi.com"}


@cache_db("streaming_info", "basic_gb")
def get_streaming_availability_gb(imdb_id: str) -> dict | None:
    return get_streaming_availability(imdb_id, "gb")


def get_streaming_availability(imdb_id: str, country: str = "gb") -> dict | None:
    logger.info(f"Getting streaming availability for {imdb_id}")
    url = BASE_URL + "get/basic"
    querystring = {"country": country, "imdb_id": imdb_id}
    response = request("GET", url, headers=HEADERS, params=querystring)
    if response.status_code == 200:
        result = response.json()["result"]
        return result
    if response.status_code == 404:
        logger.info(f"No streaming availability found for {imdb_id}")
        return {}
    logger.warning(f"Failed to get streaming availability for {imdb_id} with response: {response.text}")
