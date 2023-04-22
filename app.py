import logging
from to_consume.streamlit.app import main_app
from to_consume.streamlit.login import get_authenticator, get_user_id
import streamlit as st
from streamlit_profiler import Profiler

from to_consume.utils import db_conn

# TODO split out concept of episode from seruies with some shared base attributes
# TODO async requests
# TODO async db write/read?
# TODO dedicated watchlist table
# TODO refresh imdb ratings
# TODO streaming platform icons with links
# TODO manual entry
# TODO readlist
st.set_page_config(
    page_title="Watchlist",
    page_icon="🍿",
    layout="wide",
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs")],
)
authenticator = get_authenticator()
name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status:
    authenticator.logout("Logout", "main")
    st.write(f"Welcome *{name}*")
    st.session_state.user_id = get_user_id(username)
    with Profiler():
        main_app()
elif authentication_status is False:
    st.error("Username/password is incorrect")
elif authentication_status is None:
    st.warning("Please enter your username and password")
