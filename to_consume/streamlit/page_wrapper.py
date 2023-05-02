from to_consume.streamlit.login import get_authenticator, get_user_id
import streamlit as st
from streamlit_profiler import Profiler

from to_consume.watchlist import WatchList


def page_wrapper(wrapped_fun):
    def wrapper(*args, **kwargs):
        st.set_page_config(
            page_title="Watchlist",
            page_icon="🍿",
            layout="wide",
        )

        authenticator = get_authenticator()
        name, authentication_status, username = authenticator.login("Login", "main")

        if authentication_status:
            authenticator.logout("Logout", "sidebar")
            st.session_state.user_id = get_user_id(username)
            if "watchlist" not in st.session_state:
                st.session_state.watchlist = WatchList(st.session_state.user_id)
            st.markdown(f"{st.session_state.name}'s watchlist")
            wrapped_fun(*args, **kwargs)
        elif authentication_status is False:
            st.error("Username/password is incorrect")
        elif authentication_status is None:
            st.warning("Please enter your username and password")

    return wrapper
