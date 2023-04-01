import json
from datetime import datetime

from to_consume.title import Title


def add_to_list(imdb_id: str) -> None:
    try:
        with open("watchlist.json", "r") as f:
            watchlist = json.load(f)
    except FileNotFoundError:
        watchlist = {}
    if imdb_id in watchlist:
        raise ValueError(f"{imdb_id} is already in the watchlist")

    new_record = {
        "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "watched": False,
    }
    watchlist[imdb_id] = new_record

    with open("watchlist.json", "w") as f:
        json.dump(watchlist, f)


def load_watchlist() -> dict:
    with open("watchlist.json", "r") as f:
        watchlist = json.load(f)
    for imdb_id in watchlist.keys():
        watchlist[imdb_id]["title"] = Title(imdb_id)
    return watchlist
