import orjson
import pytest
from django.test import Client


@pytest.mark.parametrize('endpoint, query_params, expected_response', [
    (  # Test Things endpoint with no query parameters.
        'Things',
        {},
        '{"value": [{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Things(1)", "name": "THING_1", "description": "Thing 1", "properties": {}, "Locations@iot.navigationLink": "http://testserver/sensorthings/v1.1/Things(1)/Locations", "HistoricalLocations@iot.navigationLink": "http://testserver/sensorthings/v1.1/Things(1)/HistoricalLocations", "Datastreams@iot.navigationLink": "http://testserver/sensorthings/v1.1/Things(1)/Datastreams"}, {"@iot.id": 2, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Things(2)", "name": "THING_2", "description": "Thing 2", "properties": {"code": "THING"}, "Locations@iot.navigationLink": "http://testserver/sensorthings/v1.1/Things(2)/Locations", "HistoricalLocations@iot.navigationLink": "http://testserver/sensorthings/v1.1/Things(2)/HistoricalLocations", "Datastreams@iot.navigationLink": "http://testserver/sensorthings/v1.1/Things(2)/Datastreams"}]}'
    ),
    (  # Test Things endpoint with pagination.
        'Things',
        {'$count': True, '$skip': 1, '$top': 1},
        '{"@iot.count": 2, "value": [{"@iot.id": 2, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Things(2)", "name": "THING_2", "description": "Thing 2", "properties": {"code": "THING"}, "Locations@iot.navigationLink": "http://testserver/sensorthings/v1.1/Things(2)/Locations", "HistoricalLocations@iot.navigationLink": "http://testserver/sensorthings/v1.1/Things(2)/HistoricalLocations", "Datastreams@iot.navigationLink": "http://testserver/sensorthings/v1.1/Things(2)/Datastreams"}]}'
    ),
    (  # Test Things endpoint select parameter.
        'Things',
        {'$select': 'name,description'},
        '{"value": [{"name": "THING_1", "description": "Thing 1"}, {"name": "THING_2", "description": "Thing 2"}]}'
    ),
    (  # Test Things endpoint select parameter (ID).
        'Things',
        {'$select': 'id'},
        '{"value": [{"@iot.id": 1}, {"@iot.id": 2}]}'
    ),
    (  # Test Things endpoint with Locations expanded.
        'Things',
        {'$expand': 'Locations'},
        '{"value": [{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Things(1)", "name": "THING_1", "description": "Thing 1", "properties": {}, "Locations": [{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Locations(1)", "name": "LOCATION_1", "description": "Location 1", "encodingType": "application/geo+json", "location": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [41.740004, -111.793743]}, "properties": {}}, "properties": {}}], "HistoricalLocations@iot.navigationLink": "http://testserver/sensorthings/v1.1/Things(1)/HistoricalLocations", "Datastreams@iot.navigationLink": "http://testserver/sensorthings/v1.1/Things(1)/Datastreams"}, {"@iot.id": 2, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Things(2)", "name": "THING_2", "description": "Thing 2", "properties": {"code": "THING"}, "Locations": [{"@iot.id": 2, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Locations(2)", "name": "LOCATION_2", "description": "Location 2", "encodingType": "application/geo+json", "location": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [41.745527, -111.813398]}, "properties": {}}, "properties": {"code": "LOCATION"}}, {"@iot.id": 3, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Locations(3)", "name": "LOCATION_3", "description": "Location 3", "encodingType": "application/geo+json", "location": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [41.742053, -111.809579]}, "properties": {}}, "properties": {}}], "HistoricalLocations@iot.navigationLink": "http://testserver/sensorthings/v1.1/Things(2)/HistoricalLocations", "Datastreams@iot.navigationLink": "http://testserver/sensorthings/v1.1/Things(2)/Datastreams"}]}'
    ),
    (  # Test Things endpoint with Historical Locations expanded.
        'Things',
        {'$expand': 'HistoricalLocations'},
        '{"value": [{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Things(1)", "name": "THING_1", "description": "Thing 1", "properties": {}, "Locations@iot.navigationLink": "http://testserver/sensorthings/v1.1/Things(1)/Locations", "HistoricalLocations": [], "Datastreams@iot.navigationLink": "http://testserver/sensorthings/v1.1/Things(1)/Datastreams"}, {"@iot.id": 2, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Things(2)", "name": "THING_2", "description": "Thing 2", "properties": {"code": "THING"}, "Locations@iot.navigationLink": "http://testserver/sensorthings/v1.1/Things(2)/Locations", "HistoricalLocations": [{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/HistoricalLocations(1)", "time": "2024-01-01T00:00:00+00:00"}, {"@iot.id": 2, "@iot.selfLink": "http://testserver/sensorthings/v1.1/HistoricalLocations(2)", "time": "2024-01-02T00:00:00+00:00"}], "Datastreams@iot.navigationLink": "http://testserver/sensorthings/v1.1/Things(2)/Datastreams"}]}'
    ),
    (  # Test Things endpoint with Datastreams expanded.
        'Things',
        {'$expand': 'Datastreams'},
        '{"value": [{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Things(1)", "name": "THING_1", "description": "Thing 1", "properties": {}, "Locations@iot.navigationLink": "http://testserver/sensorthings/v1.1/Things(1)/Locations", "HistoricalLocations@iot.navigationLink": "http://testserver/sensorthings/v1.1/Things(1)/HistoricalLocations", "Datastreams": [{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Datastreams(1)", "name": "DATASTREAM_1", "description": "Datastream 1", "unitOfMeasurement": {"name": "Unit 1", "symbol": "U", "definition": "https://www.example.com/units/1"}, "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement", "phenomenonTime": "2024-01-01T00:00:00+00:00/2024-01-02T00:00:00+00:00", "resultTime": "2024-01-01T00:00:00+00:00/2024-01-02T00:00:00+00:00", "properties": {}}]}, {"@iot.id": 2, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Things(2)", "name": "THING_2", "description": "Thing 2", "properties": {"code": "THING"}, "Locations@iot.navigationLink": "http://testserver/sensorthings/v1.1/Things(2)/Locations", "HistoricalLocations@iot.navigationLink": "http://testserver/sensorthings/v1.1/Things(2)/HistoricalLocations", "Datastreams": [{"@iot.id": 2, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Datastreams(2)", "name": "DATASTREAM_2", "description": "Datastream 2", "unitOfMeasurement": {"name": "Unit 2", "symbol": "U", "definition": "https://www.example.com/units/2"}, "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement", "phenomenonTime": "2024-01-01T00:00:00+00:00/2024-01-02T00:00:00+00:00", "resultTime": "2024-01-01T00:00:00+00:00/2024-01-02T00:00:00+00:00", "properties": {"code": "DATASTREAM"}}]}]}'
    ),
    (  # Test Things endpoint with multiple expanded components.
        'Things',
        {'$expand': 'Locations/HistoricalLocations,Datastreams/Sensor,Datastreams/ObservedProperty'},
        '{"value": [{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Things(1)", "name": "THING_1", "description": "Thing 1", "properties": {}, "Locations": [{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Locations(1)", "name": "LOCATION_1", "description": "Location 1", "encodingType": "application/geo+json", "location": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [41.740004, -111.793743]}, "properties": {}}, "properties": {}, "HistoricalLocations": []}], "HistoricalLocations@iot.navigationLink": "http://testserver/sensorthings/v1.1/Things(1)/HistoricalLocations", "Datastreams": [{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Datastreams(1)", "name": "DATASTREAM_1", "description": "Datastream 1", "unitOfMeasurement": {"name": "Unit 1", "symbol": "U", "definition": "https://www.example.com/units/1"}, "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement", "phenomenonTime": "2024-01-01T00:00:00+00:00/2024-01-02T00:00:00+00:00", "resultTime": "2024-01-01T00:00:00+00:00/2024-01-02T00:00:00+00:00", "properties": {}, "Sensor": {"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Sensors(1)", "name": "SENSOR_1", "description": "Sensor 1", "encodingType": "text/html", "metadata": "TEST", "properties": {}}, "ObservedProperty": {"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/ObservedProperties(1)", "name": "OBSERVED_PROPERTY_1", "definition": "https://www.example.com/observed-properties/1", "description": "Observed Property 1", "properties": {}}}]}, {"@iot.id": 2, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Things(2)", "name": "THING_2", "description": "Thing 2", "properties": {"code": "THING"}, "Locations": [{"@iot.id": 2, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Locations(2)", "name": "LOCATION_2", "description": "Location 2", "encodingType": "application/geo+json", "location": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [41.745527, -111.813398]}, "properties": {}}, "properties": {"code": "LOCATION"}, "HistoricalLocations": [{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/HistoricalLocations(1)", "time": "2024-01-01T00:00:00+00:00"}, {"@iot.id": 2, "@iot.selfLink": "http://testserver/sensorthings/v1.1/HistoricalLocations(2)", "time": "2024-01-02T00:00:00+00:00"}]}, {"@iot.id": 3, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Locations(3)", "name": "LOCATION_3", "description": "Location 3", "encodingType": "application/geo+json", "location": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [41.742053, -111.809579]}, "properties": {}}, "properties": {}, "HistoricalLocations": [{"@iot.id": 2, "@iot.selfLink": "http://testserver/sensorthings/v1.1/HistoricalLocations(2)", "time": "2024-01-02T00:00:00+00:00"}]}], "HistoricalLocations@iot.navigationLink": "http://testserver/sensorthings/v1.1/Things(2)/HistoricalLocations", "Datastreams": [{"@iot.id": 2, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Datastreams(2)", "name": "DATASTREAM_2", "description": "Datastream 2", "unitOfMeasurement": {"name": "Unit 2", "symbol": "U", "definition": "https://www.example.com/units/2"}, "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement", "phenomenonTime": "2024-01-01T00:00:00+00:00/2024-01-02T00:00:00+00:00", "resultTime": "2024-01-01T00:00:00+00:00/2024-01-02T00:00:00+00:00", "properties": {"code": "DATASTREAM"}, "Sensor": {"@iot.id": 2, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Sensors(2)", "name": "SENSOR_2", "description": "Sensor 2", "encodingType": "text/html", "metadata": "TEST", "properties": {"code": "SENSOR"}}, "ObservedProperty": {"@iot.id": 2, "@iot.selfLink": "http://testserver/sensorthings/v1.1/ObservedProperties(2)", "name": "OBSERVED_PROPERTY_2", "definition": "https://www.example.com/observed-properties/2", "description": "Observed Property 2", "properties": {"code": "OBSERVED_PROPERTY"}}}]}]}'
    ),
    (  # Test Things with $ref.
        'Things/$ref',
        {},
        '{"value": [{"@iot.selfLink": "http://testserver/sensorthings/v1.1/Things(1)"}, {"@iot.selfLink": "http://testserver/sensorthings/v1.1/Things(2)"}]}'
    ),
    (  # Test Thing's Locations endpoint.
        'Things(1)/Locations',
        {},
        '{"value": [{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Locations(1)", "name": "LOCATION_1", "description": "Location 1", "encodingType": "application/geo+json", "location": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [41.740004, -111.793743]}, "properties": {}}, "properties": {}, "Things@iot.navigationLink": "http://testserver/sensorthings/v1.1/Locations(1)/Things", "HistoricalLocations@iot.navigationLink": "http://testserver/sensorthings/v1.1/Locations(1)/HistoricalLocations"}]}'
    ),
    (  # Test Thing's HistoricalLocations endpoint.
        'Things(1)/HistoricalLocations',
        {},
        '{"value": [{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/HistoricalLocations(1)", "time": "2024-01-01T00:00:00+00:00", "Thing@iot.navigationLink": "http://testserver/sensorthings/v1.1/HistoricalLocations(1)/Thing"}]}'
    ),
    (  # Test Locations endpoint with no query parameters.
        'Locations',
        {},
        '{"value": [{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Locations(1)", "name": "LOCATION_1", "description": "Location 1", "encodingType": "application/geo+json", "location": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [41.740004, -111.793743]}, "properties": {}}, "properties": {}, "Things@iot.navigationLink": "http://testserver/sensorthings/v1.1/Locations(1)/Things", "HistoricalLocations@iot.navigationLink": "http://testserver/sensorthings/v1.1/Locations(1)/HistoricalLocations"}, {"@iot.id": 2, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Locations(2)", "name": "LOCATION_2", "description": "Location 2", "encodingType": "application/geo+json", "location": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [41.745527, -111.813398]}, "properties": {}}, "properties": {"code": "LOCATION"}, "Things@iot.navigationLink": "http://testserver/sensorthings/v1.1/Locations(2)/Things", "HistoricalLocations@iot.navigationLink": "http://testserver/sensorthings/v1.1/Locations(2)/HistoricalLocations"}, {"@iot.id": 3, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Locations(3)", "name": "LOCATION_3", "description": "Location 3", "encodingType": "application/geo+json", "location": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [41.742053, -111.809579]}, "properties": {}}, "properties": {}, "Things@iot.navigationLink": "http://testserver/sensorthings/v1.1/Locations(3)/Things", "HistoricalLocations@iot.navigationLink": "http://testserver/sensorthings/v1.1/Locations(3)/HistoricalLocations"}]}'
    ),
    (  # Test Locations endpoint with pagination.
        'Locations',
        {'$count': True, '$skip': 1, '$top': 1},
        '{"@iot.count": 3, "value": [{"@iot.id": 2, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Locations(2)", "name": "LOCATION_2", "description": "Location 2", "encodingType": "application/geo+json", "location": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [41.745527, -111.813398]}, "properties": {}}, "properties": {"code": "LOCATION"}, "Things@iot.navigationLink": "http://testserver/sensorthings/v1.1/Locations(2)/Things", "HistoricalLocations@iot.navigationLink": "http://testserver/sensorthings/v1.1/Locations(2)/HistoricalLocations"}], "@iot.nextLink": "http://testserver/sensorthings/v1.1/Locations?$count=True&$skip=2&$top=1"}'
    ),
    (  # Test Locations endpoint select parameter.
        'Locations',
        {'$select': 'name,description'},
        '{"value": [{"name": "LOCATION_1", "description": "Location 1"}, {"name": "LOCATION_2", "description": "Location 2"}, {"name": "LOCATION_3", "description": "Location 3"}]}'
    ),
    (  # Test Locations endpoint select parameter (ID).
        'Locations',
        {'$select': 'id'},
        '{"value": [{"@iot.id": 1}, {"@iot.id": 2}, {"@iot.id": 3}]}'
    ),
    (  # Test Locations endpoint with Things expanded.
        'Locations',
        {'$expand': 'Things'},
        '{"value": [{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Locations(1)", "name": "LOCATION_1", "description": "Location 1", "encodingType": "application/geo+json", "location": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [41.740004, -111.793743]}, "properties": {}}, "properties": {}, "Things": [{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Things(1)", "name": "THING_1", "description": "Thing 1", "properties": {}}], "HistoricalLocations@iot.navigationLink": "http://testserver/sensorthings/v1.1/Locations(1)/HistoricalLocations"}, {"@iot.id": 2, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Locations(2)", "name": "LOCATION_2", "description": "Location 2", "encodingType": "application/geo+json", "location": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [41.745527, -111.813398]}, "properties": {}}, "properties": {"code": "LOCATION"}, "Things": [{"@iot.id": 2, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Things(2)", "name": "THING_2", "description": "Thing 2", "properties": {"code": "THING"}}], "HistoricalLocations@iot.navigationLink": "http://testserver/sensorthings/v1.1/Locations(2)/HistoricalLocations"}, {"@iot.id": 3, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Locations(3)", "name": "LOCATION_3", "description": "Location 3", "encodingType": "application/geo+json", "location": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [41.742053, -111.809579]}, "properties": {}}, "properties": {}, "Things": [{"@iot.id": 2, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Things(2)", "name": "THING_2", "description": "Thing 2", "properties": {"code": "THING"}}], "HistoricalLocations@iot.navigationLink": "http://testserver/sensorthings/v1.1/Locations(3)/HistoricalLocations"}]}'
    ),
    (  # Test Locations endpoint with HistoricalLocations expanded.
        'Locations',
        {'$expand': 'HistoricalLocations'},
        '{"value": [{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Locations(1)", "name": "LOCATION_1", "description": "Location 1", "encodingType": "application/geo+json", "location": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [41.740004, -111.793743]}, "properties": {}}, "properties": {}, "Things@iot.navigationLink": "http://testserver/sensorthings/v1.1/Locations(1)/Things", "HistoricalLocations": []}, {"@iot.id": 2, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Locations(2)", "name": "LOCATION_2", "description": "Location 2", "encodingType": "application/geo+json", "location": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [41.745527, -111.813398]}, "properties": {}}, "properties": {"code": "LOCATION"}, "Things@iot.navigationLink": "http://testserver/sensorthings/v1.1/Locations(2)/Things", "HistoricalLocations": [{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/HistoricalLocations(1)", "time": "2024-01-01T00:00:00+00:00"}, {"@iot.id": 2, "@iot.selfLink": "http://testserver/sensorthings/v1.1/HistoricalLocations(2)", "time": "2024-01-02T00:00:00+00:00"}]}, {"@iot.id": 3, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Locations(3)", "name": "LOCATION_3", "description": "Location 3", "encodingType": "application/geo+json", "location": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [41.742053, -111.809579]}, "properties": {}}, "properties": {}, "Things@iot.navigationLink": "http://testserver/sensorthings/v1.1/Locations(3)/Things", "HistoricalLocations": [{"@iot.id": 2, "@iot.selfLink": "http://testserver/sensorthings/v1.1/HistoricalLocations(2)", "time": "2024-01-02T00:00:00+00:00"}]}]}'
    ),
    (  # Test Locations endpoint with multiple expanded components.
        'Locations',
        {'$expand': 'HistoricalLocations,Things'},
        '{"value": [{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Locations(1)", "name": "LOCATION_1", "description": "Location 1", "encodingType": "application/geo+json", "location": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [41.740004, -111.793743]}, "properties": {}}, "properties": {}, "Things": [{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Things(1)", "name": "THING_1", "description": "Thing 1", "properties": {}}], "HistoricalLocations": []}, {"@iot.id": 2, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Locations(2)", "name": "LOCATION_2", "description": "Location 2", "encodingType": "application/geo+json", "location": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [41.745527, -111.813398]}, "properties": {}}, "properties": {"code": "LOCATION"}, "Things": [{"@iot.id": 2, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Things(2)", "name": "THING_2", "description": "Thing 2", "properties": {"code": "THING"}}], "HistoricalLocations": [{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/HistoricalLocations(1)", "time": "2024-01-01T00:00:00+00:00"}, {"@iot.id": 2, "@iot.selfLink": "http://testserver/sensorthings/v1.1/HistoricalLocations(2)", "time": "2024-01-02T00:00:00+00:00"}]}, {"@iot.id": 3, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Locations(3)", "name": "LOCATION_3", "description": "Location 3", "encodingType": "application/geo+json", "location": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [41.742053, -111.809579]}, "properties": {}}, "properties": {}, "Things": [{"@iot.id": 2, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Things(2)", "name": "THING_2", "description": "Thing 2", "properties": {"code": "THING"}}], "HistoricalLocations": [{"@iot.id": 2, "@iot.selfLink": "http://testserver/sensorthings/v1.1/HistoricalLocations(2)", "time": "2024-01-02T00:00:00+00:00"}]}]}'
    ),
    (  # Test Locations with $ref.
        'Locations/$ref',
        {},
        '{"value": [{"@iot.selfLink": "http://testserver/sensorthings/v1.1/Locations(1)"}, {"@iot.selfLink": "http://testserver/sensorthings/v1.1/Locations(2)"}, {"@iot.selfLink": "http://testserver/sensorthings/v1.1/Locations(3)"}]}'
    ),
    (  # Test Location's Things endpoint.
        'Locations(1)/Things',
        {},
        '{"value": [{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Things(1)", "name": "THING_1", "description": "Thing 1", "properties": {}, "Locations@iot.navigationLink": "http://testserver/sensorthings/v1.1/Things(1)/Locations", "HistoricalLocations@iot.navigationLink": "http://testserver/sensorthings/v1.1/Things(1)/HistoricalLocations", "Datastreams@iot.navigationLink": "http://testserver/sensorthings/v1.1/Things(1)/Datastreams"}]}'
    ),
    (  # Test Location's HistoricalLocations endpoint.
        'Locations(1)/HistoricalLocations',
        {},
        '{"value": [{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/HistoricalLocations(1)", "time": "2024-01-01T00:00:00+00:00", "Thing@iot.navigationLink": "http://testserver/sensorthings/v1.1/HistoricalLocations(1)/Thing"}]}'
    ),
    (  # Test HistoricalLocations endpoint with no query parameters.
        'HistoricalLocations',
        {},
        '{"value": [{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/HistoricalLocations(1)", "time": "2024-01-01T00:00:00+00:00", "Thing@iot.navigationLink": "http://testserver/sensorthings/v1.1/HistoricalLocations(1)/Thing"}, {"@iot.id": 2, "@iot.selfLink": "http://testserver/sensorthings/v1.1/HistoricalLocations(2)", "time": "2024-01-02T00:00:00+00:00", "Thing@iot.navigationLink": "http://testserver/sensorthings/v1.1/HistoricalLocations(2)/Thing"}]}'
    ),
    (  # Test HistoricalLocations endpoint with pagination.
        'HistoricalLocations',
        {'$count': True, '$skip': 1, '$top': 1},
        '{"@iot.count": 2, "value": [{"@iot.id": 2, "@iot.selfLink": "http://testserver/sensorthings/v1.1/HistoricalLocations(2)", "time": "2024-01-02T00:00:00+00:00", "Thing@iot.navigationLink": "http://testserver/sensorthings/v1.1/HistoricalLocations(2)/Thing"}]}'
    ),
    (  # Test HistoricalLocations endpoint select parameter.
        'HistoricalLocations',
        {'$select': 'time'},
        '{"value": [{"time": "2024-01-01T00:00:00+00:00"}, {"time": "2024-01-02T00:00:00+00:00"}]}'
    ),
    (  # Test HistoricalLocations endpoint select parameter (ID).
        'HistoricalLocations',
        {'$select': 'id'},
        '{"value": [{"@iot.id": 1}, {"@iot.id": 2}]}'
    ),
    (  # Test HistoricalLocations endpoint with Locations expanded.
        'HistoricalLocations',
        {'$expand': 'Locations'},
        '{"value": [{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/HistoricalLocations(1)", "time": "2024-01-01T00:00:00+00:00", "Thing@iot.navigationLink": "http://testserver/sensorthings/v1.1/HistoricalLocations(1)/Thing"}, {"@iot.id": 2, "@iot.selfLink": "http://testserver/sensorthings/v1.1/HistoricalLocations(2)", "time": "2024-01-02T00:00:00+00:00", "Thing@iot.navigationLink": "http://testserver/sensorthings/v1.1/HistoricalLocations(2)/Thing"}]}'
    ),
    (  # Test HistoricalLocations endpoint with Thing expanded.
        'HistoricalLocations',
        {'$expand': 'Thing'},
        '{"value": [{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/HistoricalLocations(1)", "time": "2024-01-01T00:00:00+00:00", "Thing": {"@iot.id": 2, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Things(2)", "name": "THING_2", "description": "Thing 2", "properties": {"code": "THING"}}}, {"@iot.id": 2, "@iot.selfLink": "http://testserver/sensorthings/v1.1/HistoricalLocations(2)", "time": "2024-01-02T00:00:00+00:00", "Thing": {"@iot.id": 2, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Things(2)", "name": "THING_2", "description": "Thing 2", "properties": {"code": "THING"}}}]}'
    ),
    (  # Test HistoricalLocations endpoint with multiple expanded components.
        'HistoricalLocations',
        {'$expand': 'Locations,Thing'},
        '{"value": [{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/HistoricalLocations(1)", "time": "2024-01-01T00:00:00+00:00", "Thing": {"@iot.id": 2, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Things(2)", "name": "THING_2", "description": "Thing 2", "properties": {"code": "THING"}}}, {"@iot.id": 2, "@iot.selfLink": "http://testserver/sensorthings/v1.1/HistoricalLocations(2)", "time": "2024-01-02T00:00:00+00:00", "Thing": {"@iot.id": 2, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Things(2)", "name": "THING_2", "description": "Thing 2", "properties": {"code": "THING"}}}]}'
    ),
    (  # Test HistoricalLocations with $ref.
        'HistoricalLocations/$ref',
        {},
        '{"value": [{"@iot.selfLink": "http://testserver/sensorthings/v1.1/HistoricalLocations(1)"}, {"@iot.selfLink": "http://testserver/sensorthings/v1.1/HistoricalLocations(2)"}]}'
    ),
    (  # Test HistoricalLocations's Locations endpoint.
        'HistoricalLocations(1)/Locations',
        {},
        '{"value": [{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Locations(1)", "name": "LOCATION_1", "description": "Location 1", "encodingType": "application/geo+json", "location": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [41.740004, -111.793743]}, "properties": {}}, "properties": {}, "Things@iot.navigationLink": "http://testserver/sensorthings/v1.1/Locations(1)/Things", "HistoricalLocations@iot.navigationLink": "http://testserver/sensorthings/v1.1/Locations(1)/HistoricalLocations"}]}'
    ),
    (  # Test Sensors endpoint with no query parameters.
        'Sensors',
        {},
        '{"value": [{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Sensors(1)", "name": "SENSOR_1", "description": "Sensor 1", "encodingType": "text/html", "metadata": "TEST", "properties": {}, "Datastreams@iot.navigationLink": "http://testserver/sensorthings/v1.1/Sensors(1)/Datastreams"}, {"@iot.id": 2, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Sensors(2)", "name": "SENSOR_2", "description": "Sensor 2", "encodingType": "text/html", "metadata": "TEST", "properties": {"code": "SENSOR"}, "Datastreams@iot.navigationLink": "http://testserver/sensorthings/v1.1/Sensors(2)/Datastreams"}]}'
    ),
    (  # Test Sensors endpoint with pagination.
        'Sensors',
        {'$count': True, '$skip': 1, '$top': 1},
        '{"@iot.count": 2, "value": [{"@iot.id": 2, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Sensors(2)", "name": "SENSOR_2", "description": "Sensor 2", "encodingType": "text/html", "metadata": "TEST", "properties": {"code": "SENSOR"}, "Datastreams@iot.navigationLink": "http://testserver/sensorthings/v1.1/Sensors(2)/Datastreams"}]}'
    ),
    (  # Test Sensors endpoint select parameter.
        'Sensors',
        {'$select': 'name'},
        '{"value": [{"name": "SENSOR_1"}, {"name": "SENSOR_2"}]}'
    ),
    (  # Test Sensors endpoint select parameter (ID).
        'Sensors',
        {'$select': 'id'},
        '{"value": [{"@iot.id": 1}, {"@iot.id": 2}]}'
    ),
    (  # Test Sensors endpoint with Datastreams expanded.
        'Sensors',
        {'$expand': 'Datastreams'},
        '{"value": [{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Sensors(1)", "name": "SENSOR_1", "description": "Sensor 1", "encodingType": "text/html", "metadata": "TEST", "properties": {}, "Datastreams": [{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Datastreams(1)", "name": "DATASTREAM_1", "description": "Datastream 1", "unitOfMeasurement": {"name": "Unit 1", "symbol": "U", "definition": "https://www.example.com/units/1"}, "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement", "phenomenonTime": "2024-01-01T00:00:00+00:00/2024-01-02T00:00:00+00:00", "resultTime": "2024-01-01T00:00:00+00:00/2024-01-02T00:00:00+00:00", "properties": {}}]}, {"@iot.id": 2, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Sensors(2)", "name": "SENSOR_2", "description": "Sensor 2", "encodingType": "text/html", "metadata": "TEST", "properties": {"code": "SENSOR"}, "Datastreams": [{"@iot.id": 2, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Datastreams(2)", "name": "DATASTREAM_2", "description": "Datastream 2", "unitOfMeasurement": {"name": "Unit 2", "symbol": "U", "definition": "https://www.example.com/units/2"}, "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement", "phenomenonTime": "2024-01-01T00:00:00+00:00/2024-01-02T00:00:00+00:00", "resultTime": "2024-01-01T00:00:00+00:00/2024-01-02T00:00:00+00:00", "properties": {"code": "DATASTREAM"}}]}]}'
    ),
    (  # Test Sensors with $ref.
        'Sensors/$ref',
        {},
        '{"value": [{"@iot.selfLink": "http://testserver/sensorthings/v1.1/Sensors(1)"}, {"@iot.selfLink": "http://testserver/sensorthings/v1.1/Sensors(2)"}]}'
    ),
    (  # Test Sensor's Datastreams endpoint.
        'Sensors(1)/Datastreams',
        {},
        '{"value": [{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Datastreams(1)", "name": "DATASTREAM_1", "description": "Datastream 1", "unitOfMeasurement": {"name": "Unit 1", "symbol": "U", "definition": "https://www.example.com/units/1"}, "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement", "phenomenonTime": "2024-01-01T00:00:00+00:00/2024-01-02T00:00:00+00:00", "resultTime": "2024-01-01T00:00:00+00:00/2024-01-02T00:00:00+00:00", "properties": {}, "Thing@iot.navigationLink": "http://testserver/sensorthings/v1.1/Datastreams(1)/Thing", "Sensor@iot.navigationLink": "http://testserver/sensorthings/v1.1/Datastreams(1)/Sensor", "ObservedProperty@iot.navigationLink": "http://testserver/sensorthings/v1.1/Datastreams(1)/ObservedProperty", "Observations@iot.navigationLink": "http://testserver/sensorthings/v1.1/Datastreams(1)/Observations"}]}'
    ),
    (  # Test ObservedProperties endpoint with no query parameters.
        'ObservedProperties',
        {},
        '{"value": [{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/ObservedProperties(1)", "name": "OBSERVED_PROPERTY_1", "definition": "https://www.example.com/observed-properties/1", "description": "Observed Property 1", "properties": {}, "Datastreams@iot.navigationLink": "http://testserver/sensorthings/v1.1/ObservedProperties(1)/Datastreams"}, {"@iot.id": 2, "@iot.selfLink": "http://testserver/sensorthings/v1.1/ObservedProperties(2)", "name": "OBSERVED_PROPERTY_2", "definition": "https://www.example.com/observed-properties/2", "description": "Observed Property 2", "properties": {"code": "OBSERVED_PROPERTY"}, "Datastreams@iot.navigationLink": "http://testserver/sensorthings/v1.1/ObservedProperties(2)/Datastreams"}]}'
    ),
    (  # Test ObservedProperties endpoint with pagination.
        'ObservedProperties',
        {'$count': True, '$skip': 1, '$top': 1},
        '{"@iot.count": 2, "value": [{"@iot.id": 2, "@iot.selfLink": "http://testserver/sensorthings/v1.1/ObservedProperties(2)", "name": "OBSERVED_PROPERTY_2", "definition": "https://www.example.com/observed-properties/2", "description": "Observed Property 2", "properties": {"code": "OBSERVED_PROPERTY"}, "Datastreams@iot.navigationLink": "http://testserver/sensorthings/v1.1/ObservedProperties(2)/Datastreams"}]}'
    ),
    (  # Test ObservedProperties endpoint select parameter.
        'ObservedProperties',
        {'$select': 'name'},
        '{"value": [{"name": "OBSERVED_PROPERTY_1"}, {"name": "OBSERVED_PROPERTY_2"}]}'
    ),
    (  # Test ObservedProperties endpoint select parameter (ID).
        'ObservedProperties',
        {'$select': 'id'},
        '{"value": [{"@iot.id": 1}, {"@iot.id": 2}]}'
    ),
    (  # Test ObservedProperties endpoint with Datastreams expanded.
        'ObservedProperties',
        {'$expand': 'Datastreams'},
        '{"value": [{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/ObservedProperties(1)", "name": "OBSERVED_PROPERTY_1", "definition": "https://www.example.com/observed-properties/1", "description": "Observed Property 1", "properties": {}, "Datastreams": [{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Datastreams(1)", "name": "DATASTREAM_1", "description": "Datastream 1", "unitOfMeasurement": {"name": "Unit 1", "symbol": "U", "definition": "https://www.example.com/units/1"}, "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement", "phenomenonTime": "2024-01-01T00:00:00+00:00/2024-01-02T00:00:00+00:00", "resultTime": "2024-01-01T00:00:00+00:00/2024-01-02T00:00:00+00:00", "properties": {}}]}, {"@iot.id": 2, "@iot.selfLink": "http://testserver/sensorthings/v1.1/ObservedProperties(2)", "name": "OBSERVED_PROPERTY_2", "definition": "https://www.example.com/observed-properties/2", "description": "Observed Property 2", "properties": {"code": "OBSERVED_PROPERTY"}, "Datastreams": [{"@iot.id": 2, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Datastreams(2)", "name": "DATASTREAM_2", "description": "Datastream 2", "unitOfMeasurement": {"name": "Unit 2", "symbol": "U", "definition": "https://www.example.com/units/2"}, "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement", "phenomenonTime": "2024-01-01T00:00:00+00:00/2024-01-02T00:00:00+00:00", "resultTime": "2024-01-01T00:00:00+00:00/2024-01-02T00:00:00+00:00", "properties": {"code": "DATASTREAM"}}]}]}'
    ),
    (  # Test ObservedProperties with $ref.
        'ObservedProperties/$ref',
        {},
        '{"value": [{"@iot.selfLink": "http://testserver/sensorthings/v1.1/ObservedProperties(1)"}, {"@iot.selfLink": "http://testserver/sensorthings/v1.1/ObservedProperties(2)"}]}'
    ),
    (  # Test ObservedProperties' Datastreams endpoint.
        'ObservedProperties(1)/Datastreams',
        {},
        '{"value": [{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Datastreams(1)", "name": "DATASTREAM_1", "description": "Datastream 1", "unitOfMeasurement": {"name": "Unit 1", "symbol": "U", "definition": "https://www.example.com/units/1"}, "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement", "phenomenonTime": "2024-01-01T00:00:00+00:00/2024-01-02T00:00:00+00:00", "resultTime": "2024-01-01T00:00:00+00:00/2024-01-02T00:00:00+00:00", "properties": {}, "Thing@iot.navigationLink": "http://testserver/sensorthings/v1.1/Datastreams(1)/Thing", "Sensor@iot.navigationLink": "http://testserver/sensorthings/v1.1/Datastreams(1)/Sensor", "ObservedProperty@iot.navigationLink": "http://testserver/sensorthings/v1.1/Datastreams(1)/ObservedProperty", "Observations@iot.navigationLink": "http://testserver/sensorthings/v1.1/Datastreams(1)/Observations"}]}'
    ),
    (  # Test Datastreams endpoint with no query parameters.
        'Datastreams',
        {},
        '{"value": [{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Datastreams(1)", "name": "DATASTREAM_1", "description": "Datastream 1", "unitOfMeasurement": {"name": "Unit 1", "symbol": "U", "definition": "https://www.example.com/units/1"}, "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement", "phenomenonTime": "2024-01-01T00:00:00+00:00/2024-01-02T00:00:00+00:00", "resultTime": "2024-01-01T00:00:00+00:00/2024-01-02T00:00:00+00:00", "properties": {}, "Thing@iot.navigationLink": "http://testserver/sensorthings/v1.1/Datastreams(1)/Thing", "Sensor@iot.navigationLink": "http://testserver/sensorthings/v1.1/Datastreams(1)/Sensor", "ObservedProperty@iot.navigationLink": "http://testserver/sensorthings/v1.1/Datastreams(1)/ObservedProperty", "Observations@iot.navigationLink": "http://testserver/sensorthings/v1.1/Datastreams(1)/Observations"}, {"@iot.id": 2, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Datastreams(2)", "name": "DATASTREAM_2", "description": "Datastream 2", "unitOfMeasurement": {"name": "Unit 2", "symbol": "U", "definition": "https://www.example.com/units/2"}, "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement", "phenomenonTime": "2024-01-01T00:00:00+00:00/2024-01-02T00:00:00+00:00", "resultTime": "2024-01-01T00:00:00+00:00/2024-01-02T00:00:00+00:00", "properties": {"code": "DATASTREAM"}, "Thing@iot.navigationLink": "http://testserver/sensorthings/v1.1/Datastreams(2)/Thing", "Sensor@iot.navigationLink": "http://testserver/sensorthings/v1.1/Datastreams(2)/Sensor", "ObservedProperty@iot.navigationLink": "http://testserver/sensorthings/v1.1/Datastreams(2)/ObservedProperty", "Observations@iot.navigationLink": "http://testserver/sensorthings/v1.1/Datastreams(2)/Observations"}]}'
    ),
    (  # Test Datastreams endpoint with pagination.
        'Datastreams',
        {'$count': True, '$skip': 1, '$top': 1},
        '{"@iot.count": 2, "value": [{"@iot.id": 2, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Datastreams(2)", "name": "DATASTREAM_2", "description": "Datastream 2", "unitOfMeasurement": {"name": "Unit 2", "symbol": "U", "definition": "https://www.example.com/units/2"}, "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement", "phenomenonTime": "2024-01-01T00:00:00+00:00/2024-01-02T00:00:00+00:00", "resultTime": "2024-01-01T00:00:00+00:00/2024-01-02T00:00:00+00:00", "properties": {"code": "DATASTREAM"}, "Thing@iot.navigationLink": "http://testserver/sensorthings/v1.1/Datastreams(2)/Thing", "Sensor@iot.navigationLink": "http://testserver/sensorthings/v1.1/Datastreams(2)/Sensor", "ObservedProperty@iot.navigationLink": "http://testserver/sensorthings/v1.1/Datastreams(2)/ObservedProperty", "Observations@iot.navigationLink": "http://testserver/sensorthings/v1.1/Datastreams(2)/Observations"}]}'
    ),
    (  # Test Datastreams endpoint select parameter.
        'Datastreams',
        {'$select': 'name'},
        '{"value": [{"name": "DATASTREAM_1"}, {"name": "DATASTREAM_2"}]}'
    ),
    (  # Test Datastreams endpoint select parameter (ID).
        'Datastreams',
        {'$select': 'id'},
        '{"value": [{"@iot.id": 1}, {"@iot.id": 2}]}'
    ),
    (  # Test Datastreams endpoint with metadata expanded.
        'Datastreams',
        {'$expand': 'Sensor,ObservedProperty'},
        '{"value": [{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Datastreams(1)", "name": "DATASTREAM_1", "description": "Datastream 1", "unitOfMeasurement": {"name": "Unit 1", "symbol": "U", "definition": "https://www.example.com/units/1"}, "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement", "phenomenonTime": "2024-01-01T00:00:00+00:00/2024-01-02T00:00:00+00:00", "resultTime": "2024-01-01T00:00:00+00:00/2024-01-02T00:00:00+00:00", "properties": {}, "Thing@iot.navigationLink": "http://testserver/sensorthings/v1.1/Datastreams(1)/Thing", "Sensor": {"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Sensors(1)", "name": "SENSOR_1", "description": "Sensor 1", "encodingType": "text/html", "metadata": "TEST", "properties": {}}, "ObservedProperty": {"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/ObservedProperties(1)", "name": "OBSERVED_PROPERTY_1", "definition": "https://www.example.com/observed-properties/1", "description": "Observed Property 1", "properties": {}}, "Observations@iot.navigationLink": "http://testserver/sensorthings/v1.1/Datastreams(1)/Observations"}, {"@iot.id": 2, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Datastreams(2)", "name": "DATASTREAM_2", "description": "Datastream 2", "unitOfMeasurement": {"name": "Unit 2", "symbol": "U", "definition": "https://www.example.com/units/2"}, "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement", "phenomenonTime": "2024-01-01T00:00:00+00:00/2024-01-02T00:00:00+00:00", "resultTime": "2024-01-01T00:00:00+00:00/2024-01-02T00:00:00+00:00", "properties": {"code": "DATASTREAM"}, "Thing@iot.navigationLink": "http://testserver/sensorthings/v1.1/Datastreams(2)/Thing", "Sensor": {"@iot.id": 2, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Sensors(2)", "name": "SENSOR_2", "description": "Sensor 2", "encodingType": "text/html", "metadata": "TEST", "properties": {"code": "SENSOR"}}, "ObservedProperty": {"@iot.id": 2, "@iot.selfLink": "http://testserver/sensorthings/v1.1/ObservedProperties(2)", "name": "OBSERVED_PROPERTY_2", "definition": "https://www.example.com/observed-properties/2", "description": "Observed Property 2", "properties": {"code": "OBSERVED_PROPERTY"}}, "Observations@iot.navigationLink": "http://testserver/sensorthings/v1.1/Datastreams(2)/Observations"}]}'
    ),
    (  # Test Datastreams endpoint with Things expanded.
        'Datastreams',
        {'$expand': 'Things/Locations'},
        '{"value": [{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Datastreams(1)", "name": "DATASTREAM_1", "description": "Datastream 1", "unitOfMeasurement": {"name": "Unit 1", "symbol": "U", "definition": "https://www.example.com/units/1"}, "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement", "phenomenonTime": "2024-01-01T00:00:00+00:00/2024-01-02T00:00:00+00:00", "resultTime": "2024-01-01T00:00:00+00:00/2024-01-02T00:00:00+00:00", "properties": {}, "Thing@iot.navigationLink": "http://testserver/sensorthings/v1.1/Datastreams(1)/Thing", "Sensor@iot.navigationLink": "http://testserver/sensorthings/v1.1/Datastreams(1)/Sensor", "ObservedProperty@iot.navigationLink": "http://testserver/sensorthings/v1.1/Datastreams(1)/ObservedProperty", "Observations@iot.navigationLink": "http://testserver/sensorthings/v1.1/Datastreams(1)/Observations"}, {"@iot.id": 2, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Datastreams(2)", "name": "DATASTREAM_2", "description": "Datastream 2", "unitOfMeasurement": {"name": "Unit 2", "symbol": "U", "definition": "https://www.example.com/units/2"}, "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement", "phenomenonTime": "2024-01-01T00:00:00+00:00/2024-01-02T00:00:00+00:00", "resultTime": "2024-01-01T00:00:00+00:00/2024-01-02T00:00:00+00:00", "properties": {"code": "DATASTREAM"}, "Thing@iot.navigationLink": "http://testserver/sensorthings/v1.1/Datastreams(2)/Thing", "Sensor@iot.navigationLink": "http://testserver/sensorthings/v1.1/Datastreams(2)/Sensor", "ObservedProperty@iot.navigationLink": "http://testserver/sensorthings/v1.1/Datastreams(2)/ObservedProperty", "Observations@iot.navigationLink": "http://testserver/sensorthings/v1.1/Datastreams(2)/Observations"}]}'
    ),
    (  # Test Datastreams endpoint with Observations expanded.
        'Datastreams',
        {'$expand': 'Observations'},
        '{"value": [{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Datastreams(1)", "name": "DATASTREAM_1", "description": "Datastream 1", "unitOfMeasurement": {"name": "Unit 1", "symbol": "U", "definition": "https://www.example.com/units/1"}, "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement", "phenomenonTime": "2024-01-01T00:00:00+00:00/2024-01-02T00:00:00+00:00", "resultTime": "2024-01-01T00:00:00+00:00/2024-01-02T00:00:00+00:00", "properties": {}, "Thing@iot.navigationLink": "http://testserver/sensorthings/v1.1/Datastreams(1)/Thing", "Sensor@iot.navigationLink": "http://testserver/sensorthings/v1.1/Datastreams(1)/Sensor", "ObservedProperty@iot.navigationLink": "http://testserver/sensorthings/v1.1/Datastreams(1)/ObservedProperty", "Observations": [{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Observations(1)", "phenomenonTime": "2024-01-01T00:00:00+00:00", "result": 10.0, "resultTime": "2024-01-01T00:00:00+00:00"}, {"@iot.id": 2, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Observations(2)", "phenomenonTime": "2024-01-02T00:00:00+00:00", "result": 15.0, "resultTime": "2024-01-02T00:00:00+00:00"}]}, {"@iot.id": 2, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Datastreams(2)", "name": "DATASTREAM_2", "description": "Datastream 2", "unitOfMeasurement": {"name": "Unit 2", "symbol": "U", "definition": "https://www.example.com/units/2"}, "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement", "phenomenonTime": "2024-01-01T00:00:00+00:00/2024-01-02T00:00:00+00:00", "resultTime": "2024-01-01T00:00:00+00:00/2024-01-02T00:00:00+00:00", "properties": {"code": "DATASTREAM"}, "Thing@iot.navigationLink": "http://testserver/sensorthings/v1.1/Datastreams(2)/Thing", "Sensor@iot.navigationLink": "http://testserver/sensorthings/v1.1/Datastreams(2)/Sensor", "ObservedProperty@iot.navigationLink": "http://testserver/sensorthings/v1.1/Datastreams(2)/ObservedProperty", "Observations": [{"@iot.id": 3, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Observations(3)", "phenomenonTime": "2024-01-01T00:00:00+00:00", "result": 20.0, "resultTime": "2024-01-01T00:00:00+00:00"}, {"@iot.id": 4, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Observations(4)", "phenomenonTime": "2024-01-02T00:00:00+00:00", "result": 25.0, "resultTime": "2024-01-02T00:00:00+00:00"}]}]}'
    ),
    (  # Test Datastreams with $ref.
        'Datastreams/$ref',
        {},
        '{"value": [{"@iot.selfLink": "http://testserver/sensorthings/v1.1/Datastreams(1)"}, {"@iot.selfLink": "http://testserver/sensorthings/v1.1/Datastreams(2)"}]}'
    ),
    (  # Test Datastream's Observations endpoint.
        'Datastreams(1)/Observations',
        {},
        '{"value": [{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Observations(1)", "phenomenonTime": "2024-01-01T00:00:00+00:00", "result": 10.0, "resultTime": "2024-01-01T00:00:00+00:00", "Datastream@iot.navigationLink": "http://testserver/sensorthings/v1.1/Observations(1)/Datastream", "FeatureOfInterest@iot.navigationLink": "http://testserver/sensorthings/v1.1/Observations(1)/FeatureOfInterest"}]}'
    ),
    (  # Test Observations endpoint with no query parameters.
        'Observations',
        {},
        '{"value": [{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Observations(1)", "phenomenonTime": "2024-01-01T00:00:00+00:00", "result": 10.0, "resultTime": "2024-01-01T00:00:00+00:00", "Datastream@iot.navigationLink": "http://testserver/sensorthings/v1.1/Observations(1)/Datastream", "FeatureOfInterest@iot.navigationLink": "http://testserver/sensorthings/v1.1/Observations(1)/FeatureOfInterest"}, {"@iot.id": 2, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Observations(2)", "phenomenonTime": "2024-01-02T00:00:00+00:00", "result": 15.0, "resultTime": "2024-01-02T00:00:00+00:00", "Datastream@iot.navigationLink": "http://testserver/sensorthings/v1.1/Observations(2)/Datastream", "FeatureOfInterest@iot.navigationLink": "http://testserver/sensorthings/v1.1/Observations(2)/FeatureOfInterest"}, {"@iot.id": 3, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Observations(3)", "phenomenonTime": "2024-01-01T00:00:00+00:00", "result": 20.0, "resultTime": "2024-01-01T00:00:00+00:00", "Datastream@iot.navigationLink": "http://testserver/sensorthings/v1.1/Observations(3)/Datastream", "FeatureOfInterest@iot.navigationLink": "http://testserver/sensorthings/v1.1/Observations(3)/FeatureOfInterest"}, {"@iot.id": 4, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Observations(4)", "phenomenonTime": "2024-01-02T00:00:00+00:00", "result": 25.0, "resultTime": "2024-01-02T00:00:00+00:00", "Datastream@iot.navigationLink": "http://testserver/sensorthings/v1.1/Observations(4)/Datastream", "FeatureOfInterest@iot.navigationLink": "http://testserver/sensorthings/v1.1/Observations(4)/FeatureOfInterest"}]}'
    ),
    (  # Test Observations endpoint with pagination.
        'Observations',
        {'$count': True, '$skip': 1, '$top': 1},
        '{"@iot.count": 4, "value": [{"@iot.id": 2, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Observations(2)", "phenomenonTime": "2024-01-02T00:00:00+00:00", "result": 15.0, "resultTime": "2024-01-02T00:00:00+00:00", "Datastream@iot.navigationLink": "http://testserver/sensorthings/v1.1/Observations(2)/Datastream", "FeatureOfInterest@iot.navigationLink": "http://testserver/sensorthings/v1.1/Observations(2)/FeatureOfInterest"}], "@iot.nextLink": "http://testserver/sensorthings/v1.1/Observations?$count=True&$skip=2&$top=1"}'
    ),
    (  # Test Observations endpoint select parameter.
        'Observations',
        {'$select': 'result'},
        '{"value": [{"result": 10.0}, {"result": 15.0}, {"result": 20.0}, {"result": 25.0}]}'
    ),
    (  # Test Observations endpoint select parameter (ID).
        'Observations',
        {'$select': 'id'},
        '{"value": [{"@iot.id": 1}, {"@iot.id": 2}, {"@iot.id": 3}, {"@iot.id": 4}]}'
    ),
    (  # Test Observations endpoint with Datastream expanded.
        'Observations',
        {'$expand': 'Datastream'},
        '{"value": [{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Observations(1)", "phenomenonTime": "2024-01-01T00:00:00+00:00", "result": 10.0, "resultTime": "2024-01-01T00:00:00+00:00", "Datastream": {"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Datastreams(1)", "name": "DATASTREAM_1", "description": "Datastream 1", "unitOfMeasurement": {"name": "Unit 1", "symbol": "U", "definition": "https://www.example.com/units/1"}, "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement", "phenomenonTime": "2024-01-01T00:00:00+00:00/2024-01-02T00:00:00+00:00", "resultTime": "2024-01-01T00:00:00+00:00/2024-01-02T00:00:00+00:00", "properties": {}}, "FeatureOfInterest@iot.navigationLink": "http://testserver/sensorthings/v1.1/Observations(1)/FeatureOfInterest"}, {"@iot.id": 2, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Observations(2)", "phenomenonTime": "2024-01-02T00:00:00+00:00", "result": 15.0, "resultTime": "2024-01-02T00:00:00+00:00", "Datastream": {"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Datastreams(1)", "name": "DATASTREAM_1", "description": "Datastream 1", "unitOfMeasurement": {"name": "Unit 1", "symbol": "U", "definition": "https://www.example.com/units/1"}, "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement", "phenomenonTime": "2024-01-01T00:00:00+00:00/2024-01-02T00:00:00+00:00", "resultTime": "2024-01-01T00:00:00+00:00/2024-01-02T00:00:00+00:00", "properties": {}}, "FeatureOfInterest@iot.navigationLink": "http://testserver/sensorthings/v1.1/Observations(2)/FeatureOfInterest"}, {"@iot.id": 3, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Observations(3)", "phenomenonTime": "2024-01-01T00:00:00+00:00", "result": 20.0, "resultTime": "2024-01-01T00:00:00+00:00", "Datastream": {"@iot.id": 2, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Datastreams(2)", "name": "DATASTREAM_2", "description": "Datastream 2", "unitOfMeasurement": {"name": "Unit 2", "symbol": "U", "definition": "https://www.example.com/units/2"}, "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement", "phenomenonTime": "2024-01-01T00:00:00+00:00/2024-01-02T00:00:00+00:00", "resultTime": "2024-01-01T00:00:00+00:00/2024-01-02T00:00:00+00:00", "properties": {"code": "DATASTREAM"}}, "FeatureOfInterest@iot.navigationLink": "http://testserver/sensorthings/v1.1/Observations(3)/FeatureOfInterest"}, {"@iot.id": 4, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Observations(4)", "phenomenonTime": "2024-01-02T00:00:00+00:00", "result": 25.0, "resultTime": "2024-01-02T00:00:00+00:00", "Datastream": {"@iot.id": 2, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Datastreams(2)", "name": "DATASTREAM_2", "description": "Datastream 2", "unitOfMeasurement": {"name": "Unit 2", "symbol": "U", "definition": "https://www.example.com/units/2"}, "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement", "phenomenonTime": "2024-01-01T00:00:00+00:00/2024-01-02T00:00:00+00:00", "resultTime": "2024-01-01T00:00:00+00:00/2024-01-02T00:00:00+00:00", "properties": {"code": "DATASTREAM"}}, "FeatureOfInterest@iot.navigationLink": "http://testserver/sensorthings/v1.1/Observations(4)/FeatureOfInterest"}]}'
    ),
    (  # Test Observations endpoint with FeatureOfInterest expanded.
        'Observations',
        {'$expand': 'FeatureOfInterest'},
        '{"value": [{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Observations(1)", "phenomenonTime": "2024-01-01T00:00:00+00:00", "result": 10.0, "resultTime": "2024-01-01T00:00:00+00:00", "Datastream@iot.navigationLink": "http://testserver/sensorthings/v1.1/Observations(1)/Datastream", "FeatureOfInterest": {"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/FeaturesOfInterest(1)", "name": "FEATURE_OF_INTEREST_1", "description": "Feature of Interest 1", "encodingType": "application/geo+json", "feature": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [41.745527, -111.813398]}, "properties": {}}, "properties": {}}}, {"@iot.id": 2, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Observations(2)", "phenomenonTime": "2024-01-02T00:00:00+00:00", "result": 15.0, "resultTime": "2024-01-02T00:00:00+00:00", "Datastream@iot.navigationLink": "http://testserver/sensorthings/v1.1/Observations(2)/Datastream", "FeatureOfInterest": {"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/FeaturesOfInterest(1)", "name": "FEATURE_OF_INTEREST_1", "description": "Feature of Interest 1", "encodingType": "application/geo+json", "feature": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [41.745527, -111.813398]}, "properties": {}}, "properties": {}}}, {"@iot.id": 3, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Observations(3)", "phenomenonTime": "2024-01-01T00:00:00+00:00", "result": 20.0, "resultTime": "2024-01-01T00:00:00+00:00", "Datastream@iot.navigationLink": "http://testserver/sensorthings/v1.1/Observations(3)/Datastream", "FeatureOfInterest": {"@iot.id": 2, "@iot.selfLink": "http://testserver/sensorthings/v1.1/FeaturesOfInterest(2)", "name": "FEATURE_OF_INTEREST_2", "description": "Feature of Interest 2", "encodingType": "application/geo+json", "feature": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [41.742053, -111.809579]}, "properties": {}}, "properties": {"code": "FEATURE_OF_INTEREST"}}}, {"@iot.id": 4, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Observations(4)", "phenomenonTime": "2024-01-02T00:00:00+00:00", "result": 25.0, "resultTime": "2024-01-02T00:00:00+00:00", "Datastream@iot.navigationLink": "http://testserver/sensorthings/v1.1/Observations(4)/Datastream", "FeatureOfInterest": {"@iot.id": 2, "@iot.selfLink": "http://testserver/sensorthings/v1.1/FeaturesOfInterest(2)", "name": "FEATURE_OF_INTEREST_2", "description": "Feature of Interest 2", "encodingType": "application/geo+json", "feature": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [41.742053, -111.809579]}, "properties": {}}, "properties": {"code": "FEATURE_OF_INTEREST"}}}]}'
    ),
    (  # Test Observations with $ref.
        'Observations/$ref',
        {},
        '{"value": [{"@iot.selfLink": "http://testserver/sensorthings/v1.1/Observations(1)"}, {"@iot.selfLink": "http://testserver/sensorthings/v1.1/Observations(2)"}, {"@iot.selfLink": "http://testserver/sensorthings/v1.1/Observations(3)"}, {"@iot.selfLink": "http://testserver/sensorthings/v1.1/Observations(4)"}]}'
    ),
    (  # Test FeaturesOfInterest endpoint with no query parameters.
        'FeaturesOfInterest',
        {},
        '{"value": [{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/FeaturesOfInterest(1)", "name": "FEATURE_OF_INTEREST_1", "description": "Feature of Interest 1", "encodingType": "application/geo+json", "feature": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [41.745527, -111.813398]}, "properties": {}}, "properties": {}, "Observations@iot.navigationLink": "http://testserver/sensorthings/v1.1/FeaturesOfInterest(1)/Observations"}, {"@iot.id": 2, "@iot.selfLink": "http://testserver/sensorthings/v1.1/FeaturesOfInterest(2)", "name": "FEATURE_OF_INTEREST_2", "description": "Feature of Interest 2", "encodingType": "application/geo+json", "feature": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [41.742053, -111.809579]}, "properties": {}}, "properties": {"code": "FEATURE_OF_INTEREST"}, "Observations@iot.navigationLink": "http://testserver/sensorthings/v1.1/FeaturesOfInterest(2)/Observations"}]}'
    ),
    (  # Test FeaturesOfInterest endpoint with pagination.
        'FeaturesOfInterest',
        {'$count': True, '$skip': 1, '$top': 1},
        '{"@iot.count": 2, "value": [{"@iot.id": 2, "@iot.selfLink": "http://testserver/sensorthings/v1.1/FeaturesOfInterest(2)", "name": "FEATURE_OF_INTEREST_2", "description": "Feature of Interest 2", "encodingType": "application/geo+json", "feature": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [41.742053, -111.809579]}, "properties": {}}, "properties": {"code": "FEATURE_OF_INTEREST"}, "Observations@iot.navigationLink": "http://testserver/sensorthings/v1.1/FeaturesOfInterest(2)/Observations"}]}'
    ),
    (  # Test FeaturesOfInterest endpoint select parameter.
        'FeaturesOfInterest',
        {'$select': 'name'},
        '{"value": [{"name": "FEATURE_OF_INTEREST_1"}, {"name": "FEATURE_OF_INTEREST_2"}]}'
    ),
    (  # Test FeaturesOfInterest endpoint select parameter (ID).
        'FeaturesOfInterest',
        {'$select': 'id'},
        '{"value": [{"@iot.id": 1}, {"@iot.id": 2}]}'
    ),
    (  # Test FeaturesOfInterest endpoint with Observations expanded.
        'FeaturesOfInterest',
        {'$expand': 'Observations'},
        '{"value": [{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/FeaturesOfInterest(1)", "name": "FEATURE_OF_INTEREST_1", "description": "Feature of Interest 1", "encodingType": "application/geo+json", "feature": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [41.745527, -111.813398]}, "properties": {}}, "properties": {}, "Observations": [{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Observations(1)", "phenomenonTime": "2024-01-01T00:00:00+00:00", "result": 10.0, "resultTime": "2024-01-01T00:00:00+00:00"}, {"@iot.id": 2, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Observations(2)", "phenomenonTime": "2024-01-02T00:00:00+00:00", "result": 15.0, "resultTime": "2024-01-02T00:00:00+00:00"}]}, {"@iot.id": 2, "@iot.selfLink": "http://testserver/sensorthings/v1.1/FeaturesOfInterest(2)", "name": "FEATURE_OF_INTEREST_2", "description": "Feature of Interest 2", "encodingType": "application/geo+json", "feature": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [41.742053, -111.809579]}, "properties": {}}, "properties": {"code": "FEATURE_OF_INTEREST"}, "Observations": [{"@iot.id": 3, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Observations(3)", "phenomenonTime": "2024-01-01T00:00:00+00:00", "result": 20.0, "resultTime": "2024-01-01T00:00:00+00:00"}, {"@iot.id": 4, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Observations(4)", "phenomenonTime": "2024-01-02T00:00:00+00:00", "result": 25.0, "resultTime": "2024-01-02T00:00:00+00:00"}]}]}'
    ),
    (  # Test FeaturesOfInterest with $ref.
        'FeaturesOfInterest/$ref',
        {},
        '{"value": [{"@iot.selfLink": "http://testserver/sensorthings/v1.1/FeaturesOfInterest(1)"}, {"@iot.selfLink": "http://testserver/sensorthings/v1.1/FeaturesOfInterest(2)"}]}'
    ),
    (  # Test FeatureOfInterest's Observations endpoint.
        'FeaturesOfInterest(1)/Observations',
        {},
        '{"value": [{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Observations(1)", "phenomenonTime": "2024-01-01T00:00:00+00:00", "result": 10.0, "resultTime": "2024-01-01T00:00:00+00:00", "Datastream@iot.navigationLink": "http://testserver/sensorthings/v1.1/Observations(1)/Datastream", "FeatureOfInterest@iot.navigationLink": "http://testserver/sensorthings/v1.1/Observations(1)/FeatureOfInterest"}]}'
    ),
])
@pytest.mark.django_db()
def test_sensorthings_list_endpoints(endpoint, query_params, expected_response):
    client = Client()

    response = client.get(
        f'http://127.0.0.1:8000/sensorthings/core/v1.1/{endpoint}',
        query_params
    )

    print(response.content)

    assert response.status_code == 200
    assert response.content.decode('utf-8') == orjson.dumps(orjson.loads(expected_response)).decode('utf-8')
