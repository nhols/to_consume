import logging
from to_consume.streamlit.app import main_app
from to_consume.streamlit.login import get_authenticator, get_user_id
import streamlit as st


# TODO split out concept of episode from seruies with some shared base attributes
# TODO async requests
# TODO async db write/read?
# TODO dedicated watchlist table
# TODO refresh imdb ratings
# TODO streaming platform icons with links
# TODO manual entry
# TODO readlist

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs")],
)

main_app()
