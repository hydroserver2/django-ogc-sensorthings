from typing import Any


def remove_whitespace(value: Any) -> Any:
    """
    Validation for whitespace values.

    Checks if string values are blank or only whitespace and converts them to NoneType.

    Parameters
    ----------
    value : Any
        The input value

    Returns
    -------
    Any
        The output value.
    """

    if isinstance(value, str):
        if value == '' or value.isspace():
            value = None
        else:
            value = value.strip()

    return value
