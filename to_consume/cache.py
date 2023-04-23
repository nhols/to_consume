import json
import logging
import streamlit as st
from to_consume.utils import db_conn
from psycopg2.errors import UniqueViolation

logger = logging.getLogger(__name__)


def cache_db(api: str, endpoint: str):
    def decorator(original_func):
        def new_func(param):
            res = fetch_from_cache(api, endpoint, param)
            if res is not None:
                return res

            res = original_func(param)
            if res is not None:
                write_to_cache(api, endpoint, param, res)
            return res

        return new_func

    return decorator


@st.cache_resource
def fetch_entire_cache():
    logger.info("Fetching entire cache")
    conn = db_conn()
    with conn.cursor() as cur:
        cur.execute(f"SELECT api, endpoint, key, response FROM cache")
        res = cur.fetchall()
    cache_dict = {}
    for api, endpoint, param, response in res:
        cache_key = (api, endpoint, param)
        cache_dict[cache_key] = response
    return cache_dict


def _fetch_from_cache(api: str, endpoint: str, param: str) -> dict | None:
    cache = fetch_entire_cache()
    res = cache.get((api, endpoint, param))
    if res is not None:
        logging.info(f"cached value fetched for {api}, {endpoint}, {param}")
        return res
    return None


def fetch_from_cache(api: str, endpoint: str, param: str) -> dict | None:
    conn = db_conn()
    with conn.cursor() as cur:
        cur.execute(f"SELECT response FROM cache WHERE api = %s AND endpoint = %s AND key = %s", (api, endpoint, param))
        res = cur.fetchone()
    if res:
        logging.info(f"cached value fetched for {api}, {endpoint}, {param}")
        return res[0]
    return None


def write_to_cache(api: str, endpoint: str, param: str, res: dict) -> None:
    logging.info(f"Writing retrieved result for {api}, {endpoint}, {param}")
    res_str = json.dumps(res)
    conn = db_conn()
    with conn.cursor() as cur:
        try:  # TODO upsert
            cur.execute(
                f"INSERT INTO cache(api, endpoint, key, response) VALUES(%s,%s,%s,%s)", (api, endpoint, param, res_str)
            )
            conn.commit()
        except UniqueViolation:
            logging.warning(f"Duplicate entry for {api}, {endpoint}, {param}, cache could be out of date")
            conn.rollback()
