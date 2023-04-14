import streamlit as st
from pandas import DataFrame


def watchlist_df():
    watchlist = st.session_state.watchlist
    records = [
        x["title"].get_title_df_record() | {"last_updated": x["last_updated"]} for x in watchlist.watchlist.values()
    ]
    df = (
        DataFrame.from_records(records, index="imdb_id")
        .sort_values("last_updated", ascending=False)
        .drop("last_updated", axis=1)
    )
    st.dataframe(df, use_container_width=True)
