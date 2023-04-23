from __future__ import annotations
from collections import defaultdict
from urllib.parse import quote

from to_consume.movies_db.content import MoviesDbEpisode, MoviesDbTitle
from to_consume.streaming_availability.content import StreamingInfoEpisode, StreamingInfoTitle


class Title(MoviesDbTitle, StreamingInfoTitle):
    def __init__(self, imdb_id: str) -> None:
        super().__init__(imdb_id, {})
        self._set_urls()
        self._set_episodes()

    def _set_urls(self) -> None:
        search_term = self.imdb_id if self.title is None else quote(self.title)
        self.imdb_url = f"https://www.imdb.com/title/{self.imdb_id}"
        self.just_watch_url = f"https://www.justwatch.com/uk/search?q={search_term}"
        self.unogs_url = f"https://unogs.com/search/{search_term}"

    def _set_episodes(self) -> list[Episode]:
        episode_responses = defaultdict(dict)
        super().append_episode_responses(episode_responses)
        self.episodes = []
        for episode_imdb_id, response in episode_responses.items():
            self.episodes.append(Episode(episode_imdb_id, response))

    def title_db_record(self) -> dict:
        return {
            "imdb_id": self.imdb_id,
            "title": self.title,
            "date_released": self.date_released,
            "title_type": self.title_type,
            "imdb_rating": self.imdb_rating,
            "imdb_rating_count": self.imdb_rating_count,
        }

    def episode_db_records(self) -> dict:
        title_info = {"title_imdb_id": self.imdb_id}
        records = []
        for episode in self.episodes:
            new_record = title_info | episode.episode_db_record()
            records.append(new_record)
        return records


class Episode(MoviesDbEpisode, StreamingInfoEpisode):
    def __init__(self, imdb_id: str, responses: dict) -> None:
        super().__init__(imdb_id, responses)

    def episode_db_record(self) -> dict:
        return {
            "episode_imdb_id": self.imdb_id,
            "season_number": self.season_number,
            "episode_number": self.episode_number,
            "title": self.title,
            "date_released": self.date_released,
            "imdb_rating": self.imdb_rating,
            "imdb_rating_count": self.imdb_rating_count,
        }
