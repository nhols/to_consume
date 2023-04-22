

from collections import defaultdict
from datetime import date
from to_consume.base_title import BaseTitle
from to_consume.movies_db.api import get_title_episodes, get_title_episodes_url, get_title_info, get_title_info_url, get_title_ratings, get_title_ratings_url
from to_consume.movies_db.api_async import get_movies_db_urls_async, get_title_info_async, get_title_rating_async



class MoviesDbBaseTitle(BaseTitle):
    def __init__(self, imdb_id: str, responses : dict) -> None:
        super().__init__(imdb_id, responses)
        self.set_attr_from_dict_if_exists(responses, "title", ["mdb_title_info", "titleText", "text"])
        self.set_attr_from_dict_if_exists(responses, "type", ["mdb_title_info", "titleType", "text"])
        self.set_attr_from_dict_if_exists(responses, "image_url", ["mdb_title_info", "primaryImage", "url"])
        self.set_attr_from_dict_if_exists(
            responses,
            "date_released",
            ["mdb_title_info", "releaseDate"],
            lambda x: date(x["year"], x["month"], x["day"]),
        )
        self.set_attr_from_dict_if_exists(responses, "avg_imdb_rating", ["mdb_title_ratings", "averageRating"])
        self.set_attr_from_dict_if_exists(responses, "imdb_ratings_count", ["mdb_title_ratings", "numVotes"])


class MoviesDbTitle(MoviesDbBaseTitle):
    def __init__(self, imdb_id: str, responses : dict) -> None:
        new_responses = {k:v for k,v in zip(["mdb_title_info", "mdb_title_ratings", "mdb_episodes"], get_movies_db_urls_async([get_title_info_url(imdb_id), get_title_ratings_url(imdb_id), get_title_episodes_url(imdb_id)]))}
        responses.update(new_responses)
        super().__init__(imdb_id, responses)
        self.set_attr_from_dict_if_exists(responses, "episode_imdb_ids", ["mdb_episodes"], lambda x: [episode["tconst"] for episode in x])


class MoviesDbEpisode(MoviesDbBaseTitle):
    def __init__(self, imdb_id: str,responses :dict) -> None:
        super().__init__(imdb_id, responses)
        # self.season_number = season_number # TODO set from dict
        # self.episode_number = episode_number


class MoviesDbEpisodes:
    def __init__(self, title_imdb_id: str, episode_imdb_ids:list[str], responses:defaultdict[dict]) -> None:
        if responses is None:
            responses = defaultdict(dict)
        self.title_imdb_id = title_imdb_id
        self.append_responses()
        super().__init__(episode_imdb_ids, responses)

    def append_responses(self, episode_imdb_ids:list[str], responses:defaultdict[dict]) -> None:
        title_infos = get_title_info_async(episode_imdb_ids)
        title_ratings = get_title_rating_async(episode_imdb_ids)
        for episode_key, title_info, title_rating in zip(self.episode_keys, title_infos, title_ratings):
            responses[episode_key].update(mdb_title_info=title_info, mdb_title_rating=title_rating)


if __name__ == "__main__":
    title = MoviesDbTitle("tt11041332", {})
    episodes = MoviesDbEpisodes(title.imdb_id, title.episodes)
    from pprint import pprint
    pprint([ep.__dict__ for ep in episodes.episodes])
    t = [x.imdb_id for x in episodes.episodes]
    a = get_title_rating_async(t)