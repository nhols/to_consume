from typing import Any, Callable

from pandas import DataFrame

from to_consume.utils import recurse_through_dict
from pydantic import BaseModel, validator


class BaseTitle:
    def __init__(self, imdb_id: str) -> None:
        self.imdb_id = imdb_id
        self.title = None
        self.type = None
        self.avg_imdb_rating = None
        self.imdb_ratings_count = None
        self.streaming_platforms = None
        self.image_url = None
        self.seasons: list[Season] = []
        self.overview: str = None

    def set_attr_from_dict_if_exists(
        self, d: dict, attr_name: str, keys: list[str], preprocess_function: Callable | None = None
    ) -> None:
        value = recurse_through_dict(d, keys)
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


class Episode(BaseModel):
    imdb_id: str
    title: str
    imdb_rating: float | None = None
    imdb_ratings_count: int = 0
    overview: str | None = None

    @validator("imdb_ratings_count", pre=True)
    def process_imdb_ratings_count(cls, imdb_ratings_count) -> int:
        if imdb_ratings_count is None:
            return 0
        return imdb_ratings_count


class Season(BaseModel):
    number: int
    episodes: list[Episode] = []
    title: str | None = None
