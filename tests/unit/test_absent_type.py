import pytest
from sensorthings.types.absent import Absent, AbsentType


# ----------------------
# Tests for AbsentType identity
# ----------------------

absent_identity_cases = [
    {"id": "Absent is instance of AbsentType", "input": Absent, "expected": AbsentType},
]


@pytest.mark.parametrize(
    "case",
    absent_identity_cases,
    ids=[c["id"] for c in absent_identity_cases]
)
def test_absent_identity(case):
    assert isinstance(case["input"], case["expected"])
