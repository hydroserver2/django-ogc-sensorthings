import pytest


pytestmark = pytest.mark.django_db

CORE_ENTITY_SET_NAMES = [
    "Things",
    "Locations",
    "HistoricalLocations",
    "Datastreams",
    "Sensors",
    "ObservedProperties",
    "Observations",
    "FeaturesOfInterest",
]


class TestGetRoot:

    def test_returns_200(self, client):
        response = client.get("/")
        assert response.status_code == 200

    def test_response_has_value_and_server_settings(self, client):
        body = client.get("/").json()
        assert "value" in body
        assert "serverSettings" in body

    def test_conformance_is_non_empty_list_of_strings(self, client):
        conformance = client.get("/").json()["serverSettings"]["conformance"]
        assert isinstance(conformance, list)
        assert len(conformance) > 0
        assert all(isinstance(uri, str) for uri in conformance)

    def test_value_contains_all_core_entity_sets(self, client):
        value = client.get("/").json()["value"]
        names = {item["name"] for item in value}
        assert set(CORE_ENTITY_SET_NAMES).issubset(names)

    def test_value_items_have_name_and_url(self, client):
        value = client.get("/").json()["value"]
        for item in value:
            assert "name" in item
            assert "url" in item

    def test_value_urls_contain_entity_set_name(self, client):
        value = client.get("/").json()["value"]
        for item in value:
            assert item["name"] in item["url"]

    def test_no_duplicate_entity_sets_in_value(self, client):
        value = client.get("/").json()["value"]
        names = [item["name"] for item in value]
        assert len(names) == len(set(names))