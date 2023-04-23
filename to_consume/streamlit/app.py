from to_consume.streamlit.sidebar import sidebar
from to_consume.streamlit.watchlist_df import watchlist_df
from to_consume.streamlit.display_title import select_display_title
import streamlit as st

from to_consume.watchlist import WatchList


def main_app():
    if "watchlist" not in st.session_state:
        st.session_state.watchlist = WatchList(st.session_state.user_id)

    sidebar()

    if st.session_state.watchlist.watchlist:
        watchlist_df(st.session_state.watchlist)

    select_display_title()
    # selected_imdb_id = st.selectbox(
    #     "View title from watchlist",
    #     options=[None] + list(st.session_state.watchlist.watchlist.keys()),
    #     format_func=lambda x: ""
    #     if x is None
    #     else getattr(st.session_state.watchlist.watchlist[x]["title"], "title", x),
    # )
    # display_title(selected_imdb_id)
