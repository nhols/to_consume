from to_consume.content import Title
import streamlit as st

st.cache_data


def fetch_title(imdb_id: str) -> Title:
    return Title(imdb_id)
