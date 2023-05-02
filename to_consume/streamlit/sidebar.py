import streamlit as st

from to_consume.streamlit.search_titles import search_add_titles


def sidebar():
    with st.sidebar:
        search_add_titles()
