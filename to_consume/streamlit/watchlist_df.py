import streamlit as st
from pandas import DataFrame

from to_consume.watchlist import WatchList


def watchlist_df(watchlist: WatchList):
    df = DataFrame.from_records(list(watchlist.watchlist_titles.values()))
    st.dataframe(df, use_container_width=True)
