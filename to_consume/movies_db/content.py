from collections import defaultdict
from datetime import date
from to_consume.base_content import BaseEpisode, BaseContent, BaseTitle
from to_consume.movies_db.api import (
    get_title_episodes,
    get_title_info_url,
    get_title_ratings_url,
)
from to_consume.movies_db.api_async import get_movies_db_urls_async, get_title_info_async, get_title_rating_async


def parse_date(x: dict):
    try:
        return date(x["year"], x["month"], x["day"])
    except:
        return None


class MoviesDbContent(BaseContent):
    def __init__(self, imdb_id: str, responses: dict) -> None:
        super().__init__(imdb_id, responses)
        self.set_attr_from_dict_if_exists(responses, "title", ["mdb_title_info", "titleText", "text"])
        self.set_attr_from_dict_if_exists(responses, "type", ["mdb_title_info", "titleType", "text"])
        self.set_attr_from_dict_if_exists(responses, "image_url", ["mdb_title_info", "primaryImage", "url"])
        self.set_attr_from_dict_if_exists(
            responses,
            "date_released",
            ["mdb_title_info", "releaseDate"],
            parse_date,
        )
        self.set_attr_from_dict_if_exists(
            responses, "avg_imdb_rating", ["mdb_title_rating", "averageRating"], lambda x: x * 10
        )
        self.set_attr_from_dict_if_exists(responses, "imdb_ratings_count", ["mdb_title_rating", "numVotes"])


class MoviesDbTitle(BaseTitle, MoviesDbContent):
    def __init__(self, imdb_id: str, responses: dict | None = None) -> None:
        if responses is None:
            responses = {}
        new_responses = self.get_title_responses_mdb(imdb_id)
        responses.update(new_responses)
        super().__init__(imdb_id, responses)

    def append_episode_responses(self, episode_responses: defaultdict[dict]) -> None:
        super().append_episode_responses(episode_responses)
        responses = self.get_episode_responses_mdb()
        for episode_imdb_id, response in responses.items():
            episode_responses[episode_imdb_id].update(response)

    @staticmethod
    def get_title_responses_mdb(imdb_id: str) -> dict:
        urls = [get_title_info_url(imdb_id), get_title_ratings_url(imdb_id)]
        resp_names = ["mdb_title_info", "mdb_title_rating"]
        responses = get_movies_db_urls_async(urls)
        return {resp_name: resp for resp_name, resp in zip(resp_names, responses)}

    def get_episode_responses_mdb(self) -> defaultdict[dict]:
        series_responses = get_title_episodes(self.imdb_id)
        episode_imdb_ids = [episode["tconst"] for episode in series_responses]
        title_infos = get_title_info_async(episode_imdb_ids)  # TODO async over both?
        title_ratings = get_title_rating_async(episode_imdb_ids)
        episode_responses = defaultdict(dict)
        for episode_imdb_id, title_info, title_rating, series in zip(
            episode_imdb_ids, title_infos, title_ratings, series_responses
        ):
            episode_responses[episode_imdb_id].update(
                mdb_title_info=title_info, mdb_title_rating=title_rating, mdb_series=series
            )
        return episode_responses


def safe_season_ep_number(x):
    try:
        return int(x)
    except:
        return -1


class MoviesDbEpisode(BaseEpisode, MoviesDbContent):
    def __init__(self, imdb_id: str, responses: dict) -> None:
        super().__init__(imdb_id, responses)
        self.set_attr_from_dict_if_exists(
            responses, "season_number", ["mdb_series", "seasonNumber"], safe_season_ep_number
        )
        self.set_attr_from_dict_if_exists(
            responses, "episode_number", ["mdb_series", "episodeNumber"], safe_season_ep_number
        )
