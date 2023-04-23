import streamlit as st

from to_consume.streamlit.search_titles import search_add_titles


def sidebar():
    with st.sidebar:
        st.markdown(f"{st.session_state.name}'s watchlist")
        search_add_titles()
