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


class TestGetThingEntity:

    def test_returns_entity_by_id(self, client):
        thing = create_test_thing(name="My Thing")
        body = client.get(f"/Things('{thing.id}')").json()
        assert body["name"] == "My Thing"
        assert body["@iot.id"] == str(thing.id)

    def test_returns_404_for_missing_id(self, client):
        response = client.get("/Things('00000000-0000-0000-0000-000000000000')")
        assert response.status_code == 404

    def test_response_includes_self_link(self, client):
        thing = create_test_thing()
        body = client.get(f"/Things('{thing.id}')").json()
        assert "@iot.selfLink" in body
        assert str(thing.id) in body["@iot.selfLink"]

    def test_response_includes_nav_links(self, client):
        thing = create_test_thing()
        body = client.get(f"/Things('{thing.id}')").json()
        assert "Locations@iot.navigationLink" in body
        assert "Datastreams@iot.navigationLink" in body
        assert "HistoricalLocations@iot.navigationLink" in body

    def test_select_returns_only_requested_fields(self, client):
        thing = create_test_thing(name="Selectable", description="Hidden")
        body = client.get(f"/Things('{thing.id}')?$select=name").json()
        assert body["name"] == "Selectable"
        assert "description" not in body


class TestGetLocationEntity:

    def test_returns_entity_by_id(self, client):
        loc = create_test_location(name="My Location")
        body = client.get(f"/Locations('{loc.id}')").json()
        assert body["name"] == "My Location"

    def test_returns_404_for_missing_id(self, client):
        response = client.get("/Locations('00000000-0000-0000-0000-000000000000')")
        assert response.status_code == 404


class TestGetHistoricalLocationEntity:

    def test_returns_entity_by_id(self, client):
        hl = create_test_historical_location()
        body = client.get(f"/HistoricalLocations('{hl.id}')").json()
        assert "time" in body

    def test_returns_404_for_missing_id(self, client):
        response = client.get("/HistoricalLocations('00000000-0000-0000-0000-000000000000')")
        assert response.status_code == 404


class TestGetSensorEntity:

    def test_returns_entity_by_id(self, client):
        sensor = create_test_sensor(name="My Sensor")
        body = client.get(f"/Sensors('{sensor.id}')").json()
        assert body["name"] == "My Sensor"

    def test_returns_404_for_missing_id(self, client):
        response = client.get("/Sensors('00000000-0000-0000-0000-000000000000')")
        assert response.status_code == 404


class TestGetObservedPropertyEntity:

    def test_returns_entity_by_id(self, client):
        op = create_test_observed_property(name="My ObservedProperty")
        body = client.get(f"/ObservedProperties('{op.id}')").json()
        assert body["name"] == "My ObservedProperty"

    def test_returns_404_for_missing_id(self, client):
        response = client.get("/ObservedProperties('00000000-0000-0000-0000-000000000000')")
        assert response.status_code == 404


class TestGetDatastreamEntity:

    def test_returns_entity_by_id(self, client):
        ds = create_test_datastream(name="My Datastream")
        body = client.get(f"/Datastreams('{ds.id}')").json()
        assert body["name"] == "My Datastream"

    def test_returns_404_for_missing_id(self, client):
        response = client.get("/Datastreams('00000000-0000-0000-0000-000000000000')")
        assert response.status_code == 404

    def test_response_includes_fk_nav_links(self, client):
        ds = create_test_datastream()
        body = client.get(f"/Datastreams('{ds.id}')").json()
        assert "Thing@iot.navigationLink" in body
        assert "Sensor@iot.navigationLink" in body
        assert "ObservedProperty@iot.navigationLink" in body


class TestGetFeatureOfInterestEntity:

    def test_returns_entity_by_id(self, client):
        foi = create_test_feature_of_interest(name="My Feature")
        body = client.get(f"/FeaturesOfInterest('{foi.id}')").json()
        assert body["name"] == "My Feature"

    def test_returns_404_for_missing_id(self, client):
        response = client.get("/FeaturesOfInterest('00000000-0000-0000-0000-000000000000')")
        assert response.status_code == 404


class TestGetObservationEntity:

    def test_returns_entity_by_id(self, client):
        obs = create_test_observation(result=99.0)
        body = client.get(f"/Observations('{obs.id}')").json()
        assert body["result"] == 99.0

    def test_returns_404_for_missing_id(self, client):
        response = client.get("/Observations('00000000-0000-0000-0000-000000000000')")
        assert response.status_code == 404

    def test_response_includes_fk_nav_links(self, client):
        obs = create_test_observation()
        body = client.get(f"/Observations('{obs.id}')").json()
        assert "Datastream@iot.navigationLink" in body
        assert "FeatureOfInterest@iot.navigationLink" in body
