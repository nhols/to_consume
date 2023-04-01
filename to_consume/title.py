from urllib.parse import quote

from to_consume.movies_database import MoviesDatabaseTitle
from to_consume.streaming_availability import StreamingInfoTitle


class Title(MoviesDatabaseTitle, StreamingInfoTitle):
    def __init__(self, imdb_id: str) -> None:
        super().__init__(imdb_id)
        self._set_urls()

    def _set_urls(self) -> None:
        self.imdb_url = f"https://www.imdb.com/title/{self.imdb_id}"
        self.just_watch_url = f"https://www.justwatch.com/uk/search?q={quote(self.title)}"
        self.unogs_url = f"https://unogs.com/search/{quote(self.title)}"
