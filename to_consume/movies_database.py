from collections import defaultdict
from typing import Any, DefaultDict
from venv import logger
import requests
import os
from to_consume.base_title import BaseTitle, Episode, Season
from to_consume.cache import cache_db
from to_consume.utils import recurse_through_dict

BASE_URL = "https://moviesdatabase.p.rapidapi.com/"

HEADERS = {"X-RapidAPI-Key": os.getenv("RAPID_API_KEY"), "X-RapidAPI-Host": "moviesdatabase.p.rapidapi.com"}


class MoviesDatabaseBaseTitle(BaseTitle):
    def __init__(self, imdb_id: str) -> None:
        super().__init__(imdb_id)
        self.get_title_info()
        self.get_title_ratings()
        self._set_seasons_mdb()

    def get_title_info(self) -> None:
        self.title_info = get_title_info(self.imdb_id)
        self.set_attr_from_dict_if_exists(self.title_info, "title", ["titleText", "text"])
        self.set_attr_from_dict_if_exists(self.title_info, "type", ["titleType", "text"])
        self.set_attr_from_dict_if_exists(self.title_info, "image_url", ["primaryImage", "url"])

    def get_title_ratings(self) -> None:
        self.title_ratings = get_title_ratings(self.imdb_id)
        self.set_attr_from_dict_if_exists(self.title_ratings, "avg_imdb_rating", ["averageRating"])
        self.set_attr_from_dict_if_exists(self.title_ratings, "imdb_ratings_count", ["numVotes"])

    def _set_seasons_mdb(self) -> None:
        self.seasons = []
        if not recurse_through_dict(self.title_info, ["titleType", "isSeries"]):
            return
        episodes = self._get_episodes_mdb()
        season_title_count = get_title_season_count(self.imdb_id)
        if season_title_count is None:
            return
        for season in range(1, get_title_season_count(self.imdb_id) + 1):
            self.seasons.append(
                Season(
                    number=season,
                    title=f"Season {season}",
                    episodes=episodes[season],
                )
            )

    def _get_episodes_mdb(self) -> DefaultDict[int, list[Episode]]:
        episodes = get_title_episodes(self.imdb_id)
        season_dict = defaultdict(list)
        for episode in episodes:
            episode_title = MoviesDatabaseBaseTitle(episode["tconst"])
            episode_ = Episode(
                imdb_id=episode_title.imdb_id,
                title=episode_title.title,
                imdb_rating=episode_title.avg_imdb_rating,
                imdb_ratings_count=episode_title.imdb_ratings_count,
                overview=episode_title.overview,
            )
            season_dict[episode["seasonNumber"]].append(episode_)
        return season_dict


@cache_db("moviesdatabase", "title_info")
def get_title_info(imdb_id: str) -> dict | None:
    url = BASE_URL + f"titles/{imdb_id}"
    return get_movies_database_data(url)


@cache_db("moviesdatabase", "title_ratings")
def get_title_ratings(imdb_id: str) -> dict | None:
    url = BASE_URL + f"titles/{imdb_id}/ratings"
    resp = get_movies_database_data(url)
    if resp is None:
        return {}
    return resp


@cache_db("moviesdatabase", "seasons")
def get_title_season_count(imdb_id: str) -> dict | None:
    url = BASE_URL + f"titles/seasons/{imdb_id}"
    return get_movies_database_data(url)


@cache_db("moviesdatabase", "episodes")
def get_title_episodes(imdb_id: str) -> dict | None:
    url = BASE_URL + f"titles/series/{imdb_id}"
    return get_movies_database_data(url)


def get_movies_database_data(url: str) -> Any:
    logger.info(f"Fetching data from {url}")
    response = requests.request("GET", url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()["results"]
