from to_consume.exceptions import ItemAlreadyInListError, ItemNotInListError
from to_consume.content import Title, write_title_records
from to_consume.streamlit.db_utils import db_conn

from psycopg2.extras import RealDictCursor
import streamlit as st

ItemStatus = tuple[bool, int]


class WatchList:
    def __init__(self, user_id: int):
        self.user_id: int = user_id
        self.refresh_watchlist_data()

    def refresh_watchlist_data(self) -> None:
        self.watchlist: dict = self.load_watchlist()
        self.watchlist_seasons: dict = self.load_watchlist_seasons()
        self.watchlist_titles: dict = self.load_watchlist_titles()

    def load_watchlist(self) -> dict:
        query = "SELECT imdb_id, watched, rating, created_at, updated_at FROM watchlist WHERE user_id = %s"
        return self.load_user_data(query)

    def load_watchlist_seasons(self) -> dict:
        query = """
            SELECT imdb_id, season_number, watched, rating, created_at, updated_at FROM watchlist_seasons 
            WHERE user_id = %s
        """
        conn = db_conn()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, (self.user_id,))
            res = cursor.fetchall()
        return {(result["imdb_id"], result["season_number"]): result for result in res}

    def load_watchlist_titles(self) -> dict:
        query = """
            SELECT
                titles.*
            FROM
                titles
                INNER JOIN watchlist ON watchlist.imdb_id = titles.imdb_id
                AND user_id = %s;
        """
        return self.load_user_data(query)

    def load_user_data(self, query: str) -> dict[str, dict]:
        conn = db_conn()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, (self.user_id,))
            res = cursor.fetchall()
        return self._key_by_imdb_id(res)

    def get_status(self, imdb_id: str) -> ItemStatus:
        if imdb_id not in self.watchlist:
            raise ItemNotInListError(f"{imdb_id} is not in the watchlist")
        record = self.watchlist[imdb_id]
        return record["watched"], record["rating"]

    def get_season_status(self, imdb_id: str, season: int) -> ItemStatus:
        record = self.watchlist_seasons.get((imdb_id, season))
        if record is None:
            return False, None
        return record["watched"], record["rating"]

    @staticmethod
    def _key_by_imdb_id(res: dict) -> dict:
        return {result["imdb_id"]: result for result in res}

    def add_to_watchlist(self, imdb_id: str) -> None:
        if imdb_id in self.watchlist:
            raise ItemAlreadyInListError(f"{imdb_id} is already in the watchlist")

        conn = db_conn()
        title = Title(imdb_id)
        write_title_records(conn, title)
        self.upsert_watchlist(imdb_id, watched=False, rating=None)
        self.refresh_watchlist_data()

    def upsert_watchlist(self, imdb_id: str, watched: bool, rating: int) -> None:
        query = """
            INSERT INTO watchlist (user_id, imdb_id, watched, rating) 
            VALUES (%(user_id)s, %(imdb_id)s, %(watched)s, %(rating)s)
            ON CONFLICT (user_id, imdb_id) DO UPDATE SET watched = EXCLUDED.watched, rating = EXCLUDED.rating;
        """
        data = {
            "user_id": self.user_id,
            "imdb_id": imdb_id,
            "watched": watched,
            "rating": rating,
        }
        self._upsert_watchlist_generic(query, data)

    def upsert_watchlist_seasons(self, imdb_id: str, season_number: int, watched: bool, rating: int) -> None:
        query = """
            INSERT INTO watchlist_seasons (user_id, imdb_id, season_number, watched, rating) 
            VALUES (%(user_id)s, %(imdb_id)s, %(season_number)s, %(watched)s, %(rating)s)
            ON CONFLICT (user_id, imdb_id, season_number) DO UPDATE SET watched = EXCLUDED.watched, rating = EXCLUDED.rating;
        """
        data = {
            "user_id": self.user_id,
            "imdb_id": imdb_id,
            "season_number": season_number,
            "watched": watched,
            "rating": rating,
        }
        self._upsert_watchlist_generic(query, data)

    def _upsert_watchlist_generic(self, query: str, data: dict) -> None:
        conn = db_conn()
        with conn.cursor() as cursor:
            cursor.execute(query, data)
            conn.commit()
        self.refresh_watchlist_data()

    def delete_from_watchlist(self, imdb_id: str) -> None:
        if imdb_id not in self.watchlist:
            raise ItemNotInListError(f"{imdb_id} is not in the watchlist")
        self._delete_db(imdb_id)
        self.refresh_watchlist_data()

    def _delete_db(self, imdb_id: str) -> None:
        conn = db_conn()
        with conn.cursor() as cursor:
            cursor.execute(
                "DELETE FROM watchlist WHERE user_id = %s AND imdb_id = %s CASCADE;",
                (self.user_id, imdb_id),
            )
            conn.commit()
