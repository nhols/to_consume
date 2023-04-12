import logging
from pandas import DataFrame
from requests import request
import os
import json
from to_consume.base_title import BaseTitle
from to_consume.cache import persist_to_file
from to_consume.utils import recurse_through_dict
import logging

BASE_URL = "https://streaming-availability.p.rapidapi.com/v2/"

HEADERS = {"X-RapidAPI-Key": os.getenv("RAPID_API_KEY"), "X-RapidAPI-Host": "streaming-availability.p.rapidapi.com"}


class StreamingInfoTitle(BaseTitle):
    def __init__(self, imdb_id: str) -> None:
        super().__init__(imdb_id)
        basic_resp = get_streaming_availability(self.imdb_id)
        self.basic_resp = basic_resp if basic_resp else {}
        self._get_info()
        self._get_streaming_availability()

    def _get_info(self) -> None:
        self.set_attr_from_dict_if_exists(self.basic_resp, "title", ["title"])
        self.set_attr_from_dict_if_exists(self.basic_resp, "type", ["type"])
        self.set_attr_from_dict_if_exists(self.basic_resp, "overview", ["overview"])
        self.set_attr_from_dict_if_exists(self.basic_resp, "tagline", ["tagline"])
        self.set_attr_from_dict_if_exists(self.basic_resp, "image_url", ["posterURLs", "original"])
        self.set_attr_from_dict_if_exists(self.basic_resp, "avg_imdb_rating", ["imdbRating"], lambda x: x / 10)
        self.set_attr_from_dict_if_exists(self.basic_resp, "imdb_ratings_count", ["imdbVoteCount"])
        self.set_attr_from_dict_if_exists(self.basic_resp, "trailer_url", ["youtubeTrailerVideoLink"])

    def _get_streaming_availability(self):
        streaming_info = recurse_through_dict(self.basic_resp, ["streamingInfo", "gb"])
        self.streaming_platforms = []
        self.streaming_links = {}
        if streaming_info:
            for platform in streaming_info:
                self.streaming_platforms.append(platform)
                watchlink = streaming_info[platform][0]["link"]
                self.streaming_links[platform] = watchlink
                self.streaming_platforms = [] if not streaming_info else list(streaming_info.keys())

    def get_seasons_df(self) -> DataFrame:
        records = []
        for season in self.basic_resp.get("seasons", []):
            season_title = season.get("title")
            episodes = season.get("episodes")
            if episodes:
                for episode in episodes:
                    records.append(
                        (
                            season_title,
                            episode.get("title"),
                            episode.get("imdbRating") / 10,
                            episode.get("imdbVoteCount"),
                            episode.get("overview"),
                        )
                    )

        return DataFrame(records, columns=["season", "episode", "imdb_rating", "imdb_ratings_count", "overview"])


@persist_to_file("streaming_info_get_basic.json")
def get_streaming_availability(imdb_id: str, country: str = "gb") -> dict | None:
    logging.info(f"Getting streaming availability for {imdb_id}")
    url = BASE_URL + "get/basic"
    querystring = {"country": country, "imdb_id": imdb_id}
    response = request("GET", url, headers=HEADERS, params=querystring)
    if response.status_code == 200:
        result = response.json()["result"]
        return result
    if response.status_code == 404:
        logging.info(f"No streaming availability found for {imdb_id}")
        return {}
    logging.warning(f"Failed to get streaming availability for {imdb_id} with response: {response.text}")
