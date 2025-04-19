import pytz
from typing import Annotated, Tuple
from datetime import datetime
from dateutil.parser import isoparse
from pydantic import AfterValidator, WithJsonSchema


def validate_iso_time(value: str) -> str:
    """
    Validate and format a string as an ISO time.

    Parameters
    ----------
    value : str
        The string to validate and format.

    Returns
    -------
    str
        The validated and formatted ISO time string.

    Raises
    ------
    TypeError
        If the input is not a string.
    ValueError
        If the input string is not in a valid ISO time format.
    """

    if not isinstance(value, str):
        raise TypeError('string required')
    try:
        parsed_value = isoparse(value)
        if parsed_value.tzinfo is None:
            parsed_value = parsed_value.replace(tzinfo=pytz.UTC)
        else:
            parsed_value = parsed_value.astimezone(pytz.UTC)
    except TypeError:
        raise ValueError('invalid ISO time format')

    return parsed_value.isoformat(sep='T', timespec='seconds')


ISOTimeString = Annotated[
    str,
    AfterValidator(validate_iso_time),
    WithJsonSchema({'type': 'string'}, mode='serialization')
]


def validate_iso_interval(value: str) -> str:
    """
    Validate and format a string as an ISO interval.

    Parameters
    ----------
    value : str
        The string to validate and format.

    Returns
    -------
    str
        The validated and formatted ISO interval string.

    Raises
    ------
    TypeError
        If the input is not a string.
    ValueError
        If the input string is not in a valid ISO interval format.
    """

    if not isinstance(value, str):
        raise TypeError('string required')

    split_value = [
        validate_iso_time(dt_value) for dt_value in value.split('/')
    ]

    try:
        if len(split_value) != 2 or isoparse(split_value[0]) >= isoparse(split_value[1]):
            raise TypeError
    except TypeError:
        raise ValueError('invalid ISO interval format')

    return '/'.join(split_value)


def parse_iso_interval(interval: str) -> Tuple[datetime, datetime]:
    """
    Parse an ISO interval string into a tuple of two datetime objects.

    Parameters
    ----------
    interval : str
        The ISO interval string to parse.

    Returns
    -------
    Tuple[datetime, datetime]
        A tuple containing the start and end datetime objects.

    Raises
    ------
    ValueError
        If the interval string is not valid.
    """

    validated_interval = validate_iso_interval(interval)
    start, end = validated_interval.split('/')
    start_datetime = isoparse(start)
    end_datetime = isoparse(end)

    return start_datetime, end_datetime


ISOIntervalString = Annotated[
    str,
    AfterValidator(validate_iso_interval),
    WithJsonSchema({'type': 'string'}, mode='serialization')
]
