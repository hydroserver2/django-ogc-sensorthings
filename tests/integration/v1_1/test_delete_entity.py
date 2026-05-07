import pytest
from sensorthings.versions.v1_1.backends.django.models import (
    Thing, Location, HistoricalLocation, Sensor, ObservedProperty,
    Datastream, FeatureOfInterest, Observation,
)
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


class TestDeleteThing:

    def test_returns_204(self, client):
        thing = create_test_thing()
        response = client.delete(f"/Things('{thing.id}')")
        assert response.status_code == 204

    def test_entity_no_longer_exists(self, client):
        thing = create_test_thing()
        client.delete(f"/Things('{thing.id}')")
        assert not Thing.objects.filter(pk=thing.id).exists()

    def test_returns_404_after_deletion(self, client):
        thing = create_test_thing()
        client.delete(f"/Things('{thing.id}')")
        assert client.get(f"/Things('{thing.id}')").status_code == 404

    def test_returns_404_for_missing_id(self, client):
        response = client.delete("/Things('00000000-0000-0000-0000-000000000000')")
        assert response.status_code == 404


class TestDeleteLocation:

    def test_returns_204(self, client):
        loc = create_test_location()
        assert client.delete(f"/Locations('{loc.id}')").status_code == 204

    def test_entity_no_longer_exists(self, client):
        loc = create_test_location()
        client.delete(f"/Locations('{loc.id}')")
        assert not Location.objects.filter(pk=loc.id).exists()


class TestDeleteHistoricalLocation:

    def test_returns_204(self, client):
        hl = create_test_historical_location()
        assert client.delete(f"/HistoricalLocations('{hl.id}')").status_code == 204

    def test_entity_no_longer_exists(self, client):
        hl = create_test_historical_location()
        client.delete(f"/HistoricalLocations('{hl.id}')")
        assert not HistoricalLocation.objects.filter(pk=hl.id).exists()


class TestDeleteSensor:

    def test_returns_204(self, client):
        sensor = create_test_sensor()
        assert client.delete(f"/Sensors('{sensor.id}')").status_code == 204

    def test_entity_no_longer_exists(self, client):
        sensor = create_test_sensor()
        client.delete(f"/Sensors('{sensor.id}')")
        assert not Sensor.objects.filter(pk=sensor.id).exists()


class TestDeleteObservedProperty:

    def test_returns_204(self, client):
        op = create_test_observed_property()
        assert client.delete(f"/ObservedProperties('{op.id}')").status_code == 204

    def test_entity_no_longer_exists(self, client):
        op = create_test_observed_property()
        client.delete(f"/ObservedProperties('{op.id}')")
        assert not ObservedProperty.objects.filter(pk=op.id).exists()


class TestDeleteDatastream:

    def test_returns_204(self, client):
        ds = create_test_datastream()
        assert client.delete(f"/Datastreams('{ds.id}')").status_code == 204

    def test_entity_no_longer_exists(self, client):
        ds = create_test_datastream()
        client.delete(f"/Datastreams('{ds.id}')")
        assert not Datastream.objects.filter(pk=ds.id).exists()

    def test_observations_deleted_with_datastream(self, client):
        obs = create_test_observation()
        ds_id = obs.datastream_id
        obs_id = obs.id
        client.delete(f"/Datastreams('{ds_id}')")
        assert not Observation.objects.filter(pk=obs_id).exists()


class TestDeleteFeatureOfInterest:

    def test_returns_204(self, client):
        foi = create_test_feature_of_interest()
        assert client.delete(f"/FeaturesOfInterest('{foi.id}')").status_code == 204

    def test_entity_no_longer_exists(self, client):
        foi = create_test_feature_of_interest()
        client.delete(f"/FeaturesOfInterest('{foi.id}')")
        assert not FeatureOfInterest.objects.filter(pk=foi.id).exists()


class TestDeleteObservation:

    def test_returns_204(self, client):
        obs = create_test_observation()
        assert client.delete(f"/Observations('{obs.id}')").status_code == 204

    def test_entity_no_longer_exists(self, client):
        obs = create_test_observation()
        client.delete(f"/Observations('{obs.id}')")
        assert not Observation.objects.filter(pk=obs.id).exists()

    def test_returns_404_for_missing_id(self, client):
        response = client.delete("/Observations('00000000-0000-0000-0000-000000000000')")
        assert response.status_code == 404
