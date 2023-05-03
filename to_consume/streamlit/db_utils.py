import streamlit as st
import psycopg2

from to_consume.config import Config


def check_conn(conn) -> bool:
    try:
        trans_status = conn.get_transaction_status()
        if trans_status == 3 or conn.closed == 1:
            conn.close()
            return False
        return True
    except:
        return False


@st.cache_resource(ttl=60 * 60 * 24, validate=check_conn)
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
