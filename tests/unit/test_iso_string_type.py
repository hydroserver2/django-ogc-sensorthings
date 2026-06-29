import pytest
from datetime import datetime, timezone
from sensorthings.types.iso_string import validate_iso_time, validate_iso_interval, parse_iso_interval


# ----------------------
# Tests for validate_iso_time
# ----------------------

iso_time_cases = [
    {"id": "UTC string", "input": "2025-10-01T00:00:00Z", "expected": "2025-10-01T00:00:00+00:00"},
    {"id": "positive offset converted", "input": "2025-10-01T02:00:00+02:00", "expected": "2025-10-01T00:00:00+00:00"},
    {"id": "naive datetime assumed UTC", "input": "2025-10-01T00:00:00", "expected": "2025-10-01T00:00:00+00:00"},
    {"id": "fractional seconds ignored", "input": "2025-10-01T00:00:00.123456Z", "expected": "2025-10-01T00:00:00+00:00"},
]


@pytest.mark.parametrize(
    "case",
    iso_time_cases,
    ids=[c["id"] for c in iso_time_cases]
)
def test_validate_iso_time_success(case):
    assert validate_iso_time(case["input"]) == case["expected"]


iso_time_failure_cases = [
    {"id": "non-string input", "input": 123, "exception": TypeError},
    {"id": "None input", "input": None, "exception": TypeError},
    {"id": "invalid string", "input": "not-a-date", "exception": ValueError},
]


@pytest.mark.parametrize(
    "case",
    iso_time_failure_cases,
    ids=[c["id"] for c in iso_time_failure_cases]
)
def test_validate_iso_time_failures(case):
    with pytest.raises(case["exception"]):
        validate_iso_time(case["input"])


# ----------------------
# Tests for validate_iso_interval
# ----------------------

iso_interval_cases = [
    {"id": "UTC interval",
     "input": "2025-10-01T00:00:00Z/2025-10-31T23:59:59Z",
     "expected": "2025-10-01T00:00:00+00:00/2025-10-31T23:59:59+00:00"},
    {"id": "interval with offset",
     "input": "2025-10-01T02:00:00+02:00/2025-10-01T04:00:00+02:00",
     "expected": "2025-10-01T00:00:00+00:00/2025-10-01T02:00:00+00:00"},
    {"id": "zero-duration interval",
     "input": "2025-10-01T00:00:00Z/2025-10-01T00:00:00Z",
     "expected": "2025-10-01T00:00:00+00:00/2025-10-01T00:00:00+00:00"},
]


@pytest.mark.parametrize(
    "case",
    iso_interval_cases,
    ids=[c["id"] for c in iso_interval_cases]
)
def test_validate_iso_interval_success(case):
    assert validate_iso_interval(case["input"]) == case["expected"]


iso_interval_failure_cases = [
    {"id": "missing slash", "input": "2025-10-01T00:00:00Z", "exception": ValueError},
    {"id": "start after end", "input": "2025-10-02T00:00:00Z/2025-10-01T00:00:00Z", "exception": ValueError},
    {"id": "non-string input", "input": 123, "exception": TypeError},
]


@pytest.mark.parametrize(
    "case",
    iso_interval_failure_cases,
    ids=[c["id"] for c in iso_interval_failure_cases]
)
def test_validate_iso_interval_failures(case):
    with pytest.raises(case["exception"]):
        validate_iso_interval(case["input"])


# ----------------------
# Tests for parse_iso_interval
# ----------------------

parse_interval_cases = [
    {"id": "simple interval",
     "input": "2025-10-01T00:00:00Z/2025-10-31T23:59:59Z",
     "expected": (datetime(2025, 10, 1, 0, 0, tzinfo=timezone.utc),
                  datetime(2025, 10, 31, 23, 59, 59, tzinfo=timezone.utc))},
    {"id": "offset interval",
     "input": "2025-10-01T02:00:00+02:00/2025-10-01T04:00:00+02:00",
     "expected": (datetime(2025, 10, 1, 0, 0, tzinfo=timezone.utc),
                  datetime(2025, 10, 1, 2, 0, tzinfo=timezone.utc))},
]


@pytest.mark.parametrize(
    "case",
    parse_interval_cases,
    ids=[c["id"] for c in parse_interval_cases]
)
def test_parse_iso_interval_success(case):
    start, end = parse_iso_interval(case["input"])
    expected_start, expected_end = case["expected"]
    assert start == expected_start
    assert end == expected_end
