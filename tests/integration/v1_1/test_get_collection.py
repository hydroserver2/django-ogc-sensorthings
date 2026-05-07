import pytest
from tests.factories.v1_1.django import (
    create_test_thing,
    create_test_location,
    create_test_historical_location,
    create_test_sensor,
    create_test_observed_property,
    create_test_datastream,
    create_test_feature_of_interest,
    create_test_observation,
)


pytestmark = pytest.mark.django_db


class TestGetThingCollection:

    def test_empty_collection(self, client):
        response = client.get("/Things")
        assert response.status_code == 200
        assert response.json() == {"value": []}

    def test_returns_created_entity(self, client):
        create_test_thing(name="My Thing")
        response = client.get("/Things")
        body = response.json()
        assert len(body["value"]) == 1
        assert body["value"][0]["name"] == "My Thing"

    def test_returns_multiple_entities(self, client):
        create_test_thing(name="Thing A")
        create_test_thing(name="Thing B")
        response = client.get("/Things")
        assert len(response.json()["value"]) == 2

    def test_response_includes_self_link(self, client):
        create_test_thing()
        entity = client.get("/Things").json()["value"][0]
        assert "@iot.selfLink" in entity
        assert "Things" in entity["@iot.selfLink"]

    def test_response_includes_nav_links(self, client):
        create_test_thing()
        entity = client.get("/Things").json()["value"][0]
        assert "Locations@iot.navigationLink" in entity
        assert "Datastreams@iot.navigationLink" in entity
        assert "HistoricalLocations@iot.navigationLink" in entity

    def test_count_included_when_requested(self, client):
        create_test_thing()
        create_test_thing()
        body = client.get("/Things?$count=true").json()
        assert body["@iot.count"] == 2

    def test_count_not_included_by_default(self, client):
        create_test_thing()
        body = client.get("/Things").json()
        assert "@iot.count" not in body

    def test_top_limits_results(self, client):
        create_test_thing(name="Thing A")
        create_test_thing(name="Thing B")
        body = client.get("/Things?$top=1").json()
        assert len(body["value"]) == 1

    def test_top_adds_next_link_when_more_results_exist(self, client):
        create_test_thing()
        create_test_thing()
        body = client.get("/Things?$top=1").json()
        assert "@iot.nextLink" in body

    def test_skip_offsets_results(self, client):
        create_test_thing(name="Thing A")
        create_test_thing(name="Thing B")
        body = client.get("/Things?$top=100&$skip=1").json()
        assert len(body["value"]) == 1

    def test_no_next_link_when_results_exhausted(self, client):
        create_test_thing()
        body = client.get("/Things?$top=100").json()
        assert "@iot.nextLink" not in body

    def test_select_returns_only_requested_fields(self, client):
        create_test_thing(name="Selectable Thing", description="Should not appear")
        entity = client.get("/Things?$select=name").json()["value"][0]
        assert "name" in entity
        assert "description" not in entity

    def test_orderby_ascending(self, client):
        create_test_thing(name="Beta")
        create_test_thing(name="Alpha")
        names = [e["name"] for e in client.get("/Things?$orderby=name asc").json()["value"]]
        assert names == sorted(names)

    def test_orderby_descending(self, client):
        create_test_thing(name="Alpha")
        create_test_thing(name="Beta")
        names = [e["name"] for e in client.get("/Things?$orderby=name desc").json()["value"]]
        assert names == sorted(names, reverse=True)

    def test_datastreams_scoped_to_thing(self, client):
        thing_a = create_test_thing(name="Thing A")
        thing_b = create_test_thing(name="Thing B")
        create_test_datastream(name="DS for A", thing=thing_a)
        create_test_datastream(name="DS for B", thing=thing_b)
        body = client.get(f"/Things('{thing_a.id}')/Datastreams").json()
        assert len(body["value"]) == 1
        assert body["value"][0]["name"] == "DS for A"


class TestGetLocationCollection:

    def test_empty_collection(self, client):
        assert client.get("/Locations").json() == {"value": []}

    def test_returns_created_entity(self, client):
        create_test_location(name="My Location")
        body = client.get("/Locations").json()
        assert len(body["value"]) == 1
        assert body["value"][0]["name"] == "My Location"

    def test_response_includes_nav_links(self, client):
        create_test_location()
        entity = client.get("/Locations").json()["value"][0]
        assert "Things@iot.navigationLink" in entity
        assert "HistoricalLocations@iot.navigationLink" in entity


