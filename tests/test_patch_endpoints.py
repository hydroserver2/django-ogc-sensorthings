import pytest
import orjson
from django.test import Client


@pytest.mark.parametrize('endpoint, patch_body', [
    ('Things(1)', {
        'name': 'TEST', 'description': 'TEST', 'properties': {'code': 'TEST'}, 'Locations': [{'@iot.id': 1}]
    }),
    ('Locations(1)', {
        'name': 'TEST', 'description': 'TEST', 'properties': {'code': 'TEST'}, 'encodingType': 'application/geo+json', 'location': {'type': 'Feature', 'properties': {}, 'geometry': {'type': 'Point', 'coordinates': [0.0, 0.0]}}, 'Things': [{'@iot.id': 1}], 'HistoricalLocations': [{'@iot.id': 1}]
    }),
    ('HistoricalLocations(1)', {
        'time': '2024-01-01T00:00:00Z', 'Thing': {'@iot.id': 1}, 'Locations': [{'@iot.id': 1}]
    }),
    ('Sensors(1)', {
        'name': 'TEST', 'description': 'TEST', 'metadata': 'TEST', 'properties': {'code': 'TEST'}
    }),
    ('ObservedProperties(1)', {
        'name': 'TEST', 'description': 'TEST', 'properties': {'code': 'TEST'}, 'definition': 'https://www.example.com'
    }),
    ('Datastreams(1)', {
        'name': 'TEST', 'description': 'TEST', 'properties': {'code': 'TEST'}, 'observationType': 'http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement', 'phenomenonTime': '2024-01-01T00:00:00Z/2024-01-02T00:00:00Z', 'resultTime': '2024-01-01T00:00:00Z/2024-01-02T00:00:00Z', 'unitOfMeasurement': {'name': 'Unit 1', 'symbol': 'U', 'definition': 'https://www.example.com/units/1'}, 'Thing': {'@iot.id': 1}, 'Sensor': {'@iot.id': 1}, 'ObservedProperty': {'@iot.id': 1}
    }),
    ('Observations(1)', {
        'phenomenonTime': '2024-01-01T00:00:00Z', 'resultTime': '2024-01-01T00:00:00Z', 'result': 1, 'Datastream': {'@iot.id': 1}, 'FeatureOfInterest': {'@iot.id': 1}
    }),
    ('FeaturesOfInterest(1)', {
        'name': 'TEST', 'description': 'TEST', 'properties': {'code': 'TEST'}, 'encodingType': 'application/geo+json', 'feature': {'type': 'Feature', 'properties': {}, 'geometry': {'type': 'Point', 'coordinates': [41.742053, -111.809579]}}
    }),
])
@pytest.mark.django_db()
def test_sensorthings_update_endpoints(endpoint, patch_body):
    client = Client()

    response = client.patch(
        f'http://127.0.0.1:8000/sensorthings/core/v1.1/{endpoint}',  orjson.dumps(patch_body)
    )

    print(response.content)

    assert response.status_code == 204
