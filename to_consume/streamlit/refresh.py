import logging
from to_consume.cache import delete_from_cache
from to_consume.content import Title, write_title_records
from to_consume.refresh import get_stale_records
from to_consume.streamlit.config import CONFIG
from to_consume.streamlit.db_utils import db_conn


def check_refresh_stale_records():
    conn = db_conn()
    stale_record_ids = get_stale_records(conn, CONFIG["days_lower_threshold"], CONFIG["staleness_upper_threshold"])
    if stale_record_ids:
        logging.info(f"Refreshing stale records {stale_record_ids}")
        referesh_stale_records(stale_record_ids)
    else:
        logging.info("No stale records found")


def referesh_stale_records(stale_ids: list[str]):
    delete_from_cache(stale_ids)
    for imdb_id in stale_ids:
        title = Title(imdb_id)
        conn = db_conn()
        write_title_records(conn, title)
