import json
from datetime import datetime
from to_consume.exceptions import ItemAlreadyInListError, ItemNotInListError
import streamlit as st
from to_consume.title import Title
from to_consume.utils import db_conn


def add_to_list(imdb_id: str) -> None:
    watchlist = load_watchlist()

    if imdb_id in watchlist:
        raise ItemAlreadyInListError(f"{imdb_id} is already in the watchlist")

    new_record = {
        "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "watched": False,
        "rating": None,
    }
    watchlist[imdb_id] = new_record
    write_watchlist(watchlist)


def delete_from_list(imdb_id: str) -> None:
    watchlist = load_watchlist()
    if imdb_id not in watchlist:
        raise ItemNotInListError(f"{imdb_id} is not in the watchlist")
    del watchlist[imdb_id]
    write_watchlist(watchlist)


def update_watchlist(imdb_id: str, watched: bool, rating: int) -> None:
    watchlist = load_watchlist()
    if imdb_id not in watchlist:
        raise ItemNotInListError(f"{imdb_id} is not in the watchlist")
    watchlist[imdb_id]["watched"] = watched
    watchlist[imdb_id]["rating"] = rating if watched else None
    watchlist[imdb_id]["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    write_watchlist(watchlist)


def load_watchlist() -> dict:
    try:
        with open("watchlist.json", "r") as f:
            watchlist = json.load(f)
    except FileNotFoundError:
        watchlist = {}
    return watchlist


def write_watchlist(watchlist: dict) -> None:
    with open("watchlist.json", "w") as f:
        json.dump(watchlist, f)


def load_watchlist_titles() -> dict:
    with open("watchlist.json", "r") as f:
        watchlist = json.load(f)
    for imdb_id in watchlist.keys():
        watchlist[imdb_id]["title"] = Title(imdb_id)
    return watchlist


class WatchList:
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.watchlist = self.load_whole_watchlist(user_id)

    @st.cache_data
    def load_whole_watchlist(self, user_id: int, imdb_id: str | None) -> dict:
        return self.load_watchlist(user_id, None)

    @staticmethod
    def load_watchlist(user_id: int, imdb_id: str | None) -> dict:
        query = "SELECT imdb_id, watched, rating, created_at, updated_at FROM watchlist WHERE user_id = %s"
        if imdb_id is not None:
            query += " AND imdb_id = %s"
        conn = db_conn()
        with conn.cursor() as cursor:
            cursor.execute(query, (user_id, imdb_id))
            res = cursor.fetchall()
        return {
            imdb_id: {"watched": watched, "rating": rating, "created": created_at, "last_updated": updated_at}
            for imdb_id, watched, rating, created_at, updated_at in res
        }

    def add_to_watchlist(self, imdb_id: str, user_id: int) -> None:
        if imdb_id in self.watchlist:
            raise ItemAlreadyInListError(f"{imdb_id} is already in the watchlist")
        self._insert_db(imdb_id, user_id, False, None)
        self.watchlist |= self.load_watchlist(user_id, imdb_id)

    def _insert_db(self, imdb_id: str, user_id: int, watched: bool, rating: int) -> None:
        conn = db_conn()
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO watchlist (user_id, imdb_id, watched, rating) VALUES (%s, %s, %s, %s);",
                (user_id, imdb_id, watched, rating),
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
            cursor.execute("DELETE FROM watchlist WHERE imdb_id = %s;", (imdb_id,))
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
                "UPDATE watchlist SET watched = %s, rating = %s WHERE imdb_id = %s;", (watched, rating, imdb_id)
            )
            conn.commit()

    def __reduce__(self) -> str | tuple[Any, ...]:
        return WatchList, (self.user_id,)
