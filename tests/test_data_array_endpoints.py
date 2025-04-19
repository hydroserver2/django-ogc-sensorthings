import pytest
import orjson
from django.test import Client


@pytest.mark.parametrize('endpoint, query_params, expected_response', [
    (  # Test Observations data array collection endpoint.
        'Observations',
        {'$resultFormat': 'dataArray'},
        '{"value": [{"Datastream@iot.navigationLink": "http://testserver/sensorthings/v1.1/Datastreams(1)", "components": ["phenomenonTime", "result"], "dataArray": [["2024-01-01T00:00:00+00:00", 10], ["2024-01-02T00:00:00+00:00", 15]]}, {"Datastream@iot.navigationLink": "http://testserver/sensorthings/v1.1/Datastreams(2)", "components": ["phenomenonTime", "result"], "dataArray": [["2024-01-01T00:00:00+00:00", 20], ["2024-01-02T00:00:00+00:00", 25]]}]}'
    ),
    (  # Test Observations data array collection endpoint with pagination.
        'Observations',
        {'$resultFormat': 'dataArray', '$skip': 1, '$top': 1},
        '{"value": [{"Datastream@iot.navigationLink": "http://testserver/sensorthings/v1.1/Datastreams(1)", "components": ["phenomenonTime", "result"], "dataArray": [["2024-01-02T00:00:00+00:00", 15]]}], "@iot.nextLink": "http://testserver/sensorthings/v1.1/Observations?$skip=2&$top=1"}'
    ),
    (  # Test Observations data array collection endpoint with select parameter.
        'Observations',
        {'$resultFormat': 'dataArray', '$select': 'result,phenomenonTime,resultTime'},
        '{"value": [{"Datastream@iot.navigationLink": "http://testserver/sensorthings/v1.1/Datastreams(1)", "components": ["phenomenonTime", "result", "resultTime"], "dataArray": [["2024-01-01T00:00:00+00:00", 10, "2024-01-01T00:00:00+00:00"], ["2024-01-02T00:00:00+00:00", 15, "2024-01-02T00:00:00+00:00"]]}, {"Datastream@iot.navigationLink": "http://testserver/sensorthings/v1.1/Datastreams(2)", "components": ["phenomenonTime", "result", "resultTime"], "dataArray": [["2024-01-01T00:00:00+00:00", 20, "2024-01-01T00:00:00+00:00"], ["2024-01-02T00:00:00+00:00", 25, "2024-01-02T00:00:00+00:00"]]}]}'
    ),
    (  # Test Things endpoint select parameter (ID).
        'Observations',
        {'$resultFormat': 'dataArray', '$select': 'id'},
        '{"value": [{"Datastream@iot.navigationLink": "http://testserver/sensorthings/v1.1/Datastreams(1)", "components": ["@iot.id"], "dataArray": [[1], [2]]}, {"Datastream@iot.navigationLink": "http://testserver/sensorthings/v1.1/Datastreams(2)", "components": ["@iot.id"], "dataArray": [[3], [4]]}]}'
    ),
    (  # Test Datastream's Observations data array collection endpoint.
        'Datastreams(1)/Observations',
        {'$resultFormat': 'dataArray'},
        '{"value": [{"Datastream@iot.navigationLink": "http://testserver/sensorthings/v1.1/Datastreams(1)", "components": ["phenomenonTime", "result"], "dataArray": [["2024-01-01T00:00:00+00:00", 10]]}]}'
    ),
])
@pytest.mark.django_db()
def test_sensorthings_data_array_get_endpoints(endpoint, query_params, expected_response):
    client = Client()

    response = client.get(
        f'http://127.0.0.1:8000/sensorthings/data-array/v1.1/{endpoint}',
        query_params
    )

    assert response.status_code == 200
    assert response.content.decode('utf-8') == orjson.dumps(orjson.loads(expected_response)).decode('utf-8')


@pytest.mark.parametrize('endpoint, post_body', [
    ('CreateObservations', [  # Test CreateObservations endpoint.
        {
            'Datastream': {'@iot.id': 1},
            'components': ['phenomenonTime', 'result'],
            'dataArray': [['2024-01-01T00:00:00+00:00', 10.0], ['2024-01-02T00:00:00+00:00', 15.0]]
        },
    ]),
    ('CreateObservations', [  # Test CreateObservations endpoint with FeatureOfInterest.
        {
            'Datastream': {'@iot.id': 1},
            'components': ['phenomenonTime', 'result', 'FeatureOfInterest/id'],
            'dataArray': [['2024-01-01T00:00:00+00:00', 10.0, 1], ['2024-01-02T00:00:00+00:00', 15.0, 1]]
        },
    ]),
    ('CreateObservations', [  # Test CreateObservations endpoint with multiple Datastreams.
        {
            'Datastream': {'@iot.id': 1},
            'components': ['phenomenonTime', 'result'],
            'dataArray': [['2024-01-01T00:00:00+00:00', 10.0], ['2024-01-02T00:00:00+00:00', 15.0]]
        },
        {
            'Datastream': {'@iot.id': 2},
            'components': ['phenomenonTime', 'result'],
            'dataArray': [['2024-01-01T00:00:00+00:00', 10.0], ['2024-01-02T00:00:00+00:00', 15.0]]
        },
    ]),
])
@pytest.mark.django_db()
def test_sensorthings_create_endpoints(endpoint, post_body):
    client = Client()

    response = client.post(
        f'http://127.0.0.1:8000/sensorthings/data-array/v1.1/{endpoint}',  orjson.dumps(post_body),
        content_type='application/json'
    )

    assert response.status_code == 201
