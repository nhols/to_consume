from datetime import datetime
import logging
from random import randint
from to_consume.exceptions import ItemAlreadyInListError
from to_consume.title import Title
from to_consume.watchlist import add_to_list, delete_from_list, load_watchlist_titles, update_watchlist
from to_consume.imdb import IMDBSearch, IMDBListing
from to_consume.movies_database import MoviesDatabaseTitle
import streamlit as st
from pandas import DataFrame, read_csv
import numpy as np
import plotly.express as px
import streamlit_authenticator as stauth

st.set_page_config(
    page_title="Watchlist",
    page_icon="🎬",
    layout="wide",
)

# TODO seasons
# TODO refresh imdb ratings
# TODO readlist
# TODO manual entry
# TODO streaming platform icons with links
# TODO users
# TODO persist in db
logging.basicConfig(level=logging.DEBUG)


# see https://github.com/streamlit/streamlit/issues/6310
@st.cache_data(persist=True)
def workaround():
    return True


x = workaround()


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
    st_load_watchlist.clear()


def st_update_watchlist(imdb_id: str, watched: bool, rating: int) -> None:
    update_watchlist(imdb_id, watched, rating)
    st.success(f"Updated title {imdb_id}")
    st_load_watchlist.clear()


def st_delete_from_list(imdb_id: str) -> None:
    delete_from_list(imdb_id)
    st.success(f"Deleted title {imdb_id}")
    st_load_watchlist.clear()


def add_imdb_ids(imdb_ids: str) -> None:
    for imdb_id in imdb_ids.split(","):
        st_add_to_list(imdb_id)


def searched_title_add(searched_title: str):
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


def watchlist_df():
    watchlist = st_load_watchlist()
    records = [x["title"].get_title_df_record() | {"last_updated": x["last_updated"]} for x in watchlist.values()]
    df = (
        DataFrame.from_records(records, index="imdb_id")
        .sort_values("last_updated", ascending=False)
        .drop("last_updated", axis=1)
    )
    st.dataframe(df, use_container_width=True)


def plot_episode_ratings(title: Title):
    df = title.get_seasons_df()
    if not df.empty:
        fig = px.line(
            df,
            x=df.index,
            y="imdb_rating",
            color="season",
            title="Episode ratings",
            hover_data=["season", "episode", "imdb_rating", "imdb_ratings_count", "overview"],
            markers=True,
        )
        fig.update_xaxes(visible=False)
        fig.update_yaxes(showgrid=False)
        st.plotly_chart(fig, use_container_width=True)


def safe_write(obj, attr):
    value = getattr(obj, attr, "")
    st.write(value)


def display_title(selected_imdb_id):
    if selected_imdb_id:
        selected_title = st.session_state.watchlist[selected_imdb_id]
        title = selected_title["title"]
        plot_episode_ratings(title)
        st.title(title.title)
        st.subheader(title.type)
        col1, col2 = st.columns(2)
        with col1:
            if title.image_url:
                st.image(title.image_url, width=400)
        with col2:
            safe_write(title, "overview")
            safe_write(title, "tagline")
            st.markdown("""---""")
            for platform, link in title.streaming_links.items():
                st.write(f"[{platform}]({link})")
            st.markdown("""---""")
            st.write(f"[IMDb]({title.imdb_url})")
            st.write(f"[Just Watch]({title.just_watch_url})")
            st.write(f"[UNOGS]({title.unogs_url})")
            st.markdown("""---""")
            st.write(f"Average IMDb rating: {title.avg_imdb_rating}⭐ ({title.imdb_ratings_count} ratings)")
            st.markdown("""---""")
            watched = st.checkbox("Watched", value=selected_title["watched"])
            rating = st.slider(
                "Rating", value=selected_title["rating"], min_value=1, max_value=100, disabled=not watched
            )
            st.button(label="Update status", args=[selected_imdb_id, watched, rating], on_click=st_update_watchlist)
            st.markdown("""---""")
            st.button("Remove from list", args=[selected_imdb_id], on_click=delete_from_list)
        try:
            st.video(title.trailer_url)
        except:
            pass


def main_app():
    with st.sidebar:
        imdb_ids = st.text_input("Add titles by their IMDb ID", help="Separate multiple IDs with commas")
        if imdb_ids:
            add_imdb_ids(imdb_ids)
        imdb_ids = ""
        searched_title = st.text_input("Search title", key="search_title", value="")
        if searched_title:
            searched_title_add(searched_title)
        searched_title = ""

    st.session_state.watchlist = st_load_watchlist()

    if st.session_state.watchlist:
        watchlist_df()

    selected_imdb_id = st.selectbox(
        "View title from watchlist",
        options=[None] + list(st.session_state.watchlist.keys()),
        format_func=lambda x: "" if x is None else getattr(st.session_state.watchlist[x]["title"], "title", x),
    )
    display_title(selected_imdb_id)


auth_config = {
    "usernames": {
        "neno": {
            "email": "",
            "name": "neno",
            "password": "$2b$12$KeaV6dBJsCfHksgDzXumhu/QvfCQ/2mc7Kfyrs9ce/X8VwGlcEfH2",
        }
    },
}
authenticator = stauth.Authenticate(
    auth_config,
    cookie_name="cookie_monster",
    key="cookie_monster",
    cookie_expiry_days=100,
)

name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status:
    authenticator.logout("Logout", "main")
    st.write(f"Welcome *{name}*")
    main_app()
elif authentication_status is False:
    st.error("Username/password is incorrect")
elif authentication_status is None:
    st.warning("Please enter your username and password")
