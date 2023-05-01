import streamlit as st
from pandas import DataFrame

from to_consume.watchlist import WatchList


def watchlist_df(watchlist: WatchList):
    keep_cols = ["imdb_id", "title", "title_type", "date_released", "imdb_rating", "imdb_rating_count"]
    df = DataFrame.from_records(list(watchlist.watchlist_titles.values())).loc[:, keep_cols].set_index("imdb_id")
    df_watchlist = (
        DataFrame.from_records(list(watchlist.watchlist.values()))
        .loc[:, ["imdb_id", "updated_at"]]
        .set_index("imdb_id")
    )
    df = df.join(df_watchlist, how="left").sort_values("updated_at", ascending=False)
    st.dataframe(df.drop(columns="updated_at"), use_container_width=True)
