

from collections import defaultdict
from datetime import date
from to_consume.base_title import BaseEpisode, BaseContent, BaseTitle
from to_consume.movies_db.api import get_title_episodes, get_title_episodes_url, get_title_info, get_title_info_url, get_title_ratings, get_title_ratings_url
from to_consume.movies_db.api_async import get_movies_db_urls_async, get_title_info_async, get_title_rating_async



class MoviesDbBaseTitle(BaseContent):
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


class MoviesDbTitle(BaseTitle, MoviesDbBaseTitle):
    def __init__(self, imdb_id: str, responses : dict) -> None:
        new_responses = {k:v for k,v in zip(["mdb_title_info", "mdb_title_ratings", "mdb_episodes"], get_movies_db_urls_async([get_title_info_url(imdb_id), get_title_ratings_url(imdb_id), get_title_episodes_url(imdb_id)]))}
        responses.update(new_responses)
        super().__init__(imdb_id, responses)
        self.set_attr_from_dict_if_exists(responses, "episode_imdb_ids", ["mdb_episodes"], lambda x: [episode["tconst"] for episode in x])
    
    def append_episode_responses(self, responses:defaultdict[dict]) -> None:
        series_responses = get_title_episodes(self.imdb_id)
        episode_imdb_ids = [episode["tconst"] for episode in series_responses]
        title_infos = get_title_info_async(episode_imdb_ids) # TODO async over both?
        title_ratings = get_title_rating_async(episode_imdb_ids)
        for episode_imdb_id, title_info, title_rating, series in zip(episode_imdb_ids, title_infos, title_ratings, series_responses):
            responses[episode_imdb_id].update(mdb_title_info=title_info, mdb_title_rating=title_rating, mdb_series=series)

class MoviesDbEpisode(BaseEpisode, MoviesDbBaseTitle):
    def __init__(self, imdb_id: str, responses :dict) -> None:
        super().__init__(imdb_id, responses)
        self.set_attr_from_dict_if_exists(responses, "season_number", ["mdb_series", "seasonNumber"])
        self.set_attr_from_dict_if_exists(responses, "episode_number", ["mdb_series", "episodeNumber"])




if __name__ == "__main__":
    title = MoviesDbTitle("tt11041332", {})
