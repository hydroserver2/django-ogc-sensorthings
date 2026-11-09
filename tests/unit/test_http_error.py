import pytest
from ninja.errors import HttpError
from sensorthings.http import InvalidQueryError, http_error


def test_invalid_query_error_returns_400_with_message():
    error = http_error(InvalidQueryError("Invalid $filter: bad"))
    assert error.status_code == 400
    assert error.message == "Invalid $filter: bad"


def test_http_error_passes_through():
    original = HttpError(418, "Teapot")
    assert http_error(original) is original


@pytest.mark.parametrize("exception,status_code", [
    (PermissionError(), 403),
    (LookupError(), 404),
    (type("EntityNotFound", (LookupError,), {})(), 404),
    (KeyError("internal detail"), 500),
    (IndexError("internal detail"), 500),
    (NotImplementedError(), 501),
    (ValueError("internal detail"), 500),
    (TypeError("internal detail"), 500),
    (Exception("internal detail"), 500),
])
def test_exception_status_codes(exception, status_code):
    error = http_error(exception)
    assert error.status_code == status_code
    assert "internal detail" not in error.message
