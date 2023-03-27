from typing import Any


def recurse_through_dict(d: dict, keys: list[str]) -> Any:
    if not keys:
        return d
    if isinstance(d, dict):
        return recurse_through_dict(d.get(keys[0]), keys[1:])
