import json
from datetime import datetime
from to_consume.exceptions import ItemAlreadyInListError, ItemNotInListError

from to_consume.title import Title


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
