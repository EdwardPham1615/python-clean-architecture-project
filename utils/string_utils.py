import orjson


def from_str_to_dict(json_str: str) -> dict:
    return orjson.loads(json_str)
