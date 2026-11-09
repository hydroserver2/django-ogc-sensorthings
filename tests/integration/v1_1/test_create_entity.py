from datetime import datetime, timezone
import pytest
from sensorthings.versions.v1_1.backends.django.models import (
    Datastream, Thing, Location, Observation
)
from tests.factories.v1_1.django import (
    create_test_thing,
    create_test_location,
    create_test_sensor,
    create_test_observed_property,
    create_test_datastream,
    create_test_feature_of_interest,
)


pytestmark = pytest.mark.django_db

OM_MEASUREMENT = "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement"
UNIT_OF_MEASUREMENT = {"name": "Unit", "symbol": "U", "definition": "http://example.com/units/test"}
GEO_JSON_POINT = {"type": "Feature", "geometry": {"type": "Point", "coordinates": [0.0, 0.0]}, "properties": {}}


def get_created_id(response):
    """Extract the entity ID from the Location response header."""
    location = response.headers["Location"]
    return location.split("('")[1].rstrip("')")


class TestCreateThing:

    def test_returns_201(self, client):
        response = client.post("/Things", {"name": "New Thing", "description": "A thing"})
        assert response.status_code == 201

    def test_location_header_present(self, client):
        response = client.post("/Things", {"name": "New Thing", "description": "A thing"})
        assert "Location" in response.headers
        assert "Things" in response.headers["Location"]

    def test_entity_retrievable_after_create(self, client):
        response = client.post("/Things", {"name": "Created Thing", "description": "A thing"})
        entity_id = get_created_id(response)
        body = client.get(f"/Things('{entity_id}')").json()
        assert body["name"] == "Created Thing"

    def test_deep_insert_with_inline_location(self, client):
        payload = {
            "name": "Thing with Location",
            "description": "...",
            "Locations": [{
                "name": "Inline Location",
                "description": "...",
                "encodingType": "application/geo+json",
                "location": GEO_JSON_POINT,
            }],
        }
        response = client.post("/Things", payload)
        assert response.status_code == 201
        assert Location.objects.filter(name="Inline Location").exists()

    def test_deep_insert_location_linked_to_thing(self, client):
        payload = {
            "name": "Linked Thing",
            "description": "...",
            "Locations": [{
                "name": "Linked Location",
                "description": "...",
                "encodingType": "application/geo+json",
                "location": GEO_JSON_POINT,
            }],
        }
        response = client.post("/Things", payload)
        entity_id = get_created_id(response)
        body = client.get(f"/Things('{entity_id}')/Locations").json()
        assert len(body["value"]) == 1
        assert body["value"][0]["name"] == "Linked Location"

    def test_deep_insert_location_by_id(self, client):
        loc = create_test_location()
        payload = {
            "name": "Thing referencing Location",
            "description": "...",
            "Locations": [{"@iot.id": str(loc.id)}],
        }
        response = client.post("/Things", payload)
        assert response.status_code == 201
        entity_id = get_created_id(response)
        body = client.get(f"/Things('{entity_id}')/Locations").json()
        assert len(body["value"]) == 1

    def test_deep_insert_with_inline_datastream(self, client):
        sensor = create_test_sensor()
        op = create_test_observed_property()
        payload = {
            "name": "Thing with Datastream",
            "description": "...",
            "Datastreams": [{
                "name": "Inline Datastream",
                "description": "...",
                "unitOfMeasurement": UNIT_OF_MEASUREMENT,
                "observationType": OM_MEASUREMENT,
                "Sensor": {"@iot.id": str(sensor.id)},
                "ObservedProperty": {"@iot.id": str(op.id)},
            }],
        }
        response = client.post("/Things", payload)
        assert response.status_code == 201
        assert Datastream.objects.filter(name="Inline Datastream").exists()

    def test_deep_insert_datastream_linked_to_thing(self, client):
        sensor = create_test_sensor()
        op = create_test_observed_property()
        payload = {
            "name": "Thing with Datastream",
            "description": "...",
            "Datastreams": [{
                "name": "Linked Datastream",
                "description": "...",
                "unitOfMeasurement": UNIT_OF_MEASUREMENT,
                "observationType": OM_MEASUREMENT,
                "Sensor": {"@iot.id": str(sensor.id)},
                "ObservedProperty": {"@iot.id": str(op.id)},
            }],
        }
        response = client.post("/Things", payload)
        entity_id = get_created_id(response)
        body = client.get(f"/Things('{entity_id}')/Datastreams").json()
        assert len(body["value"]) == 1
        assert body["value"][0]["name"] == "Linked Datastream"


