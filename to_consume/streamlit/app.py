from to_consume.streamlit.page_wrapper import page_wrapper
from to_consume.streamlit.rate_title import rate_titles
from to_consume.streamlit.refresh import check_refresh_stale_records
from to_consume.streamlit.sidebar import sidebar
from to_consume.streamlit.watchlist_df import watchlist_df
import streamlit as st

from to_consume.watchlist import WatchList


@page_wrapper
def main_app():
    sidebar()
    check_refresh_stale_records()
    if st.session_state.watchlist.watchlist:
        watchlist_df(st.session_state.watchlist)
        rate_titles()
