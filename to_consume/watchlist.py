from datetime import datetime
from pandas import DataFrame

from to_consume.movies_database import Listing
from to_consume.streaming_availability import get_streaming_availability_list


def add_to_list(listing_info: Listing) -> None:
    df = DataFrame([listing_info.get_watchlist_record()])
    df["watched"] = False
    df["rating"] = None
    df["where"] = [get_streaming_availability_list(listing_info.imdb_id)]
    df["added"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df.to_csv("watchlist.csv", mode="a", header=False, index=False)
