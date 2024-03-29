from typing import Any
import psycopg2
import streamlit as st


def recurse_through_dict(d: dict, keys: list[str]) -> Any:
    if not keys:
        return d
    if isinstance(d, dict):
        return recurse_through_dict(d.get(keys[0]), keys[1:])


def insert_dicts(
    conn, tbl: str, dict_ins: list[dict], cols: list[str] | None = None, suffix: str | None = None
) -> None:
    if cols is None:
        cols = list(dict_ins[0].keys())
    cols_comma = ", ".join(cols)
    cols_format = ", ".join(f"%({col})s" for col in cols)
    query = f"INSERT INTO {tbl} ({cols_comma}) VALUES ({cols_format})"
    if suffix is not None:
        query += f" {suffix}"
    with conn.cursor() as cur:
        cur.executemany(query, dict_ins)
        conn.commit()


def update_on_conflict_str(key: list[str], upd_cols: list[str]) -> str:
    key = ", ".join(key)
    upd_cols = get_update_cols_str(upd_cols)
    return f"ON CONFLICT ({key}) DO UPDATE {upd_cols}"


def get_update_cols_str(cols: list[str]) -> str:
    excluded_cols = [f"EXCLUDED.{col}" for col in cols]
    cols = ", ".join(cols)
    excluded_cols = ", ".join(excluded_cols)
    return f"SET ({cols}) = ({excluded_cols})"
