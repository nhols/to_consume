import json
import logging

from to_consume.utils import db_conn

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
        cur.execute(
            f"INSERT INTO cache(api, endpoint, key, response) VALUES(%s,%s,%s,%s)", (api, endpoint, param, res_str)
        )
        conn.commit()