class TestCreateDatastream:

    def test_returns_201_with_fk_references(self, client):
        thing = create_test_thing()
        sensor = create_test_sensor()
        op = create_test_observed_property()
        payload = {
            "name": "New Datastream",
            "description": "...",
            "unitOfMeasurement": UNIT_OF_MEASUREMENT,
            "observationType": OM_MEASUREMENT,
            "Thing": {"@iot.id": str(thing.id)},
            "Sensor": {"@iot.id": str(sensor.id)},
            "ObservedProperty": {"@iot.id": str(op.id)},
        }
        response = client.post("/Datastreams", payload)
        assert response.status_code == 201

    def test_entity_retrievable_after_create(self, client):
        thing = create_test_thing()
        sensor = create_test_sensor()
        op = create_test_observed_property()
        payload = {
            "name": "Retrievable Datastream",
            "description": "...",
            "unitOfMeasurement": UNIT_OF_MEASUREMENT,
            "observationType": OM_MEASUREMENT,
            "Thing": {"@iot.id": str(thing.id)},
            "Sensor": {"@iot.id": str(sensor.id)},
            "ObservedProperty": {"@iot.id": str(op.id)},
        }
        response = client.post("/Datastreams", payload)
        entity_id = get_created_id(response)
        body = client.get(f"/Datastreams('{entity_id}')").json()
        assert body["name"] == "Retrievable Datastream"

    def test_deep_insert_with_inline_fk_parents(self, client):
        payload = {
            "name": "Datastream with inline parents",
            "description": "...",
            "unitOfMeasurement": UNIT_OF_MEASUREMENT,
            "observationType": OM_MEASUREMENT,
            "Thing": {
                "name": "Inline Thing",
                "description": "...",
            },
            "Sensor": {
                "name": "Inline Sensor",
                "description": "...",
                "encodingType": "application/pdf",
                "metadata": "http://example.com/sensor.pdf",
            },
            "ObservedProperty": {
                "name": "Inline ObservedProperty",
                "definition": "http://example.com/op",
                "description": "...",
            },
        }
        response = client.post("/Datastreams", payload)
        assert response.status_code == 201
        assert Thing.objects.filter(name="Inline Thing").exists()

    def test_deep_insert_with_inline_observations(self, client):
        thing = create_test_thing()
        sensor = create_test_sensor()
        op = create_test_observed_property()
        foi = create_test_feature_of_interest()
        payload = {
            "name": "Datastream with Observations",
            "description": "...",
            "unitOfMeasurement": UNIT_OF_MEASUREMENT,
            "observationType": OM_MEASUREMENT,
            "Thing": {"@iot.id": str(thing.id)},
            "Sensor": {"@iot.id": str(sensor.id)},
            "ObservedProperty": {"@iot.id": str(op.id)},
            "Observations": [{
                "phenomenonTime": "2025-01-01T00:00:00Z",
                "result": 42.0,
                "resultTime": "2025-01-01T00:00:00Z",
                "FeatureOfInterest": {"@iot.id": str(foi.id)},
            }],
        }
        response = client.post("/Datastreams", payload)
        assert response.status_code == 201
        entity_id = get_created_id(response)
        obs_body = client.get(f"/Datastreams('{entity_id}')/Observations").json()
        assert len(obs_body["value"]) == 1
        assert obs_body["value"][0]["result"] == 42.0


class TestCreateObservation:

    def test_returns_201_with_fk_references(self, client):
        ds = create_test_datastream()
        foi = create_test_feature_of_interest()
        payload = {
            "phenomenonTime": "2025-01-01T00:00:00Z",
            "result": 99.0,
            "resultTime": "2025-01-01T00:00:00Z",
            "Datastream": {"@iot.id": str(ds.id)},
            "FeatureOfInterest": {"@iot.id": str(foi.id)},
        }
        response = client.post("/Observations", payload)
        assert response.status_code == 201

    def test_entity_retrievable_after_create(self, client):
        ds = create_test_datastream()
        foi = create_test_feature_of_interest()
        payload = {
            "phenomenonTime": "2025-01-01T00:00:00Z",
            "result": 77.0,
            "resultTime": "2025-01-01T00:00:00Z",
            "Datastream": {"@iot.id": str(ds.id)},
            "FeatureOfInterest": {"@iot.id": str(foi.id)},
        }
        response = client.post("/Observations", payload)
        entity_id = get_created_id(response)
        body = client.get(f"/Observations('{entity_id}')").json()
        assert body["result"] == 77.0

    def test_observation_linked_to_datastream(self, client):
        ds = create_test_datastream()
        foi = create_test_feature_of_interest()
        payload = {
            "phenomenonTime": "2025-01-01T00:00:00Z",
            "result": 55.0,
            "resultTime": "2025-01-01T00:00:00Z",
            "Datastream": {"@iot.id": str(ds.id)},
            "FeatureOfInterest": {"@iot.id": str(foi.id)},
        }
        client.post("/Observations", payload)
        body = client.get(f"/Datastreams('{ds.id}')/Observations").json()
        assert any(o["result"] == 55.0 for o in body["value"])