class TestGetHistoricalLocationCollection:

    def test_empty_collection(self, client):
        assert client.get("/HistoricalLocations").json() == {"value": []}

    def test_returns_created_entity(self, client):
        create_test_historical_location()
        body = client.get("/HistoricalLocations").json()
        assert len(body["value"]) == 1
        assert "time" in body["value"][0]

    def test_response_includes_nav_links(self, client):
        create_test_historical_location()
        entity = client.get("/HistoricalLocations").json()["value"][0]
        assert "Thing@iot.navigationLink" in entity
        assert "Locations@iot.navigationLink" in entity


class TestGetSensorCollection:

    def test_empty_collection(self, client):
        assert client.get("/Sensors").json() == {"value": []}

    def test_returns_created_entity(self, client):
        create_test_sensor(name="My Sensor")
        body = client.get("/Sensors").json()
        assert len(body["value"]) == 1
        assert body["value"][0]["name"] == "My Sensor"

    def test_response_includes_nav_links(self, client):
        create_test_sensor()
        entity = client.get("/Sensors").json()["value"][0]
        assert "Datastreams@iot.navigationLink" in entity


class TestGetObservedPropertyCollection:

    def test_empty_collection(self, client):
        assert client.get("/ObservedProperties").json() == {"value": []}

    def test_returns_created_entity(self, client):
        create_test_observed_property(name="My ObservedProperty")
        body = client.get("/ObservedProperties").json()
        assert len(body["value"]) == 1
        assert body["value"][0]["name"] == "My ObservedProperty"

    def test_response_includes_nav_links(self, client):
        create_test_observed_property()
        entity = client.get("/ObservedProperties").json()["value"][0]
        assert "Datastreams@iot.navigationLink" in entity


class TestGetDatastreamCollection:

    def test_empty_collection(self, client):
        assert client.get("/Datastreams").json() == {"value": []}

    def test_returns_created_entity(self, client):
        create_test_datastream(name="My Datastream")
        body = client.get("/Datastreams").json()
        assert len(body["value"]) == 1
        assert body["value"][0]["name"] == "My Datastream"

    def test_response_includes_nav_links(self, client):
        create_test_datastream()
        entity = client.get("/Datastreams").json()["value"][0]
        assert "Thing@iot.navigationLink" in entity
        assert "Sensor@iot.navigationLink" in entity
        assert "ObservedProperty@iot.navigationLink" in entity
        assert "Observations@iot.navigationLink" in entity


class TestGetFeatureOfInterestCollection:

    def test_empty_collection(self, client):
        assert client.get("/FeaturesOfInterest").json() == {"value": []}

    def test_returns_created_entity(self, client):
        create_test_feature_of_interest(name="My Feature")
        body = client.get("/FeaturesOfInterest").json()
        assert len(body["value"]) == 1
        assert body["value"][0]["name"] == "My Feature"

    def test_response_includes_nav_links(self, client):
        create_test_feature_of_interest()
        entity = client.get("/FeaturesOfInterest").json()["value"][0]
        assert "Observations@iot.navigationLink" in entity


class TestGetObservationCollection:

    def test_empty_collection(self, client):
        response = client.get("/Observations")
        assert response.status_code == 200
        assert response.json() == {"value": []}

    def test_returns_created_entity(self, client):
        create_test_observation(result=42.0)
        body = client.get("/Observations").json()
        assert len(body["value"]) == 1
        assert body["value"][0]["result"] == 42.0

    def test_response_includes_nav_links(self, client):
        create_test_observation()
        entity = client.get("/Observations").json()["value"][0]
        assert "Datastream@iot.navigationLink" in entity
        assert "FeatureOfInterest@iot.navigationLink" in entity

    def test_observations_scoped_to_datastream(self, client):
        ds_a = create_test_datastream(name="Datastream A")
        ds_b = create_test_datastream(name="Datastream B")
        create_test_observation(result=1.0, datastream=ds_a)
        create_test_observation(result=2.0, datastream=ds_b)
        body = client.get(f"/Datastreams('{ds_a.id}')/Observations").json()
        assert len(body["value"]) == 1
        assert body["value"][0]["result"] == 1.0
