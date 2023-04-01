from datetime import datetime
from to_consume.watchlist import add_to_list, load_watchlist
from to_consume.imdb import IMDBSearch, IMDBListing
from to_consume.movies_database import MoviesDatabaseTitle
import streamlit as st
from pandas import DataFrame, read_csv
import numpy as np
from to_consume.streaming_availability import get_streaming_availability_list

st.set_page_config(layout="wide")

# TODO cache api calls
# TODO title display with info, urls, rating
# TODO seasons
# TODO remove from list
# TODO refresh imdb ratings
# TODO readlist
# TODO manual entry


@st.cache_data
def st_load_watchlist() -> dict:
    try:
        return load_watchlist()
    except FileNotFoundError:
        st.write("Watchlist is empty, search for titles to add to the list")
        return {}


def st_add_to_list(imdb_id: str) -> None:
    add_to_list(imdb_id)
    st_load_watchlist.clear_cache()


with st.sidebar:
    searched_title = st.text_input("Search title", key="search_title", value="")
    if searched_title:
        scraped_title = IMDBSearch(searched_title)
        for href in scraped_title.hrefs:
            listing = IMDBListing(href)
            if listing.imdb_type == "title":
                st.write(f"[🔗]({listing.url})")
                listing_info = MoviesDatabaseTitle(listing.imdb_id)
                st.json(listing_info.title_info, expanded=False)
                if listing_info.image_url:
                    st.image(listing_info.image_url, width=200)
                st.button("Add to list", args=[listing.imdb_id], on_click=add_to_list)
    searched_title = ""


watchlist = st_load_watchlist()

selected_imdb_id = st.selectbox("View title from watchlist", options=watchlist.keys())
if selected_imdb_id:
    selected_title = watchlist[selected_imdb_id]
    st.title(selected_title["title"].title)
    st.subheader(selected_title["title"].type)
    col1, col2 = st.columns(2)
    with col1:
        st.image(selected_title["title"].image_url, width=400)
    with col2:
        st.write(f'[IMDb]({selected_title["title"].imdb_url})')
        st.write(f'[Just Watch]({selected_title["title"].just_watch_url})')
        st.write(f'[UNOGS]({selected_title["title"].unogs_url})')
        st.write(
            f"Average IMDb rating: {selected_title['title'].avg_imdb_rating}/10⭐ ({selected_title['title'].imdb_ratings_count} ratings)"
        )
# try:
#     df_watchlist = read_csv(
#         "watchlist.csv",
#         index_col="imdb_id",
#         dtype={
#             "imdb_id": str,
#             "title": str,
#             "type": str,
#             "avg_imdb_rating": float,
#             "imdb_ratings_count": "Int64",
#             "watched": bool,
#             "rating": "Int64",
#         },
#         converters={"where": lambda x: x.strip("[]").strip("'").split(",")},
#         parse_dates=["added"],
#     )
#     # st.experimental_data_editor(df_watchlist, on_change=update_watchlist, key="watchlist", use_container_width=True)
#     st.dataframe(df_watchlist, use_container_width=True)
# except:
#     pass
