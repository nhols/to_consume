from typing import Any, Callable

from to_consume.utils import recurse_through_dict


class BaseTitle:
    def __init__(self, imdb_id: str) -> None:
        self.imdb_id = imdb_id
        self.title = None
        self.type = None
        self.avg_imdb_rating = None
        self.imdb_ratings_count = None
        self.streaming_platforms = None
        self.image_url = None

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
