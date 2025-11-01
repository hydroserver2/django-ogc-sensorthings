from typing import Annotated
from datetime import datetime, timezone
from dateutil.parser import isoparse
from pydantic import AfterValidator


def validate_iso_time(value: str) -> str:
    """
    Validate and normalize an ISO 8601 time string to UTC.

    Ensures the string is a valid ISO 8601 timestamp and returns
    it in normalized UTC format with second-level precision.
    """

    if not isinstance(value, str):
        raise TypeError("string required")

    try:
        parsed_value = isoparse(value)
        if parsed_value.tzinfo is None:
            parsed_value = parsed_value.replace(tzinfo=timezone.utc)
        else:
            parsed_value = parsed_value.astimezone(timezone.utc)
    except TypeError:
        raise ValueError("invalid ISO time format")

    return parsed_value.isoformat(sep="T", timespec="seconds")


ISOTimeString = Annotated[
    str,
    AfterValidator(validate_iso_time),
]
"""A string type that must represent a valid ISO 8601 timestamp."""


example_iso_time_string = "2025-10-01T00:00:00Z"


def validate_iso_interval(value: str) -> str:
    """
    Validate and normalize an ISO 8601 time interval string.

    The interval must be in the format "<start>/<end>", where each
    endpoint is a valid ISO 8601 timestamp, and the start precedes the end.
    """

    if not isinstance(value, str):
        raise TypeError("string required")

    split_value = [validate_iso_time(dt_value) for dt_value in value.split("/")]

    try:
        if len(split_value) != 2 or isoparse(split_value[0]) >= isoparse(
            split_value[1]
        ):
            raise TypeError
    except TypeError:
        raise ValueError("invalid ISO interval format")

    return "/".join(split_value)


def parse_iso_interval(interval: str) -> tuple[datetime, datetime]:
    """
    Parse an ISO 8601 interval string into two datetime objects.

    The returned date times are timezone-aware and normalized to UTC.
    """

    validated_interval = validate_iso_interval(interval)
    start, end = validated_interval.split("/")
    start_datetime = isoparse(start)
    end_datetime = isoparse(end)

    return start_datetime, end_datetime


ISOIntervalString = Annotated[
    str,
    AfterValidator(validate_iso_interval),
]
"""A string type that must represent a valid ISO 8601 time interval."""


example_iso_interval_string = "2025-10-01T00:00:00Z/2025-10-31T23:59:59Z"
