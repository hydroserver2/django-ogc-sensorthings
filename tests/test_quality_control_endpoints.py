import pytest
import orjson
from django.test import Client


@pytest.mark.parametrize('endpoint, post_body', [
    ('DeleteObservations', [  # Test DeleteObservations endpoint.
        {
            'Datastream': {'@iot.id': 1}
        },
    ]),
    ('DeleteObservations', [  # Test DeleteObservations endpoint with phenomenonTime interval.
        {
            'Datastream': {'@iot.id': 1},
            'phenomenonTime': '2024-01-01T00:00:00Z/2024-01-02T00:00:00Z'
        },
    ]),
    ('DeleteObservations', [  # Test DeleteObservations endpoint with multiple Datastreams.
        {
            'Datastream': {'@iot.id': 1},
        },
        {
            'Datastream': {'@iot.id': 2},
        },
    ]),
])
@pytest.mark.django_db()
def test_sensorthings_delete_endpoints(endpoint, post_body):
    client = Client()

    response = client.post(
        f'http://127.0.0.1:8000/sensorthings/quality-control/v1.1/{endpoint}',  orjson.dumps(post_body),
        content_type='application/json'
    )

    assert response.status_code == 204
