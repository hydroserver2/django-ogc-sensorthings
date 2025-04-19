import pytest
import orjson
from django.test import Client


@pytest.mark.parametrize('endpoint, post_body', [
    ('Things', {
        'name': 'TEST', 'description': 'TEST', 'properties': {'code': 'TEST'}, 'Locations': [{'@iot.id': 1}]
    }),
    ('Locations', {
        'name': 'TEST', 'description': 'TEST', 'properties': {'code': 'TEST'}, 'encodingType': 'application/geo+json', 'location': {'type': 'Feature', 'properties': {}, 'geometry': {'type': 'Point', 'coordinates': [0.0, 0.0]}}, 'Things': [{'@iot.id': 1}], 'HistoricalLocations': [{'@iot.id': 1}]
    }),
    ('HistoricalLocations', {
        'time': '2024-01-01T00:00:00Z', 'Thing': {'@iot.id': 1}, 'Locations': [{'@iot.id': 1}]
    }),
    ('Sensors', {
        'name': 'TEST', 'description': 'TEST', 'metadata': 'https://www.example.com/test.html', 'properties': {'code': 'TEST'}, 'encodingType': 'text/html'
    }),
    ('ObservedProperties', {
        'name': 'TEST', 'description': 'TEST', 'properties': {'code': 'TEST'}, 'definition': 'https://www.example.com'
    }),
    ('Datastreams', {
        'name': 'TEST', 'description': 'TEST', 'properties': {'code': 'TEST'}, 'observationType': 'http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement', 'phenomenonTime': '2024-01-01T00:00:00Z/2024-01-02T00:00:00Z', 'resultTime': '2024-01-01T00:00:00Z/2024-01-02T00:00:00Z', 'unitOfMeasurement': {'name': 'Unit 1', 'symbol': 'U', 'definition': 'https://www.example.com/units/1'}, 'Thing': {'@iot.id': 1}, 'Sensor': {'@iot.id': 1}, 'ObservedProperty': {'@iot.id': 1}
    }),
    ('Observations', {
        'phenomenonTime': '2024-01-01T00:00:00Z', 'resultTime': '2024-01-01T00:00:00Z', 'result': 1, 'Datastream': {'@iot.id': 1}, 'FeatureOfInterest': {'@iot.id': 1}
    }),
    ('FeaturesOfInterest', {
        'name': 'TEST', 'description': 'TEST', 'properties': {'code': 'TEST'}, 'encodingType': 'application/geo+json', 'feature': {'type': 'Feature', 'properties': {}, 'geometry': {'type': 'Point', 'coordinates': [41.742053, -111.809579]}}
    }),
])
@pytest.mark.django_db()
def test_sensorthings_create_endpoints(endpoint, post_body):
    client = Client()

    response = client.post(
        f'http://127.0.0.1:8000/sensorthings/core/v1.1/{endpoint}',  orjson.dumps(post_body),
        content_type='application/json'
    )

    assert response.status_code == 201
