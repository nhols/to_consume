from typing import Any
import psycopg2
import streamlit as st


def recurse_through_dict(d: dict, keys: list[str]) -> Any:
    if not keys:
        return d
    if isinstance(d, dict):
        return recurse_through_dict(d.get(keys[0]), keys[1:])


@st.cache_resource(ttl=60 * 60 * 24, validate=lambda x: not x.closed)
def db_conn():
    secrets = st.secrets["postgres"]
    conn = psycopg2.connect(
        dbname="watchlist",
        user=secrets["PGUSER"],
        password=secrets["PGPASSWORD"],
        host=secrets["PGHOST"],
        port=secrets["PGPORT"],
    )
    return conn
