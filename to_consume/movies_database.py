from typing import Any
import requests
import os
from to_consume.cache import persist_to_file
from to_consume.utils import recurse_through_dict

BASE_URL = "https://moviesdatabase.p.rapidapi.com/"

HEADERS = {"X-RapidAPI-Key": os.getenv("RAPID_API_KEY"), "X-RapidAPI-Host": "moviesdatabase.p.rapidapi.com"}


class MoviesDatabaseTitle:
    def __init__(self, imdb_id: str) -> None:
        self.imdb_id = imdb_id
        self.get_title_info()
        self.get_title_ratings()

    def get_title_info(self) -> None:
        self.title_info = get_title_info(self.imdb_id)
        self.title = recurse_through_dict(self.title_info, ["titleText", "text"])
        self.type = recurse_through_dict(self.title_info, ["titleType", "text"])
        self.image_url = recurse_through_dict(self.title_info, ["primaryImage", "url"])

    def get_title_ratings(self) -> None:
        self.title_ratings = get_title_ratings(self.imdb_id)
        self.avg_imdb_rating = recurse_through_dict(self.title_ratings, ["averageRating"])
        self.imdb_ratings_count = recurse_through_dict(self.title_ratings, ["numVotes"])

    def get_watchlist_record(self) -> dict:
        return {k: v for k, v in self.__dict__.items() if k not in ["title_info", "title_ratings", "image_url"]}


@persist_to_file("moviesdatabase_title_info.json")
def get_title_info(imdb_id: str) -> dict | None:
    url = BASE_URL + f"titles/{imdb_id}"
    return get_movies_database_data(url)


@persist_to_file("moviesdatabase_title_ratings.json")
def get_title_ratings(imdb_id: str) -> dict | None:
    url = BASE_URL + f"titles/{imdb_id}/ratings"
    return get_movies_database_data(url)


def get_movies_database_data(url: str) -> Any:
    response = requests.request("GET", url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()["results"]
