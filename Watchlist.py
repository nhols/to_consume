import logging
from to_consume.streamlit.app import main_app
from to_consume.streamlit.login import get_authenticator, get_user_id
import streamlit as st

# TODO better rating interface
# TODO view but not write access to other people's lists
# TODO sort out db conn - sqlalchemy?
# TODO async db write/read?
# TODO refresh imdb ratings
# TODO streaming platform icons with links
# TODO readlist

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs")],
)

main_app()
