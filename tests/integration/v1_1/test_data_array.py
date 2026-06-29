import pytest
from django.test import override_settings
from sensorthings.versions.v1_1.backends.django.models import FeatureOfInterest, Observation
from tests.factories.v1_1.django import (
    create_test_datastream,
    create_test_feature_of_interest,
    create_test_location,
    create_test_observation,
)


pytestmark = pytest.mark.django_db


class TestDataArrayNestedPath:

    def test_nested_path_returns_data_array_format(self, client):
        datastream = create_test_datastream()
        create_test_observation(datastream=datastream)
        response = client.get(f"/Datastreams('{datastream.id}')/Observations?$resultFormat=dataArray")
        assert response.status_code == 200
        body = response.json()
        assert "value" in body
        assert len(body["value"]) > 0
        item = body["value"][0]
        assert "Datastream@iot.navigationLink" in item
        assert "components" in item
        assert "dataArray" in item

    def test_nested_path_without_result_format_returns_standard_format(self, client):
        datastream = create_test_datastream()
        create_test_observation(datastream=datastream)
        response = client.get(f"/Datastreams('{datastream.id}')/Observations")
        assert response.status_code == 200
        body = response.json()
        assert "value" in body
        assert len(body["value"]) > 0
        item = body["value"][0]
        assert "@iot.id" in item
        assert "dataArray" not in item

    def test_nested_path_only_returns_observations_for_that_datastream(self, client):
        datastream_a = create_test_datastream()
        datastream_b = create_test_datastream()
        create_test_observation(datastream=datastream_a, result=1.0)
        create_test_observation(datastream=datastream_a, result=2.0)
        create_test_observation(datastream=datastream_b, result=99.0)
        response = client.get(f"/Datastreams('{datastream_a.id}')/Observations?$resultFormat=dataArray")
        assert response.status_code == 200
        body = response.json()
        assert len(body["value"]) == 1
        assert len(body["value"][0]["dataArray"]) == 2

    def test_nested_path_data_array_groups_by_datastream(self, client):
        datastream = create_test_datastream()
        create_test_observation(datastream=datastream, result=1.0)
        create_test_observation(datastream=datastream, result=2.0)
        response = client.get(f"/Datastreams('{datastream.id}')/Observations?$resultFormat=dataArray")
        body = response.json()
        assert len(body["value"]) == 1
        assert f"{datastream.id}" in body["value"][0]["Datastream@iot.navigationLink"]


class TestDataArrayTopLimit:

    @override_settings(SENSORTHINGS_V1_1_MAX_TOP=10, SENSORTHINGS_V1_1_MAX_TOP_DATA_ARRAY=50)
    def test_data_array_top_above_max_top_data_array_returns_422(self, client):
        response = client.get("/Observations?$resultFormat=dataArray&$top=51")
        assert response.status_code == 422

    @override_settings(SENSORTHINGS_V1_1_MAX_TOP=10, SENSORTHINGS_V1_1_MAX_TOP_DATA_ARRAY=50)
    def test_data_array_top_within_max_top_data_array_is_accepted(self, client):
        response = client.get("/Observations?$resultFormat=dataArray&$top=50")
        assert response.status_code == 200

    @override_settings(SENSORTHINGS_V1_1_MAX_TOP=10, SENSORTHINGS_V1_1_MAX_TOP_DATA_ARRAY=50)
    def test_non_data_array_top_above_max_top_returns_422(self, client):
        response = client.get("/Observations?$top=11")
        assert response.status_code == 422

    @override_settings(SENSORTHINGS_V1_1_MAX_TOP=10, SENSORTHINGS_V1_1_MAX_TOP_DATA_ARRAY=50)
    def test_non_data_array_top_within_max_top_is_accepted(self, client):
        response = client.get("/Observations?$top=10")
        assert response.status_code == 200


