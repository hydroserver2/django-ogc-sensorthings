import pytest
from django.test import Client


@pytest.mark.parametrize('endpoint', [
    'Things(1)',
    'Locations(1)',
    'HistoricalLocations(1)',
    'Sensors(1)',
    'ObservedProperties(1)',
    'Datastreams(1)',
    'Observations(1)',
    'FeaturesOfInterest(1)',
])
@pytest.mark.django_db()
def test_sensorthings_delete_endpoints(endpoint):
    client = Client()

    response = client.delete(
        f'http://127.0.0.1:8000/sensorthings/core/v1.1/{endpoint}', {}
    )

    assert response.status_code == 204
