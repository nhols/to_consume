from datetime import datetime
import logging
from to_consume.exceptions import ItemAlreadyInListError
from to_consume.watchlist import add_to_list, delete_from_list, load_watchlist_titles
from to_consume.imdb import IMDBSearch, IMDBListing
from to_consume.movies_database import MoviesDatabaseTitle
import streamlit as st
from pandas import DataFrame, read_csv
import numpy as np

st.set_page_config(layout="wide")

# TODO watched + rating option
# TODO seasons
# TODO season rating trendts
# TODO remove from list
# TODO refresh imdb ratings
# TODO readlist
# TODO manual entry

logging.basicConfig(level=logging.DEBUG)


@st.cache_data
def st_load_watchlist() -> dict:
    try:
        return load_watchlist_titles()
    except FileNotFoundError:
        st.write("Watchlist is empty, search for titles to add to the list")
        return {}


def st_add_to_list(imdb_id: str) -> None:
    try:
        add_to_list(imdb_id)
    except ItemAlreadyInListError:
        st.warning(f"{imdb_id} already in the list")
        return None
    st.success(f"Added {imdb_id} to the watchlist")
    st_load_watchlist.clear()  # had to manually create ~/.streamlit/cache dir to get this working - bug?


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
                st.button("Add to list", key=listing.imdb_id, args=[listing.imdb_id], on_click=st_add_to_list)
                st.markdown("""---""")
    searched_title = ""

watchlist = st_load_watchlist()


def watchlist_df():
    watchlist = st_load_watchlist()
    records = [x["title"].get_title_df_record() | {"last_updated": x["last_updated"]} for x in watchlist.values()]
    df = (
        DataFrame.from_records(records, index="imdb_id")
        .sort_values("last_updated", ascending=False)
        .drop("last_updated", axis=1)
    )
    st.dataframe(df, use_container_width=True)


watchlist_df()

selected_imdb_id = st.selectbox(
    "View title from watchlist", options=watchlist.keys(), format_func=lambda x: watchlist[x]["title"].title
)
if selected_imdb_id:
    selected_title = watchlist[selected_imdb_id]
    title = selected_title["title"]
    st.title(title.title)
    st.subheader(title.type)
    col1, col2 = st.columns(2)
    with col1:
        if title.image_url:
            st.image(title.image_url, width=400)
    with col2:
        st.write(title.overview)
        st.write(title.tagline)
        st.write(title.streaming_platforms)
        st.write(f"[IMDb]({title.imdb_url})")
        st.write(f"[Just Watch]({title.just_watch_url})")
        st.write(f"[UNOGS]({title.unogs_url})")
        st.write(
            f"Average IMDb rating: {selected_title['title'].avg_imdb_rating}⭐ ({selected_title['title'].imdb_ratings_count} ratings)"
        )
    st.video(title.trailer_url)
    st.button("Remove from list", args=[selected_imdb_id], on_click=delete_from_list)
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
