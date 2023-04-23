import logging
from typing import Callable
import streamlit as st
from to_consume.content import Title

from to_consume.streamlit.plot_episode_ratings import plot_episode_ratings
from to_consume.streamlit.utils import fetch_title

logger = logging.getLogger(__name__)


def select_display_title():
    selected_imdb_id = st.selectbox(
        "View title from watchlist",
        options=[None] + list(st.session_state.watchlist.watchlist.keys()),
        format_func=lambda x: "" if x is None else st.session_state.watchlist.watchlist_titles[x].get("title", x),
    )
    if selected_imdb_id:
        display_title(selected_imdb_id)


def display_title(imdb_id: str) -> None:
    title = fetch_title(imdb_id)

    display_sections(title, [plot_episode_ratings, main_title])

    col1, col2 = st.columns((1, 3))

    with col1:
        if title.image_url:
            st.image(title.image_url, width=400)

    with col2:
        display_sections(
            title,
            [
                main_watched_checkbox_rating_slider,
                text_description,
                links,
                streaming_platform_links,
                ratings,
                delete_button,
                seasons_watched_checkbox_rating_slider,
            ],
        )

    display_sections(title, [trailer])
    # watched = st.checkbox("Watched", value=title["watched"])
    # rating = st.slider("Rating", value=title["rating"], min_value=1, max_value=100, disabled=not watched)
    # st.button(label="Update status", args=[selected_imdb_id, watched, rating], on_click=st_update_watchlist)


def display_sections(title: Title, sections=list[Callable]) -> None:
    for section in sections:
        try:
            section(title)
        except Exception as e:
            raise e
            logger.error(f"Error in section {section.__name__}: {e}")
            st.error("Issue loading this section")
        st.markdown("---")


def main_title(title: Title) -> None:
    st.title(title.title)
    st.subheader(title.type)
    safe_write(title, "tagline")


def text_description(title: Title) -> None:
    safe_write(title, "overview")


def links(title: Title) -> None:
    st.markdown(f"[IMDb]({title.imdb_url})")
    st.markdown(f"[Just Watch]({title.just_watch_url})")
    st.markdown(f"[UNOGS]({title.unogs_url})")


def streaming_platform_links(title: Title) -> None:
    for platform, url in title.streaming_links.items():
        st.markdown(f"[{platform}]({url})")


def ratings(title: Title) -> None:
    st.markdown(f"Average IMDb rating: {title.avg_imdb_rating}⭐ ({title.imdb_ratings_count} ratings)")


def delete_button(title: Title) -> None:
    st.button("Remove from list", args=[title.imdb_id], on_click=st_delete_from_list)


def trailer(title: Title) -> None:
    st.video(title.trailer_url)


def safe_write(obj, attr):
    value = getattr(obj, attr, "")
    st.markdown(value)


def main_watched_checkbox_rating_slider(title: Title) -> None:
    status = st.session_state.watchlist.get_status(title.imdb_id)
    watched_checkbox_rating_slider(title.imdb_id, *status)


def seasons_watched_checkbox_rating_slider(title: Title) -> None:
    seasons = title.get_season_numbers()
    if not seasons:
        return
    with st.expander(f"Seasons", expanded=False):
        for season in seasons:
            status = st.session_state.watchlist.get_season_status(title.imdb_id, season)
            watched_checkbox_rating_slider(title.imdb_id, *status, season)


def watched_checkbox_rating_slider(imdb_id: str, watched: bool, rating: int, season: int | None = None) -> None:
    watched = st.checkbox("Watched", value=watched, key=f"watched_checkbox_{imdb_id}_{season}")
    rating = st.slider(
        "Rating",
        value=rating,
        min_value=1,
        max_value=100,
        disabled=not watched,
        key=f"rating_slider_{imdb_id}_{season}",
    )
    with st.form(key=f"watched_checkbox_rating_slider_imdb_id_{season}"):
        st.form_submit_button(
            label="Update status", args=[imdb_id, watched, rating, season], on_click=st_update_watchlist
        )


def st_update_watchlist(imdb_id: str, watched: bool, rating: int, season: int | None) -> None:
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


def st_delete_from_list(imdb_id: str) -> None:
    st.session_state.watchlist.delete_from_watchlist(imdb_id)
    st.success(f"Deleted title {imdb_id}")
