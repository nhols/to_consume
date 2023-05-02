from time import sleep
import streamlit as st
from to_consume.content import Title
from to_consume.streamlit.utils import fetch_title, title_selector


def rate_titles():
    imdb_id = title_selector("Rate title from watchlist")
    if imdb_id:
        rate_title(imdb_id)


@st.cache_data
def fetch_title_seasons(imdb_id: str) -> list[int]:
    title = fetch_title(imdb_id)
    return title.get_season_numbers()


def rate_title(imdb_id: str):
    title_seasons = fetch_title_seasons(imdb_id)
    answers = {}
    with st.form("rating"):
        answers[(imdb_id, None)] = main_watched_checkbox_rating_slider(imdb_id)
        if title_seasons:
            with st.expander("Seasons"):
                for season in title_seasons:
                    answers[(imdb_id, season)] = season_watched_checkbox_rating_slider(imdb_id, season)
        st.form_submit_button("Update ratings", on_click=st_update_watchlist_all, args=(answers,))


def main_watched_checkbox_rating_slider(imdb_id: str) -> None:
    status = st.session_state.watchlist.get_status(imdb_id)
    return watched_checkbox_rating_slider(imdb_id, *status)


def season_watched_checkbox_rating_slider(imdb_id: str, season: int) -> None:
    status = st.session_state.watchlist.get_season_status(imdb_id, season)
    return watched_checkbox_rating_slider(imdb_id, *status, season)


def watched_checkbox_rating_slider(imdb_id: str, watched: bool, rating: int, season: int | None = None) -> None:
    text = "Title" if season is None else f"Season {season}"
    col0, col1, col2 = st.columns([1, 1, 4])
    col0.markdown(text)
    watched = col1.checkbox("Watched", value=watched, key=f"watched_checkbox_{imdb_id}_{season}")
    rating = col2.slider(
        "Rating",
        value=rating,
        min_value=1,
        max_value=100,
        # disabled=not watched,
        key=f"rating_slider_{imdb_id}_{season}",
    )
    st.markdown("---")
    return watched, rating


def st_update_watchlist_all(answers: dict[tuple[str, int | None], tuple[bool, int]]) -> None:
    for (imdb_id, season), (watched, rating) in answers.items():
        st_update_watchlist(imdb_id, season, watched, rating)
    sleep(1)


def st_update_watchlist(imdb_id: str, season: int | None, watched: bool, rating: int) -> None:
    if not watched:
        rating = None
    if season:
        st.session_state.watchlist.upsert_watchlist_seasons(
            imdb_id,
            season,
            watched,
            rating,
        )
    else:
        st.session_state.watchlist.upsert_watchlist(imdb_id, watched, rating)
    season_msg = f"season {season}" if season else ""
    st.success(f"Updated title status {season_msg} {imdb_id}: watched={watched}, rating={rating}")
