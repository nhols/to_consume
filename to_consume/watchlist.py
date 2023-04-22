from venv import logger
from to_consume.exceptions import ItemAlreadyInListError, ItemNotInListError
from to_consume.title import Title
from to_consume.utils import db_conn


class WatchList:
    def __init__(self, user_id: int):
        self.user_id: int = user_id
        self.watchlist: dict = self.load_whole_watchlist()

    def load_whole_watchlist(self) -> dict:
        return self.load_watchlist(self.user_id, None)

    @staticmethod
    def load_watchlist(user_id: int, imdb_id: str | None) -> dict:
        query = "SELECT imdb_id, watched, rating, created_at, updated_at FROM watchlist WHERE user_id = %s"
        params = (user_id,)
        if imdb_id is not None:
            query += " AND imdb_id = %s"
            params += (imdb_id,)

        conn = db_conn()
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            res = cursor.fetchall()

        def catch(x):
            try:
                return Title(x)
            except:
                logger.error(f"Error loading title {x}")

        return {
            imdb_id: {
                "watched": watched,
                "rating": rating,
                "created": created_at,
                "last_updated": updated_at,
                "title": catch(imdb_id),
            }
            for imdb_id, watched, rating, created_at, updated_at in res
        }

    def add_to_watchlist(self, imdb_id: str) -> None:
        if imdb_id in self.watchlist:
            raise ItemAlreadyInListError(f"{imdb_id} is already in the watchlist")
        self._insert_db(imdb_id, False, None)
        self.watchlist |= self.load_watchlist(self.user_id, imdb_id)

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

    def __reduce__(self):
        return WatchList, (self.user_id,)
