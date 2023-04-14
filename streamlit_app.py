from to_consume.streamlit.app import main_app
from to_consume.streamlit.login import get_authenticator, get_user_id
import streamlit as st

authenticator = get_authenticator()
name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status:
    authenticator.logout("Logout", "main")
    st.write(f"Welcome *{name}*")
    st.session_state.user_id = get_user_id(username)
    main_app()
elif authentication_status is False:
    st.error("Username/password is incorrect")
elif authentication_status is None:
    st.warning("Please enter your username and password")
