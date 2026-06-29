import traceback
from ninja.errors import HttpError


get_collection_error_responses: dict[int, type[str]] = {
    400: str,
    401: str,
    422: str,
}

get_entity_error_responses: dict[int, type[str]] = {
    400: str,
    401: str,
    403: str,
    404: str,
    422: str,
}

create_entity_error_responses: dict[int, type[str]] = {
    400: str,
    401: str,
    403: str,
    404: str,
    422: str,
}

update_entity_error_responses: dict[int, type[str]] = {
    400: str,
    401: str,
    403: str,
    404: str,
    422: str,
}

delete_entity_error_responses: dict[int, type[str]] = {
    400: str,
    401: str,
    403: str,
    404: str,
    422: str,
}


def http_error(exception: Exception) -> HttpError:
    """Map a Python exception to an HTTP error response."""

    traceback.print_exc()

    if isinstance(exception, HttpError):
        return exception
    elif isinstance(exception, (ValueError, TypeError)):
        return HttpError(400, "Bad request")
    elif isinstance(exception, PermissionError):
        return HttpError(403, "Permission denied")
    elif isinstance(exception, LookupError):
        return HttpError(404, "Not found")
    elif isinstance(exception, NotImplementedError):
        return HttpError(501, "Not implemented")
    else:
        return HttpError(500, "Internal server error")
