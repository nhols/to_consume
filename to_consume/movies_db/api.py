import logging
import os
from typing import Any
from venv import logger
import requests
from to_consume.cache import cache_db
logger = logging.getLogger(__name__)

BASE_URL = "https://moviesdatabase.p.rapidapi.com/"

HEADERS = {"X-RapidAPI-Key": os.getenv("RAPID_API_KEY"), "X-RapidAPI-Host": "moviesdatabase.p.rapidapi.com"}

def get_title_info_url(imdb_id: str) -> str:
    return BASE_URL + f"titles/{imdb_id}"

@cache_db("moviesdatabase", "title_info")
def get_title_info(imdb_id: str) -> dict | None:
    url = get_title_info_url(imdb_id)
    return get_movies_database_data(url)

def get_title_ratings_url(imdb_id: str) -> str:
    return BASE_URL + f"titles/{imdb_id}/ratings"

@cache_db("moviesdatabase", "title_ratings")
def get_title_ratings(imdb_id: str) -> dict | None:
    url = get_title_ratings_url(imdb_id)
    resp = get_movies_database_data(url)
    if resp is None:
        return {}
    return resp


@cache_db("moviesdatabase", "seasons")
def get_title_season_count(imdb_id: str) -> dict | None:
    url = BASE_URL + f"titles/seasons/{imdb_id}"
    return get_movies_database_data(url)

def get_title_episodes_url(imdb_id: str) -> str:
    return BASE_URL + f"titles/series/{imdb_id}"

@cache_db("moviesdatabase", "episodes")
def get_title_episodes(imdb_id: str) -> dict | None:
    url = get_title_episodes_url(imdb_id)
    return get_movies_database_data(url)


def get_movies_database_data(url: str) -> Any:
    logger.info(f"Fetching data from {url}")
    response = requests.request("GET", url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()["results"]
