import pytest
from tests.factories.v1_1.django import create_test_datastream, create_test_observation


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