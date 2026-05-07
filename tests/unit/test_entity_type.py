import pytest
from sensorthings.types import EntityType


# ----------------------
# Tests for EntityType
# ----------------------

entity_type_str_cases = [
    {
        "id": "str returns set_name",
        "input": EntityType(
            name="Thing", set_name="Things", primitive_properties=["name"]
        ),
        "expected": "Things",
    }
]


@pytest.mark.parametrize(
    "case",
    entity_type_str_cases,
    ids=[c["id"] for c in entity_type_str_cases],
)
def test_entity_type_str(case):
    assert str(case["input"]) == case["expected"]
