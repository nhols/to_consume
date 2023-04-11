from urllib.parse import quote

from to_consume.movies_database import MoviesDatabaseTitle
from to_consume.streaming_availability import StreamingInfoTitle


class Title(MoviesDatabaseTitle, StreamingInfoTitle):
    def __init__(self, imdb_id: str) -> None:
        super().__init__(imdb_id)
        self._set_urls()

    def _set_urls(self) -> None:
        search_term = self.imdb_id if self.title is None else quote(self.title)
        self.imdb_url = f"https://www.imdb.com/title/{self.imdb_id}"
        self.just_watch_url = f"https://www.justwatch.com/uk/search?q={search_term}"
        self.unogs_url = f"https://unogs.com/search/{search_term}"

    def get_title_df_record(self) -> dict:
        return {
            "imdb_id": self.imdb_id,
            "title": self.title,
            "type": self.type,
            "imdb_rating": self.avg_imdb_rating,
            "streaming_platforms": self.streaming_platforms,
        }
