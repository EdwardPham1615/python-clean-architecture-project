from datetime import datetime


class ParseDateTimeException(Exception):
    pass


DATETIME_DEFAULT_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"
BIRTH_DATE_FORMAT = "%Y%m%d"


def from_str_to_dt(str_time: str, format_: str) -> datetime:
    try:
        dt = datetime.strptime(str_time, format_)
        return dt
    except Exception as exc:
        raise ParseDateTimeException(exc)


def from_dt_to_str(dt: datetime, format_: str) -> str:
    try:
        return dt.strftime(format_)
    except Exception as exc:
        raise ParseDateTimeException(exc)


def from_dt_to_int_timestamp(dt: datetime) -> int:
    return int(dt.timestamp())
