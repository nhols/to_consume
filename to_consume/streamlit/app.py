from to_consume.streamlit.watchlist_df import watchlist_df
from to_consume.streamlit.search_titles import search_titles
from to_consume.streamlit.display_title import display_title
import streamlit as st

from to_consume.watchlist import WatchList


def main_app():
    if "watchlist" not in st.session_state:
        st.session_state.watchlist = WatchList(st.session_state.user_id)

    with st.sidebar:
        search_titles()

    if st.session_state.watchlist.watchlist:
        watchlist_df()

    selected_imdb_id = st.selectbox(
        "View title from watchlist",
        options=[None] + list(st.session_state.watchlist.watchlist.keys()),
        format_func=lambda x: ""
        if x is None
        else getattr(st.session_state.watchlist.watchlist[x]["title"], "title", x),
    )
    display_title(selected_imdb_id)
