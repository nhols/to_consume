from to_consume.utils import db_conn
import streamlit_authenticator as stauth


def get_auth_config():
    conn = db_conn()
    with conn.cursor() as cur:
        cur.execute("SELECT username, password FROM users")
        config = cur.fetchall()
    return {"usernames": {name: {"email": "", "name": name, "password": password} for name, password in config}}


def get_user_id(username: str):
    conn = db_conn()
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM users WHERE username=%s", (username,))
        user_id = cur.fetchone()[0]
    return user_id


def get_authenticator():
    return stauth.Authenticate(
        get_auth_config(),
        cookie_name="cookie_monster",
        key="cookie_monster",
        cookie_expiry_days=100,
    )
