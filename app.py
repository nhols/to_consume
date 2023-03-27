from datetime import datetime
from to_consume.watchlist import add_to_list
from to_consume.imdb import IMDBSearch, IMDBListing
from to_consume.movies_database import Listing
import streamlit as st
from pandas import DataFrame, read_csv
import numpy as np
from to_consume.streaming_availability import get_streaming_availability_list

st.set_page_config(layout="wide")

# TODO cache api calls
# TODO title display with info, urls, rating
# TODO seasons

with st.sidebar:
    searched_title = st.text_input("Search title", key="search_title", value="")
    if searched_title:
        scraped_title = IMDBSearch(searched_title)
        for href in scraped_title.hrefs:
            listing = IMDBListing(href)
            if listing.imdb_type == "title":
                st.write(f"[🔗]({listing.url})")
                listing_info = Listing(listing.imdb_id)
                st.json(listing_info.title_info, expanded=False)
                if listing_info.image_url:
                    st.image(listing_info.image_url, width=200)
                st.button("Add to list", key=listing.imdb_id, args=[listing_info], on_click=add_to_list)
    searched_title = ""


def update_watchlist():
    st.session_state["watchlist"]


try:
    df_watchlist = read_csv(
        "watchlist.csv",
        index_col="imdb_id",
        dtype={
            "imdb_id": str,
            "title": str,
            "type": str,
            "avg_imdb_rating": float,
            "imdb_ratings_count": "Int64",
            "watched": bool,
            "rating": "Int64",
        },
        converters={"where": lambda x: x.strip("[]").strip("'").split(",")},
        parse_dates=["added"],
    )
    # st.experimental_data_editor(df_watchlist, on_change=update_watchlist, key="watchlist", use_container_width=True)
    st.dataframe(df_watchlist, use_container_width=True)
except:
    pass