class TestCreateTimeIntervals:

    INSTANT = "2020-01-01T00:00:00Z"
    INTERVAL = "2020-01-01T00:00:00Z/2021-01-01T00:00:00Z"
    BEGIN = datetime(2020, 1, 1, tzinfo=timezone.utc)
    END = datetime(2021, 1, 1, tzinfo=timezone.utc)

    @staticmethod
    def observation_payload(**fields):
        return {
            "phenomenonTime": TestCreateTimeIntervals.INSTANT,
            "result": 1.0,
            "Datastream": {"@iot.id": str(create_test_datastream().id)},
            "FeatureOfInterest": {"@iot.id": str(create_test_feature_of_interest().id)},
            **fields,
        }

    @staticmethod
    def datastream_payload(**fields):
        return {
            "name": "Interval Datastream",
            "description": "...",
            "unitOfMeasurement": UNIT_OF_MEASUREMENT,
            "observationType": OM_MEASUREMENT,
            "Thing": {"@iot.id": str(create_test_thing().id)},
            "Sensor": {"@iot.id": str(create_test_sensor().id)},
            "ObservedProperty": {"@iot.id": str(create_test_observed_property().id)},
            **fields,
        }

    def test_observation_valid_time(self, client):
        response = client.post("/Observations", self.observation_payload(validTime=self.INTERVAL))
        assert response.status_code == 201
        observation = Observation.objects.get()
        assert (observation.valid_time_begin, observation.valid_time_end) == (self.BEGIN, self.END)

    def test_observation_phenomenon_time_interval_defaults_result_time_to_start(self, client):
        response = client.post("/Observations", self.observation_payload(phenomenonTime=self.INTERVAL))
        assert response.status_code == 201
        observation = Observation.objects.get()
        assert (observation.phenomenon_time_begin, observation.phenomenon_time_end) == (self.BEGIN, self.END)
        assert observation.result_time == self.BEGIN

    def test_observation_phenomenon_time_instant(self, client):
        response = client.post("/Observations", self.observation_payload())
        assert response.status_code == 201
        observation = Observation.objects.get()
        assert (observation.phenomenon_time_begin, observation.phenomenon_time_end) == (self.BEGIN, None)

    def test_observation_omitted_phenomenon_time_uses_server_time(self, client):
        payload = self.observation_payload()
        del payload["phenomenonTime"]
        assert client.post("/Observations", payload).status_code == 201
        assert Observation.objects.get().phenomenon_time_begin is not None

    def test_observation_null_phenomenon_time_uses_server_time(self, client):
        assert client.post("/Observations", self.observation_payload(phenomenonTime=None)).status_code == 201
        assert Observation.objects.get().phenomenon_time_begin is not None

    @pytest.mark.parametrize("field,property_name", [
        ("phenomenon_time", "phenomenonTime"),
        ("result_time", "resultTime"),
    ])
    def test_datastream_interval(self, client, field, property_name):
        response = client.post("/Datastreams", self.datastream_payload(**{property_name: self.INTERVAL}))
        assert response.status_code == 201
        datastream = Datastream.objects.get(name="Interval Datastream")
        assert (getattr(datastream, f"{field}_begin"), getattr(datastream, f"{field}_end")) == (self.BEGIN, self.END)

    def test_deep_insert(self, client):
        foi = create_test_feature_of_interest()
        response = client.post("/Datastreams", self.datastream_payload(
            phenomenonTime=self.INTERVAL,
            Observations=[{
                "phenomenonTime": self.INTERVAL,
                "validTime": self.INTERVAL,
                "result": 1.0,
                "FeatureOfInterest": {"@iot.id": str(foi.id)},
            }],
        ))
        assert response.status_code == 201
        assert Datastream.objects.get(name="Interval Datastream").phenomenon_time_end == self.END
        assert Observation.objects.get().valid_time_end == self.END

    def test_data_array(self, client):
        ds = create_test_datastream()
        foi = create_test_feature_of_interest()
        response = client.post("/CreateObservations", [{
            "Datastream": {"@iot.id": str(ds.id)},
            "components": ["phenomenonTime", "result", "FeatureOfInterest/id"],
            "dataArray": [[self.INTERVAL, 1.0, str(foi.id)]],
        }])
        assert response.status_code == 201
        assert Observation.objects.get().phenomenon_time_end == self.END
