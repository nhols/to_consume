import logging
from typing import Callable
import streamlit as st
from to_consume.content import Title
from to_consume.streamlit.page_wrapper import page_wrapper

from to_consume.streamlit.plot_episode_ratings import plot_episode_ratings
from to_consume.streamlit.refresh import referesh_stale_records
from to_consume.streamlit.utils import fetch_title, title_selector

logger = logging.getLogger(__name__)


@page_wrapper
def select_display_title():
    selected_imdb_id = title_selector(
        "View title from watchlist",
    )
    if selected_imdb_id:
        display_title(selected_imdb_id)


def display_title(imdb_id: str) -> None:
    title = fetch_title(imdb_id)

    display_sections(title, [plot_episode_ratings, main_title])

    col1, col2 = st.columns((1, 3))

    with col1:
        if title.image_url:
            st.image(title.image_url, use_column_width=True)

    with col2:
        display_sections(
            title,
            [text_description, links, streaming_platform_links, ratings, delete_button, refresh_button],
        )

    display_sections(title, [trailer])


def display_sections(title: Title, sections=list[Callable]) -> None:
    for section in sections:
        try:
            section(title)
        except Exception as e:
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


def refresh_button(title: Title) -> None:
    st.button("Refresh", args=[[title.imdb_id]], on_click=referesh_stale_records)


def trailer(title: Title) -> None:
    st.video(title.trailer_url)


def safe_write(obj, attr):
    value = getattr(obj, attr, "")
    st.markdown(value)


def st_delete_from_list(imdb_id: str) -> None:
    st.session_state.watchlist.delete_from_watchlist(imdb_id)
    st.success(f"Deleted title {imdb_id}")
