import json


def persist_to_file(file_name):
    def decorator(original_func):
        try:
            cache = json.load(open(file_name, "r"))
        except (IOError, ValueError):
            cache = {}

        def new_func(param):
            if param not in cache:
                res = original_func(param)
                if res is not None:
                    cache[param] = res
                    json.dump(cache, open(file_name, "w"))
            return cache.get(param)

        return new_func

    return decorator
