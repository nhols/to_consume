from __future__ import annotations
from urllib.parse import quote
from to_consume.base_title import Episode

from to_consume.movies_database import MoviesDatabaseBaseTitle
from to_consume.streaming_availability import StreamingInfoTitle


class Title(MoviesDatabaseBaseTitle, StreamingInfoTitle):
    def __init__(self, imdb_id: str) -> None:
        super().__init__(imdb_id)
        self._set_urls()
        self._update_episodes()

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

    def _update_episodes(self) -> list[Episode]:
        for season in self.seasons:
            episode_ids = [episode.imdb_id for episode in season.episodes]
            season.episodes.clear()
            for episode_id in episode_ids:
                episode_title = Title(episode_id)
                season.episodes.append(
                    Episode(
                        imdb_id=episode_title.imdb_id,
                        title=episode_title.title,
                        imdb_rating=episode_title.avg_imdb_rating,
                        imdb_ratings_count=episode_title.imdb_ratings_count,
                        overview=episode_title.overview,
                    )
                )
