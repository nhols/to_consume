import streamlit as st
from to_consume.content import Title
import streamlit as st

st.cache_data


@st.cache_data
def fetch_title(imdb_id: str) -> Title:
    return Title(imdb_id)


def title_selector(title_text: str):
    return st.selectbox(
        title_text,
        options=[None] + list(st.session_state.watchlist.watchlist.keys()),
        format_func=lambda x: "" if x is None else st.session_state.watchlist.watchlist_titles[x].get("title", x),
    )
