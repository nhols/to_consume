import streamlit as st
import psycopg2

from to_consume.config import Config


@st.cache_resource(ttl=60 * 60 * 24, validate=lambda x: not x.closed)
def db_conn():
    secrets = st.secrets["postgres"]
    conn = psycopg2.connect(
        dbname=Config().dbname,
        user=secrets["PGUSER"],
        password=secrets["PGPASSWORD"],
        host=secrets["PGHOST"],
        port=secrets["PGPORT"],
    )
    return conn
