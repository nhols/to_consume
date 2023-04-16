import logging
from requests import request
import os
from to_consume.base_title import BaseTitle, Episode, Season
from to_consume.cache import cache_db, fetch_from_cache, write_to_cache
from to_consume.utils import recurse_through_dict
import logging

BASE_URL = "https://streaming-availability.p.rapidapi.com/v2/"

HEADERS = {"X-RapidAPI-Key": os.getenv("RAPID_API_KEY"), "X-RapidAPI-Host": "streaming-availability.p.rapidapi.com"}


class StreamingInfoTitle(BaseTitle):
    def __init__(self, imdb_id: str) -> None:
        super().__init__(imdb_id)
        basic_resp = get_streaming_availability_gb(self.imdb_id)
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
        self._set_seasons()

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

    def _set_seasons(self) -> None:
        self.seasons = []
        for number, season in enumerate(self.basic_resp.get("seasons", []), start=1):
            season_ = Season(
                number=number,
                title=season.get("title"),
                episodes=self._get_episodes(season),
            )
            self.seasons.append(season_)

    def _get_episodes(self, season: dict) -> list[Episode]:
        episodes = season.get("episodes")
        episodes_ = []
        if episodes:
            for episode in episodes:
                episodes_.append(
                    Episode(
                        imdb_id=episode.get("imdbId"),
                        title=episode.get("title"),
                        imdb_rating=episode.get("imdbRating") / 10,
                        imdb_ratings_count=episode.get("imdbVoteCount"),
                        overview=episode.get("overview"),
                    )
                )
        return episodes_


def cache_db_streaming_info(api: str, endpoint: str):
    def decorator(original_func):
        def new_func(param):
            res = fetch_from_cache(api, endpoint, param)
            if res is not None:
                return res

            res = original_func(param)
            if res is not None:
                write_to_cache(api, endpoint, param, res)
                write_episodes_to_cache(api, endpoint, res)
            return res

        return new_func

    return decorator


def write_episodes_to_cache(api: str, endpoint: str, res: dict) -> None:
    for season in res.get("seasons", []):
        for episode in season.get("episodes", []):
            if episode["imdbId"]:
                write_to_cache(api, endpoint, episode["imdbId"], episode)


@cache_db_streaming_info("streaming_info", "basic_gb")
def get_streaming_availability_gb(imdb_id: str) -> dict | None:
    return get_streaming_availability(imdb_id, "gb")


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
