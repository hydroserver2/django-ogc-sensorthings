import pytest
from tests.factories.v1_1.django import (
    create_test_thing,
    create_test_sensor,
    create_test_observed_property,
    create_test_datastream,
    create_test_feature_of_interest,
    create_test_observation,
)


pytestmark = pytest.mark.django_db

OM_MEASUREMENT = "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement"
UNIT_OF_MEASUREMENT = {"name": "Unit", "symbol": "U", "definition": "http://example.com/units/test"}


class TestUpdateThing:

    def test_returns_204(self, client):
        thing = create_test_thing()
        response = client.patch(f"/Things('{thing.id}')", {"name": "Updated Name"})
        assert response.status_code == 204

    def test_updates_primitive_field(self, client):
        thing = create_test_thing(name="Original")
        client.patch(f"/Things('{thing.id}')", {"name": "Updated"})
        body = client.get(f"/Things('{thing.id}')").json()
        assert body["name"] == "Updated"

    def test_unpatched_fields_unchanged(self, client):
        thing = create_test_thing(name="Original", description="Keep this")
        client.patch(f"/Things('{thing.id}')", {"name": "Updated"})
        body = client.get(f"/Things('{thing.id}')").json()
        assert body["description"] == "Keep this"

    def test_returns_404_for_missing_id(self, client):
        response = client.patch(
            "/Things('00000000-0000-0000-0000-000000000000')",
            {"name": "Ghost"}
        )
        assert response.status_code == 404


class TestUpdateDatastream:

    def test_updates_primitive_field(self, client):
        ds = create_test_datastream(name="Original")
        client.patch(f"/Datastreams('{ds.id}')", {"name": "Updated"})
        body = client.get(f"/Datastreams('{ds.id}')").json()
        assert body["name"] == "Updated"

    def test_reassigns_sensor(self, client):
        ds = create_test_datastream()
        new_sensor = create_test_sensor(name="New Sensor")
        client.patch(f"/Datastreams('{ds.id}')", {"Sensor": {"@iot.id": str(new_sensor.id)}})
        sensor_body = client.get(f"/Datastreams('{ds.id}')/Sensor").json()
        assert sensor_body["@iot.id"] == str(new_sensor.id)

    def test_reassigns_observed_property(self, client):
        ds = create_test_datastream()
        new_op = create_test_observed_property(name="New OP")
        client.patch(
            f"/Datastreams('{ds.id}')",
            {"ObservedProperty": {"@iot.id": str(new_op.id)}}
        )
        op_body = client.get(f"/Datastreams('{ds.id}')/ObservedProperty").json()
        assert op_body["@iot.id"] == str(new_op.id)

    def test_reassigns_thing(self, client):
        ds = create_test_datastream()
        new_thing = create_test_thing(name="New Thing")
        client.patch(f"/Datastreams('{ds.id}')", {"Thing": {"@iot.id": str(new_thing.id)}})
        body = client.get(f"/Things('{new_thing.id}')/Datastreams").json()
        assert any(d["name"] == ds.name for d in body["value"])

    def test_returns_404_for_missing_id(self, client):
        response = client.patch(
            "/Datastreams('00000000-0000-0000-0000-000000000000')",
            {"name": "Ghost"}
        )
        assert response.status_code == 404


class TestUpdateObservation:

    def test_updates_result(self, client):
        obs = create_test_observation(result=1.0)
        client.patch(f"/Observations('{obs.id}')", {"result": 2.0})
        body = client.get(f"/Observations('{obs.id}')").json()
        assert body["result"] == 2.0

    def test_reassigns_feature_of_interest(self, client):
        obs = create_test_observation()
        new_foi = create_test_feature_of_interest(name="New FOI")
        client.patch(
            f"/Observations('{obs.id}')",
            {"FeatureOfInterest": {"@iot.id": str(new_foi.id)}}
        )
        foi_body = client.get(f"/Observations('{obs.id}')/FeatureOfInterest").json()
        assert foi_body["@iot.id"] == str(new_foi.id)

    def test_returns_404_for_missing_id(self, client):
        response = client.patch(
            "/Observations('00000000-0000-0000-0000-000000000000')",
            {"result": 0.0}
        )
        assert response.status_code == 404


class TestUpdateSensor:

    def test_updates_primitive_field(self, client):
        sensor = create_test_sensor(name="Original")
        client.patch(f"/Sensors('{sensor.id}')", {"name": "Updated"})
        body = client.get(f"/Sensors('{sensor.id}')").json()
        assert body["name"] == "Updated"

    def test_unpatched_fields_unchanged(self, client):
        sensor = create_test_sensor(name="Original", description="Keep this")
        client.patch(f"/Sensors('{sensor.id}')", {"name": "Updated"})
        body = client.get(f"/Sensors('{sensor.id}')").json()
        assert body["description"] == "Keep this"


class TestUpdateObservedProperty:

    def test_updates_primitive_field(self, client):
        op = create_test_observed_property(name="Original")
        client.patch(f"/ObservedProperties('{op.id}')", {"name": "Updated"})
        body = client.get(f"/ObservedProperties('{op.id}')").json()
        assert body["name"] == "Updated"
