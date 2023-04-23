from to_consume.exceptions import ItemAlreadyInListError, ItemNotInListError
from to_consume.content import Title, write_title_records
from to_consume.streamlit.db_utils import db_conn

from psycopg2.extras import RealDictCursor


class WatchList:
    def __init__(self, user_id: int):
        self.user_id: int = user_id
        self.watchlist: dict = self.load_whole_watchlist()
        self.watchlist_titles: dict = self.load_watchlist_titles()

    def load_whole_watchlist(self) -> dict:
        return self.load_watchlist(None)

    def load_watchlist(self, imdb_id: str | None) -> dict:
        query = "SELECT imdb_id, watched, rating, created_at, updated_at FROM watchlist WHERE user_id = %s"
        params = (self.user_id,)
        if imdb_id is not None:
            query += " AND imdb_id = %s"
            params += (imdb_id,)

        conn = db_conn()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, params)
            res = cursor.fetchall()
        return self._key_by_imdb_id(res)

    def load_watchlist_titles(self) -> dict:
        conn = db_conn()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                SELECT
                    titles.*
                FROM
                    titles
                    INNER JOIN watchlist ON watchlist.imdb_id = titles.imdb_id
                    AND user_id = 1;
                """,
                (self.user_id,),
            )
            res = cursor.fetchall()
        return self._key_by_imdb_id(res)

    @staticmethod
    def _key_by_imdb_id(res: dict) -> dict:
        return {result["imdb_id"]: result for result in res}

    def add_to_watchlist(self, imdb_id: str) -> None:
        if imdb_id in self.watchlist:
            raise ItemAlreadyInListError(f"{imdb_id} is already in the watchlist")

        conn = db_conn()
        title = Title(imdb_id)
        write_title_records(conn, title)

        self._insert_db(imdb_id, False, None)
        self.watchlist |= self.load_watchlist(imdb_id)

    def _insert_db(self, imdb_id: str, watched: bool, rating: int) -> None:
        conn = db_conn()
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO watchlist (user_id, imdb_id, watched, rating) VALUES (%s, %s, %s, %s);",
                (
                    self.user_id,
                    imdb_id,
                    watched,
                    rating,
                ),
            )
            conn.commit()

    def delete_from_watchlist(self, imdb_id: str) -> None:
        if imdb_id not in self.watchlist:
            raise ItemNotInListError(f"{imdb_id} is not in the watchlist")
        self._delete_db(imdb_id)
        del self.watchlist[imdb_id]

    def _delete_db(self, imdb_id: str) -> None:
        conn = db_conn()
        with conn.cursor() as cursor:
            cursor.execute(
                "DELETE FROM watchlist WHERE user_id = %s AND imdb_id = %s;",
                (
                    self.user_id,
                    imdb_id,
                ),
            )
            conn.commit()

    def update_watchlist(self, imdb_id: str, watched: bool, rating: int) -> None:
        if imdb_id not in self.watchlist:
            raise ItemNotInListError(f"{imdb_id} is not in the watchlist")
        self.watchlist[imdb_id]["watched"] = watched
        self.watchlist[imdb_id]["rating"] = rating if watched else None
        self._update_db(imdb_id, watched, rating)

    def _update_db(self, imdb_id: str, watched: bool, rating: int) -> None:
        conn = db_conn()
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE watchlist SET watched = %s, rating = %s WHERE user_id = %s AND imdb_id = %s;",
                (
                    watched,
                    rating,
                    self.user_id,
                    imdb_id,
                ),
            )
            conn.commit()
