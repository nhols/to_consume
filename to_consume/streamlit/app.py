from to_consume.streamlit.page_wrapper import page_wrapper
from to_consume.streamlit.rate_title import rate_titles
from to_consume.streamlit.sidebar import sidebar
from to_consume.streamlit.watchlist_df import watchlist_df
import streamlit as st

from to_consume.watchlist import WatchList


@page_wrapper
def main_app():
    sidebar()

    if st.session_state.watchlist.watchlist:
        watchlist_df(st.session_state.watchlist)
        rate_titles()
    # selected_imdb_id = st.selectbox(
    #     "View title from watchlist",
    #     options=[None] + list(st.session_state.watchlist.watchlist.keys()),
    #     format_func=lambda x: ""
    #     if x is None
    #     else getattr(st.session_state.watchlist.watchlist[x]["title"], "title", x),
    # )
    # display_title(selected_imdb_id)
