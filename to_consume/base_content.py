from collections import defaultdict
import logging
from typing import Any, Callable

from pandas import DataFrame

from to_consume.utils import recurse_through_dict
from pydantic import BaseModel, validator

logger = logging.getLogger(__name__)


class BaseContent:
    def __init__(self, imdb_id: str, responses: dict) -> None:
        self.imdb_id = imdb_id
        self.title = None
        self.type = None
        self.avg_imdb_rating = None
        self.imdb_ratings_count = None
        self.date_released = None
        self.streaming_platforms = None
        self.image_url = None
        self.overview: str = None

    def set_attr_from_dict_if_exists(
        self, d: dict, attr_name: str, keys: list[str], preprocess_function: Callable | None = None
    ) -> None:
        value = recurse_through_dict(d, keys)
        if preprocess_function is not None and value is not None:
            try:
                value = preprocess_function(value)
            except Exception as e:
                logger.error(f"Error in preprocess_function for {self.imdb_id}, {attr_name}: {e}")
        self.set_attr_if_exists(attr_name, value)

    def set_attr_if_exists(self, attr_name: str, attr_value: Any, preprocess_function: Callable | None = None) -> None:
        if attr_value is not None:
            if preprocess_function is not None:
                attr_value = preprocess_function(attr_value)
            setattr(self, attr_name, attr_value)

    def get_seasons_df(self) -> DataFrame:
        records = []
        for season in self.seasons:
            for episode in season.episodes:
                records.append(
                    (
                        season.title,
                        episode.title,
                        episode.imdb_rating,
                        episode.imdb_ratings_count,
                        episode.overview,
                    )
                )

        return DataFrame(
            records,
            columns=["season", "episode", "imdb_rating", "imdb_ratings_count", "overview"],
        )


class BaseTitle:
    def __init__(self, imdb_id: str, responses: dict) -> None:
        super().__init__(imdb_id, responses)

    def append_episode_responses(self, episode_responses: defaultdict[dict]) -> None:
        pass


class BaseEpisode:
    def __init__(self, imdb_id: str, responses: dict) -> None:
        super().__init__(imdb_id, responses)
        self.imdb_id = imdb_id
        self.season_number = None
        self.episode_number = None
