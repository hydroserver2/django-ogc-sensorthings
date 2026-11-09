from datetime import datetime, timezone
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

    @pytest.mark.parametrize("relation", ["Thing", "Sensor", "ObservedProperty"])
    def test_returns_400_with_message_for_missing_relation(self, client, relation):
        ds = create_test_datastream()
        missing_id = "00000000-0000-0000-0000-000000000000"
        response = client.patch(f"/Datastreams('{ds.id}')", {relation: {"@iot.id": missing_id}})
        assert response.status_code == 400
        assert response.json()["detail"] == f"{relation} with id {missing_id} does not exist."


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


class TestUpdateTimeIntervals:

    INTERVAL = "2022-01-01T00:00:00Z/2023-01-01T00:00:00Z"
    INSTANT = "2022-01-01T00:00:00Z"
    NEW_BEGIN = datetime(2022, 1, 1, tzinfo=timezone.utc)
    NEW_END = datetime(2023, 1, 1, tzinfo=timezone.utc)
    BEGIN = datetime(2020, 1, 1, tzinfo=timezone.utc)
    END = datetime(2021, 1, 1, tzinfo=timezone.utc)

    def create_observation(self):
        return create_test_observation(
            phenomenon_time_begin=self.BEGIN,
            phenomenon_time_end=self.END,
            valid_time_begin=self.BEGIN,
            valid_time_end=self.END,
        )

    def create_datastream(self):
        return create_test_datastream(
            phenomenon_time_begin=self.BEGIN,
            phenomenon_time_end=self.END,
            result_time_begin=self.BEGIN,
            result_time_end=self.END,
        )

    @staticmethod
    def times(entity, field):
        entity.refresh_from_db()
        return getattr(entity, f"{field}_begin"), getattr(entity, f"{field}_end")

    @pytest.mark.parametrize("field,property_name", [
        ("phenomenon_time", "phenomenonTime"),
        ("valid_time", "validTime"),
    ])
    def test_observation_interval(self, client, field, property_name):
        obs = self.create_observation()
        assert client.patch(f"/Observations('{obs.id}')", {property_name: self.INTERVAL}).status_code == 204
        assert self.times(obs, field) == (self.NEW_BEGIN, self.NEW_END)

    def test_observation_instant_replaces_interval(self, client):
        obs = self.create_observation()
        assert client.patch(f"/Observations('{obs.id}')", {"phenomenonTime": self.INSTANT}).status_code == 204
        assert self.times(obs, "phenomenon_time") == (self.NEW_BEGIN, None)

    def test_observation_valid_time_can_be_cleared(self, client):
        obs = self.create_observation()
        assert client.patch(f"/Observations('{obs.id}')", {"validTime": None}).status_code == 204
        assert self.times(obs, "valid_time") == (None, None)

    def test_observation_null_phenomenon_time_returns_400(self, client):
        obs = self.create_observation()
        response = client.patch(f"/Observations('{obs.id}')", {"phenomenonTime": None})
        assert response.status_code == 400
        assert response.json()["detail"] == "phenomenonTime cannot be null."
        assert self.times(obs, "phenomenon_time") == (self.BEGIN, self.END)

    def test_observation_other_fields_keep_times(self, client):
        obs = self.create_observation()
        assert client.patch(f"/Observations('{obs.id}')", {"result": 5.0}).status_code == 204
        assert self.times(obs, "phenomenon_time") == (self.BEGIN, self.END)
        assert self.times(obs, "valid_time") == (self.BEGIN, self.END)

    @pytest.mark.parametrize("field,property_name", [
        ("phenomenon_time", "phenomenonTime"),
        ("result_time", "resultTime"),
    ])
    def test_datastream_interval(self, client, field, property_name):
        ds = self.create_datastream()
        assert client.patch(f"/Datastreams('{ds.id}')", {property_name: self.INTERVAL}).status_code == 204
        assert self.times(ds, field) == (self.NEW_BEGIN, self.NEW_END)

    @pytest.mark.parametrize("field,property_name", [
        ("phenomenon_time", "phenomenonTime"),
        ("result_time", "resultTime"),
    ])
    def test_datastream_time_can_be_cleared(self, client, field, property_name):
        ds = self.create_datastream()
        assert client.patch(f"/Datastreams('{ds.id}')", {property_name: None}).status_code == 204
        assert self.times(ds, field) == (None, None)

    def test_datastream_other_fields_keep_times(self, client):
        ds = self.create_datastream()
        assert client.patch(f"/Datastreams('{ds.id}')", {"name": "Updated"}).status_code == 204
        assert self.times(ds, "phenomenon_time") == (self.BEGIN, self.END)
        assert self.times(ds, "result_time") == (self.BEGIN, self.END)


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
