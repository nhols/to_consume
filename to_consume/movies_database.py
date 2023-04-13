from typing import Any
import requests
import os
from to_consume.base_title import BaseTitle
from to_consume.cache import cache_db

BASE_URL = "https://moviesdatabase.p.rapidapi.com/"

HEADERS = {"X-RapidAPI-Key": os.getenv("RAPID_API_KEY"), "X-RapidAPI-Host": "moviesdatabase.p.rapidapi.com"}


class MoviesDatabaseTitle(BaseTitle):
    def __init__(self, imdb_id: str) -> None:
        super().__init__(imdb_id)
        self.get_title_info()
        self.get_title_ratings()

    def get_title_info(self) -> None:
        self.title_info = get_title_info(self.imdb_id)
        self.set_attr_from_dict_if_exists(self.title_info, "title", ["titleText", "text"])
        self.set_attr_from_dict_if_exists(self.title_info, "type", ["titleType", "text"])
        self.set_attr_from_dict_if_exists(self.title_info, "image_url", ["primaryImage", "url"])

    def get_title_ratings(self) -> None:
        self.title_ratings = get_title_ratings(self.imdb_id)
        self.set_attr_from_dict_if_exists(self.title_ratings, "avg_imdb_rating", ["averageRating"])
        self.set_attr_from_dict_if_exists(self.title_ratings, "imdb_ratings_count", ["numVotes"])

    def get_watchlist_record(self) -> dict:
        return {k: v for k, v in self.__dict__.items() if k not in ["title_info", "title_ratings", "image_url"]}


@cache_db("moviesdatabase", "title_info")
def get_title_info(imdb_id: str) -> dict | None:
    url = BASE_URL + f"titles/{imdb_id}"
    return get_movies_database_data(url)


@cache_db("moviesdatabase", "title_ratings")
def get_title_ratings(imdb_id: str) -> dict | None:
    url = BASE_URL + f"titles/{imdb_id}/ratings"
    return get_movies_database_data(url)


def get_movies_database_data(url: str) -> Any:
    response = requests.request("GET", url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()["results"]