class TestCreateObservations:

    T1 = "2025-01-01T00:00:00Z"
    T2 = "2025-01-02T00:00:00Z"
    T3 = "2025-01-03T00:00:00Z"

    def _group(self, ds, rows, components=None):
        if components is None:
            components = ["phenomenonTime", "result", "resultTime", "FeatureOfInterest/id"]
        return {
            "Datastream": {"@iot.id": str(ds.id)},
            "components": components,
            "dataArray": rows,
        }

    def test_returns_201(self, client):
        ds = create_test_datastream()
        foi = create_test_feature_of_interest()
        response = client.post("/CreateObservations", [self._group(ds, [[self.T1, 1.0, self.T1, str(foi.id)]])])
        assert response.status_code == 201

    def test_response_is_list_of_self_links(self, client):
        ds = create_test_datastream()
        foi = create_test_feature_of_interest()
        response = client.post("/CreateObservations", [self._group(ds, [[self.T1, 1.0, self.T1, str(foi.id)]])])
        body = response.json()
        assert isinstance(body, list)
        assert len(body) == 1
        assert "Observations" in body[0]

    def test_observations_persisted_in_db(self, client):
        ds = create_test_datastream()
        foi = create_test_feature_of_interest()
        before = Observation.objects.count()
        client.post("/CreateObservations", [self._group(ds, [[self.T1, 1.0, self.T1, str(foi.id)]])])
        assert Observation.objects.count() == before + 1

    def test_multiple_rows_in_one_group(self, client):
        ds = create_test_datastream()
        foi = create_test_feature_of_interest()
        rows = [
            [self.T1, 1.0, self.T1, str(foi.id)],
            [self.T2, 2.0, self.T2, str(foi.id)],
            [self.T3, 3.0, self.T3, str(foi.id)],
        ]
        before = Observation.objects.count()
        response = client.post("/CreateObservations", [self._group(ds, rows)])
        assert response.status_code == 201
        assert len(response.json()) == 3
        assert Observation.objects.count() == before + 3

    def test_multiple_datastream_groups(self, client):
        ds_a = create_test_datastream()
        ds_b = create_test_datastream()
        foi = create_test_feature_of_interest()
        before = Observation.objects.count()
        payload = [
            self._group(ds_a, [[self.T1, 1.0, self.T1, str(foi.id)]]),
            self._group(ds_b, [[self.T1, 2.0, self.T1, str(foi.id)]]),
        ]
        response = client.post("/CreateObservations", payload)
        assert response.status_code == 201
        assert len(response.json()) == 2
        assert Observation.objects.count() == before + 2

    def test_foi_auto_resolved_from_thing_location(self, client):
        ds = create_test_datastream()
        create_test_location(things=[ds.thing])
        before_foi = FeatureOfInterest.objects.count()
        before_obs = Observation.objects.count()
        response = client.post("/CreateObservations", [
            self._group(ds, [[self.T1, 1.0, self.T1]], components=["phenomenonTime", "result", "resultTime"])
        ])
        assert response.status_code == 201
        assert Observation.objects.count() == before_obs + 1
        assert FeatureOfInterest.objects.count() == before_foi + 1

    def test_foi_reused_for_multiple_rows_on_same_datastream(self, client):
        ds = create_test_datastream()
        create_test_location(things=[ds.thing])
        before_foi = FeatureOfInterest.objects.count()
        rows = [
            [self.T1, 1.0, self.T1],
            [self.T2, 2.0, self.T2],
        ]
        client.post("/CreateObservations", [
            self._group(ds, rows, components=["phenomenonTime", "result", "resultTime"])
        ])
        assert FeatureOfInterest.objects.count() == before_foi + 1

    def test_phenomenon_time_defaults_to_server_time(self, client):
        ds = create_test_datastream()
        foi = create_test_feature_of_interest()
        before = Observation.objects.count()
        response = client.post("/CreateObservations", [
            self._group(ds, [[1.0, str(foi.id)]], components=["result", "FeatureOfInterest/id"])
        ])
        assert response.status_code == 201
        assert Observation.objects.count() == before + 1

    def test_row_length_mismatch_returns_422(self, client):
        ds = create_test_datastream()
        response = client.post("/CreateObservations", [
            self._group(ds, [[self.T1, 1.0]], components=["phenomenonTime", "result", "resultTime"])
        ])
        assert response.status_code == 422

    @override_settings(SENSORTHINGS_V1_1_MAX_POST_DATA_ARRAY_OBSERVATIONS=2)
    def test_total_rows_above_limit_returns_400(self, client):
        ds = create_test_datastream()
        foi = create_test_feature_of_interest()
        rows = [[self.T1, 1.0, self.T1, str(foi.id)]] * 3
        response = client.post("/CreateObservations", [self._group(ds, rows)])
        assert response.status_code == 400

    @override_settings(SENSORTHINGS_V1_1_MAX_POST_DATA_ARRAY_OBSERVATIONS=4)
    def test_total_rows_across_groups_above_limit_returns_400(self, client):
        ds_a = create_test_datastream()
        ds_b = create_test_datastream()
        foi = create_test_feature_of_interest()
        row = [self.T1, 1.0, self.T1, str(foi.id)]
        payload = [self._group(ds_a, [row] * 3), self._group(ds_b, [row] * 2)]
        response = client.post("/CreateObservations", payload)
        assert response.status_code == 400

    @override_settings(SENSORTHINGS_V1_1_MAX_POST_DATA_ARRAY_OBSERVATIONS=3)
    def test_total_rows_at_limit_is_accepted(self, client):
        ds = create_test_datastream()
        foi = create_test_feature_of_interest()
        rows = [[self.T1, 1.0, self.T1, str(foi.id)]] * 3
        response = client.post("/CreateObservations", [self._group(ds, rows)])
        assert response.status_code == 201
