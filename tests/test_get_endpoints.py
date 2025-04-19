import pytest
import orjson
from django.test import Client


@pytest.mark.parametrize('endpoint, query_params, expected_response', [
    (  # Test Things endpoint with no query parameters.
        'Things(1)',
        {},
        '{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Things(1)", "name": "THING_1", "description": "Thing 1", "properties": {}, "Locations@iot.navigationLink": "http://testserver/sensorthings/v1.1/Things(1)/Locations", "HistoricalLocations@iot.navigationLink": "http://testserver/sensorthings/v1.1/Things(1)/HistoricalLocations", "Datastreams@iot.navigationLink": "http://testserver/sensorthings/v1.1/Things(1)/Datastreams"}'
    ),
    (  # Test Things endpoint select parameter.
        'Things(1)',
        {'$select': 'name,description'},
        '{"name": "THING_1", "description": "Thing 1"}'
    ),
    (  # Test Things endpoint select parameter (ID).
        'Things(1)',
        {'$select': 'id'},
        '{"@iot.id": 1}'
    ),
    (  # Test Things endpoint with Locations expanded.
        'Things(1)',
        {'$expand': 'Locations'},
        '{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Things(1)", "name": "THING_1", "description": "Thing 1", "properties": {}, "Locations": [{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Locations(1)", "name": "LOCATION_1", "description": "Location 1", "encodingType": "application/geo+json", "location": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [41.740004, -111.793743]}, "properties": {}}, "properties": {}}], "HistoricalLocations@iot.navigationLink": "http://testserver/sensorthings/v1.1/Things(1)/HistoricalLocations", "Datastreams@iot.navigationLink": "http://testserver/sensorthings/v1.1/Things(1)/Datastreams"}'
    ),
    (  # Test Things endpoint with Historical Locations expanded.
        'Things(1)',
        {'$expand': 'HistoricalLocations'},
        '{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Things(1)", "name": "THING_1", "description": "Thing 1", "properties": {}, "Locations@iot.navigationLink": "http://testserver/sensorthings/v1.1/Things(1)/Locations", "HistoricalLocations": [], "Datastreams@iot.navigationLink": "http://testserver/sensorthings/v1.1/Things(1)/Datastreams"}'
    ),
    (  # Test Things endpoint with Datastreams expanded.
        'Things(1)',
        {'$expand': 'Datastreams'},
        '{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Things(1)", "name": "THING_1", "description": "Thing 1", "properties": {}, "Locations@iot.navigationLink": "http://testserver/sensorthings/v1.1/Things(1)/Locations", "HistoricalLocations@iot.navigationLink": "http://testserver/sensorthings/v1.1/Things(1)/HistoricalLocations", "Datastreams": [{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Datastreams(1)", "name": "DATASTREAM_1", "description": "Datastream 1", "unitOfMeasurement": {"name": "Unit 1", "symbol": "U", "definition": "https://www.example.com/units/1"}, "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement", "phenomenonTime": "2024-01-01T00:00:00+00:00/2024-01-02T00:00:00+00:00", "resultTime": "2024-01-01T00:00:00+00:00/2024-01-02T00:00:00+00:00", "properties": {}}]}'
    ),
    (  # Test Things endpoint with multiple expanded components.
        'Things(1)',
        {'$expand': 'Locations/HistoricalLocations,Datastreams/Sensor,Datastreams/ObservedProperty'},
        '{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Things(1)", "name": "THING_1", "description": "Thing 1", "properties": {}, "Locations": [{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Locations(1)", "name": "LOCATION_1", "description": "Location 1", "encodingType": "application/geo+json", "location": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [41.740004, -111.793743]}, "properties": {}}, "properties": {}, "HistoricalLocations": []}], "HistoricalLocations@iot.navigationLink": "http://testserver/sensorthings/v1.1/Things(1)/HistoricalLocations", "Datastreams": [{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Datastreams(1)", "name": "DATASTREAM_1", "description": "Datastream 1", "unitOfMeasurement": {"name": "Unit 1", "symbol": "U", "definition": "https://www.example.com/units/1"}, "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement", "phenomenonTime": "2024-01-01T00:00:00+00:00/2024-01-02T00:00:00+00:00", "resultTime": "2024-01-01T00:00:00+00:00/2024-01-02T00:00:00+00:00", "properties": {}, "Sensor": {"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Sensors(1)", "name": "SENSOR_1", "description": "Sensor 1", "encodingType": "text/html", "metadata": "TEST", "properties": {}}, "ObservedProperty": {"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/ObservedProperties(1)", "name": "OBSERVED_PROPERTY_1", "definition": "https://www.example.com/observed-properties/1", "description": "Observed Property 1", "properties": {}}}]}'
    ),
    (  # Test Things value
        'Things(1)/name',
        {},
        '{"name": "THING_1"}'
    ),
    (  # Test Things value only
        'Things(1)/name/$value',
        {},
        '"THING_1"'
    ),
    (  # Test Locations endpoint with no query parameters.
        'Locations(1)',
        {},
        '{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Locations(1)", "name": "LOCATION_1", "description": "Location 1", "encodingType": "application/geo+json", "location": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [41.740004, -111.793743]}, "properties": {}}, "properties": {}, "Things@iot.navigationLink": "http://testserver/sensorthings/v1.1/Locations(1)/Things", "HistoricalLocations@iot.navigationLink": "http://testserver/sensorthings/v1.1/Locations(1)/HistoricalLocations"}'
    ),
    (  # Test Locations endpoint select parameter.
        'Locations(1)',
        {'$select': 'name,description'},
        '{"name": "LOCATION_1", "description": "Location 1"}'
    ),
    (  # Test Locations endpoint select parameter (ID).
        'Locations(1)',
        {'$select': 'id'},
        '{"@iot.id": 1}'
    ),
    (  # Test Locations endpoint with Things expanded.
        'Locations(1)',
        {'$expand': 'Things'},
        '{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Locations(1)", "name": "LOCATION_1", "description": "Location 1", "encodingType": "application/geo+json", "location": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [41.740004, -111.793743]}, "properties": {}}, "properties": {}, "Things": [{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Things(1)", "name": "THING_1", "description": "Thing 1", "properties": {}}], "HistoricalLocations@iot.navigationLink": "http://testserver/sensorthings/v1.1/Locations(1)/HistoricalLocations"}'
    ),
    (  # Test Locations endpoint with HistoricalLocations expanded.
        'Locations(1)',
        {'$expand': 'HistoricalLocations'},
        '{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Locations(1)", "name": "LOCATION_1", "description": "Location 1", "encodingType": "application/geo+json", "location": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [41.740004, -111.793743]}, "properties": {}}, "properties": {}, "Things@iot.navigationLink": "http://testserver/sensorthings/v1.1/Locations(1)/Things", "HistoricalLocations": []}'
    ),
    (  # Test Locations endpoint with multiple expanded components.
        'Locations(1)',
        {'$expand': 'HistoricalLocations,Things'},
        '{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Locations(1)", "name": "LOCATION_1", "description": "Location 1", "encodingType": "application/geo+json", "location": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [41.740004, -111.793743]}, "properties": {}}, "properties": {}, "Things": [{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Things(1)", "name": "THING_1", "description": "Thing 1", "properties": {}}], "HistoricalLocations": []}'
    ),
    (  # Test Locations value
        'Locations(1)/name',
        {},
        '{"name": "LOCATION_1"}'
    ),
    (  # Test Locations value only
        'Locations(1)/name/$value',
        {},
        '"LOCATION_1"'
    ),
    (  # Test HistoricalLocations endpoint with no query parameters.
        'HistoricalLocations(1)',
        {},
        '{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/HistoricalLocations(1)", "time": "2024-01-01T00:00:00+00:00", "Thing@iot.navigationLink": "http://testserver/sensorthings/v1.1/HistoricalLocations(1)/Thing"}'
    ),
    (  # Test HistoricalLocations endpoint select parameter.
        'HistoricalLocations(1)',
        {'$select': 'time'},
        '{"time": "2024-01-01T00:00:00+00:00"}'
    ),
    (  # Test HistoricalLocations endpoint select parameter (ID).
        'HistoricalLocations(1)',
        {'$select': 'id'},
        '{"@iot.id": 1}'
    ),
    (  # Test HistoricalLocations endpoint with Locations expanded.
        'HistoricalLocations(1)',
        {'$expand': 'Locations'},
        '{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/HistoricalLocations(1)", "time": "2024-01-01T00:00:00+00:00", "Thing@iot.navigationLink": "http://testserver/sensorthings/v1.1/HistoricalLocations(1)/Thing"}'
    ),
    (  # Test HistoricalLocations endpoint with Thing expanded.
        'HistoricalLocations(1)',
        {'$expand': 'Thing'},
        '{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/HistoricalLocations(1)", "time": "2024-01-01T00:00:00+00:00", "Thing": {"@iot.id": 2, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Things(2)", "name": "THING_2", "description": "Thing 2", "properties": {"code": "THING"}}}'
    ),
    (  # Test HistoricalLocations endpoint with multiple expanded components.
        'HistoricalLocations(1)',
        {'$expand': 'Locations,Thing'},
        '{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/HistoricalLocations(1)", "time": "2024-01-01T00:00:00+00:00", "Thing": {"@iot.id": 2, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Things(2)", "name": "THING_2", "description": "Thing 2", "properties": {"code": "THING"}}}'
    ),
    (  # Test HistoricalLocations value
        'HistoricalLocations(1)/time',
        {},
        '{"time": "2024-01-01T00:00:00+00:00"}'
    ),
    (  # Test HistoricalLocations value only
        'HistoricalLocations(1)/time/$value',
        {},
        '"2024-01-01T00:00:00Z"'
    ),
    (  # Test HistoricalLocation's Thing endpoint.
        'HistoricalLocations(1)/Thing',
        {},
        '{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Things(1)", "name": "THING_1", "description": "Thing 1", "properties": {}, "Locations@iot.navigationLink": "http://testserver/sensorthings/v1.1/Things(1)/Locations", "HistoricalLocations@iot.navigationLink": "http://testserver/sensorthings/v1.1/Things(1)/HistoricalLocations", "Datastreams@iot.navigationLink": "http://testserver/sensorthings/v1.1/Things(1)/Datastreams"}'
    ),
    (  # Test Sensors endpoint with no query parameters.
        'Sensors(1)',
        {},
        '{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Sensors(1)", "name": "SENSOR_1", "description": "Sensor 1", "encodingType": "text/html", "metadata": "TEST", "properties": {}, "Datastreams@iot.navigationLink": "http://testserver/sensorthings/v1.1/Sensors(1)/Datastreams"}'
    ),
    (  # Test Sensors endpoint select parameter.
        'Sensors(1)',
        {'$select': 'name'},
        '{"name": "SENSOR_1"}'
    ),
    (  # Test Sensors endpoint select parameter (ID).
        'Sensors(1)',
        {'$select': 'id'},
        '{"@iot.id": 1}'
    ),
    (  # Test Sensors endpoint with Datastreams expanded.
        'Sensors(1)',
        {'$expand': 'Datastreams'},
        '{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Sensors(1)", "name": "SENSOR_1", "description": "Sensor 1", "encodingType": "text/html", "metadata": "TEST", "properties": {}, "Datastreams": [{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Datastreams(1)", "name": "DATASTREAM_1", "description": "Datastream 1", "unitOfMeasurement": {"name": "Unit 1", "symbol": "U", "definition": "https://www.example.com/units/1"}, "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement", "phenomenonTime": "2024-01-01T00:00:00+00:00/2024-01-02T00:00:00+00:00", "resultTime": "2024-01-01T00:00:00+00:00/2024-01-02T00:00:00+00:00", "properties": {}}]}'
    ),
    (  # Test Sensors value
        'Sensors(1)/name',
        {},
        '{"name": "SENSOR_1"}'
    ),
    (  # Test Sensors value only
        'Sensors(1)/name/$value',
        {},
        '"SENSOR_1"'
    ),
    (  # Test ObservedProperties endpoint with no query parameters.
        'ObservedProperties(1)',
        {},
        '{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/ObservedProperties(1)", "name": "OBSERVED_PROPERTY_1", "definition": "https://www.example.com/observed-properties/1", "description": "Observed Property 1", "properties": {}, "Datastreams@iot.navigationLink": "http://testserver/sensorthings/v1.1/ObservedProperties(1)/Datastreams"}'
    ),
    (  # Test ObservedProperties endpoint select parameter.
        'ObservedProperties(1)',
        {'$select': 'name'},
        '{"name": "OBSERVED_PROPERTY_1"}'
    ),
    (  # Test ObservedProperties endpoint select parameter (ID).
        'ObservedProperties(1)',
        {'$select': 'id'},
        '{"@iot.id": 1}'
    ),
    (  # Test ObservedProperties endpoint with Datastreams expanded.
        'ObservedProperties(1)',
        {'$expand': 'Datastreams'},
        '{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/ObservedProperties(1)", "name": "OBSERVED_PROPERTY_1", "definition": "https://www.example.com/observed-properties/1", "description": "Observed Property 1", "properties": {}, "Datastreams": [{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Datastreams(1)", "name": "DATASTREAM_1", "description": "Datastream 1", "unitOfMeasurement": {"name": "Unit 1", "symbol": "U", "definition": "https://www.example.com/units/1"}, "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement", "phenomenonTime": "2024-01-01T00:00:00+00:00/2024-01-02T00:00:00+00:00", "resultTime": "2024-01-01T00:00:00+00:00/2024-01-02T00:00:00+00:00", "properties": {}}]}'
    ),
    (  # Test ObservedProperties value
        'ObservedProperties(1)/name',
        {},
        '{"name": "OBSERVED_PROPERTY_1"}'
    ),
    (  # Test ObservedProperties value only
        'ObservedProperties(1)/name/$value',
        {},
        '"OBSERVED_PROPERTY_1"'
    ),
    (  # Test Datastreams endpoint with no query parameters.
        'Datastreams(1)',
        {},
        '{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Datastreams(1)", "name": "DATASTREAM_1", "description": "Datastream 1", "unitOfMeasurement": {"name": "Unit 1", "symbol": "U", "definition": "https://www.example.com/units/1"}, "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement", "phenomenonTime": "2024-01-01T00:00:00+00:00/2024-01-02T00:00:00+00:00", "resultTime": "2024-01-01T00:00:00+00:00/2024-01-02T00:00:00+00:00", "properties": {}, "Thing@iot.navigationLink": "http://testserver/sensorthings/v1.1/Datastreams(1)/Thing", "Sensor@iot.navigationLink": "http://testserver/sensorthings/v1.1/Datastreams(1)/Sensor", "ObservedProperty@iot.navigationLink": "http://testserver/sensorthings/v1.1/Datastreams(1)/ObservedProperty", "Observations@iot.navigationLink": "http://testserver/sensorthings/v1.1/Datastreams(1)/Observations"}'
    ),
    (  # Test Datastreams endpoint select parameter.
        'Datastreams(1)',
        {'$select': 'name'},
        '{"name": "DATASTREAM_1"}'
    ),
    (  # Test Datastreams endpoint select parameter (ID).
        'Datastreams(1)',
        {'$select': 'id'},
        '{"@iot.id": 1}'
    ),
    (  # Test Datastreams endpoint with metadata expanded.
        'Datastreams(1)',
        {'$expand': 'Sensor,ObservedProperty'},
        '{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Datastreams(1)", "name": "DATASTREAM_1", "description": "Datastream 1", "unitOfMeasurement": {"name": "Unit 1", "symbol": "U", "definition": "https://www.example.com/units/1"}, "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement", "phenomenonTime": "2024-01-01T00:00:00+00:00/2024-01-02T00:00:00+00:00", "resultTime": "2024-01-01T00:00:00+00:00/2024-01-02T00:00:00+00:00", "properties": {}, "Thing@iot.navigationLink": "http://testserver/sensorthings/v1.1/Datastreams(1)/Thing", "Sensor": {"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Sensors(1)", "name": "SENSOR_1", "description": "Sensor 1", "encodingType": "text/html", "metadata": "TEST", "properties": {}}, "ObservedProperty": {"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/ObservedProperties(1)", "name": "OBSERVED_PROPERTY_1", "definition": "https://www.example.com/observed-properties/1", "description": "Observed Property 1", "properties": {}}, "Observations@iot.navigationLink": "http://testserver/sensorthings/v1.1/Datastreams(1)/Observations"}'
    ),
    (  # Test Datastreams endpoint with Things expanded.
        'Datastreams(1)',
        {'$expand': 'Things/Locations'},
        '{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Datastreams(1)", "name": "DATASTREAM_1", "description": "Datastream 1", "unitOfMeasurement": {"name": "Unit 1", "symbol": "U", "definition": "https://www.example.com/units/1"}, "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement", "phenomenonTime": "2024-01-01T00:00:00+00:00/2024-01-02T00:00:00+00:00", "resultTime": "2024-01-01T00:00:00+00:00/2024-01-02T00:00:00+00:00", "properties": {}, "Thing@iot.navigationLink": "http://testserver/sensorthings/v1.1/Datastreams(1)/Thing", "Sensor@iot.navigationLink": "http://testserver/sensorthings/v1.1/Datastreams(1)/Sensor", "ObservedProperty@iot.navigationLink": "http://testserver/sensorthings/v1.1/Datastreams(1)/ObservedProperty", "Observations@iot.navigationLink": "http://testserver/sensorthings/v1.1/Datastreams(1)/Observations"}'
    ),
    (  # Test Datastreams endpoint with Observations expanded.
        'Datastreams(1)',
        {'$expand': 'Observations'},
        '{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Datastreams(1)", "name": "DATASTREAM_1", "description": "Datastream 1", "unitOfMeasurement": {"name": "Unit 1", "symbol": "U", "definition": "https://www.example.com/units/1"}, "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement", "phenomenonTime": "2024-01-01T00:00:00+00:00/2024-01-02T00:00:00+00:00", "resultTime": "2024-01-01T00:00:00+00:00/2024-01-02T00:00:00+00:00", "properties": {}, "Thing@iot.navigationLink": "http://testserver/sensorthings/v1.1/Datastreams(1)/Thing", "Sensor@iot.navigationLink": "http://testserver/sensorthings/v1.1/Datastreams(1)/Sensor", "ObservedProperty@iot.navigationLink": "http://testserver/sensorthings/v1.1/Datastreams(1)/ObservedProperty", "Observations": [{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Observations(1)", "phenomenonTime": "2024-01-01T00:00:00+00:00", "result": 10.0, "resultTime": "2024-01-01T00:00:00+00:00"}, {"@iot.id": 2, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Observations(2)", "phenomenonTime": "2024-01-02T00:00:00+00:00", "result": 15.0, "resultTime": "2024-01-02T00:00:00+00:00"}]}'
    ),
    (  # Test Datastreams value
        'Datastreams(1)/name',
        {},
        '{"name": "DATASTREAM_1"}'
    ),
    (  # Test Datastreams value only
        'Datastreams(1)/name/$value',
        {},
        '"DATASTREAM_1"'
    ),
    (  # Test Datastream's Thing endpoint.
        'Datastreams(1)/Thing',
        {},
        '{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Things(1)", "name": "THING_1", "description": "Thing 1", "properties": {}, "Locations@iot.navigationLink": "http://testserver/sensorthings/v1.1/Things(1)/Locations", "HistoricalLocations@iot.navigationLink": "http://testserver/sensorthings/v1.1/Things(1)/HistoricalLocations", "Datastreams@iot.navigationLink": "http://testserver/sensorthings/v1.1/Things(1)/Datastreams"}'
    ),
    (  # Test Datastream's Sensor endpoint.
        'Datastreams(1)/Sensor',
        {},
        '{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Sensors(1)", "name": "SENSOR_1", "description": "Sensor 1", "encodingType": "text/html", "metadata": "TEST", "properties": {}, "Datastreams@iot.navigationLink": "http://testserver/sensorthings/v1.1/Sensors(1)/Datastreams"}'
    ),
    (  # Test Datastream's ObservedProperty endpoint.
        'Datastreams(1)/ObservedProperty',
        {},
        '{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/ObservedProperties(1)", "name": "OBSERVED_PROPERTY_1", "definition": "https://www.example.com/observed-properties/1", "description": "Observed Property 1", "properties": {}, "Datastreams@iot.navigationLink": "http://testserver/sensorthings/v1.1/ObservedProperties(1)/Datastreams"}'
    ),
    (  # Test Observations endpoint with no query parameters.
        'Observations(1)',
        {},
        '{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Observations(1)", "phenomenonTime": "2024-01-01T00:00:00+00:00", "result": 10.0, "resultTime": "2024-01-01T00:00:00+00:00", "Datastream@iot.navigationLink": "http://testserver/sensorthings/v1.1/Observations(1)/Datastream", "FeatureOfInterest@iot.navigationLink": "http://testserver/sensorthings/v1.1/Observations(1)/FeatureOfInterest"}'
    ),
    (  # Test Observations endpoint select parameter.
        'Observations(1)',
        {'$select': 'result'},
        '{"result": 10.0}'
    ),
    (  # Test Observations endpoint select parameter (ID).
        'Observations(1)',
        {'$select': 'id'},
        '{"@iot.id": 1}'
    ),
    (  # Test Observations endpoint with Datastream expanded.
        'Observations(1)',
        {'$expand': 'Datastream'},
        '{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Observations(1)", "phenomenonTime": "2024-01-01T00:00:00+00:00", "result": 10.0, "resultTime": "2024-01-01T00:00:00+00:00", "Datastream": {"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Datastreams(1)", "name": "DATASTREAM_1", "description": "Datastream 1", "unitOfMeasurement": {"name": "Unit 1", "symbol": "U", "definition": "https://www.example.com/units/1"}, "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement", "phenomenonTime": "2024-01-01T00:00:00+00:00/2024-01-02T00:00:00+00:00", "resultTime": "2024-01-01T00:00:00+00:00/2024-01-02T00:00:00+00:00", "properties": {}}, "FeatureOfInterest@iot.navigationLink": "http://testserver/sensorthings/v1.1/Observations(1)/FeatureOfInterest"}'
    ),
    (  # Test Observations endpoint with FeatureOfInterest expanded.
        'Observations(1)',
        {'$expand': 'FeatureOfInterest'},
        '{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Observations(1)", "phenomenonTime": "2024-01-01T00:00:00+00:00", "result": 10.0, "resultTime": "2024-01-01T00:00:00+00:00", "Datastream@iot.navigationLink": "http://testserver/sensorthings/v1.1/Observations(1)/Datastream", "FeatureOfInterest": {"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/FeaturesOfInterest(1)", "name": "FEATURE_OF_INTEREST_1", "description": "Feature of Interest 1", "encodingType": "application/geo+json", "feature": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [41.745527, -111.813398]}, "properties": {}}, "properties": {}}}'
    ),
    (  # Test Observations value
        'Observations(1)/result',
        {},
        '{"result": 10.0}'
    ),
    (  # Test Observations value only
        'Observations(1)/result/$value',
        {},
        '"10"'
    ),
    (  # Test Observation's Datastream endpoint.
        'Observations(1)/Datastream',
        {},
        '{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Datastreams(1)", "name": "DATASTREAM_1", "description": "Datastream 1", "unitOfMeasurement": {"name": "Unit 1", "symbol": "U", "definition": "https://www.example.com/units/1"}, "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement", "phenomenonTime": "2024-01-01T00:00:00+00:00/2024-01-02T00:00:00+00:00", "resultTime": "2024-01-01T00:00:00+00:00/2024-01-02T00:00:00+00:00", "properties": {}, "Thing@iot.navigationLink": "http://testserver/sensorthings/v1.1/Datastreams(1)/Thing", "Sensor@iot.navigationLink": "http://testserver/sensorthings/v1.1/Datastreams(1)/Sensor", "ObservedProperty@iot.navigationLink": "http://testserver/sensorthings/v1.1/Datastreams(1)/ObservedProperty", "Observations@iot.navigationLink": "http://testserver/sensorthings/v1.1/Datastreams(1)/Observations"}'
    ),
    (  # Test Observation's FeatureOfInterest endpoint.
        'Observations(1)/FeatureOfInterest',
        {},
        '{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/FeaturesOfInterest(1)", "name": "FEATURE_OF_INTEREST_1", "description": "Feature of Interest 1", "encodingType": "application/geo+json", "feature": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [41.745527, -111.813398]}, "properties": {}}, "properties": {}, "Observations@iot.navigationLink": "http://testserver/sensorthings/v1.1/FeaturesOfInterest(1)/Observations"}'
    ),
    (  # Test FeaturesOfInterest endpoint with no query parameters.
        'FeaturesOfInterest(1)',
        {},
        '{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/FeaturesOfInterest(1)", "name": "FEATURE_OF_INTEREST_1", "description": "Feature of Interest 1", "encodingType": "application/geo+json", "feature": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [41.745527, -111.813398]}, "properties": {}}, "properties": {}, "Observations@iot.navigationLink": "http://testserver/sensorthings/v1.1/FeaturesOfInterest(1)/Observations"}'
    ),
    (  # Test FeaturesOfInterest endpoint select parameter.
        'FeaturesOfInterest(1)',
        {'$select': 'name'},
        '{"name": "FEATURE_OF_INTEREST_1"}'
    ),
    (  # Test FeaturesOfInterest endpoint select parameter (ID).
        'FeaturesOfInterest(1)',
        {'$select': 'id'},
        '{"@iot.id": 1}'
    ),
    (  # Test FeaturesOfInterest endpoint with Datastream expanded.
        'FeaturesOfInterest(1)',
        {'$expand': 'Observations'},
        '{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/FeaturesOfInterest(1)", "name": "FEATURE_OF_INTEREST_1", "description": "Feature of Interest 1", "encodingType": "application/geo+json", "feature": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [41.745527, -111.813398]}, "properties": {}}, "properties": {}, "Observations": [{"@iot.id": 1, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Observations(1)", "phenomenonTime": "2024-01-01T00:00:00+00:00", "result": 10.0, "resultTime": "2024-01-01T00:00:00+00:00"}, {"@iot.id": 2, "@iot.selfLink": "http://testserver/sensorthings/v1.1/Observations(2)", "phenomenonTime": "2024-01-02T00:00:00+00:00", "result": 15.0, "resultTime": "2024-01-02T00:00:00+00:00"}]}'
    ),
    (  # Test FeaturesOfInterest value
        'FeaturesOfInterest(1)/name',
        {},
        '{"name": "FEATURE_OF_INTEREST_1"}'
    ),
    (  # Test FeaturesOfInterest value only
        'FeaturesOfInterest(1)/name/$value',
        {},
        '"FEATURE_OF_INTEREST_1"'
    ),
])
@pytest.mark.django_db()
def test_sensorthings_get_endpoints(endpoint, query_params, expected_response):
    client = Client()

    response = client.get(
        f'http://127.0.0.1:8000/sensorthings/core/v1.1/{endpoint}',
        query_params
    )

    print(response.content)

    assert response.status_code == 200
    assert response.content.decode('utf-8') == orjson.dumps(orjson.loads(expected_response)).decode('utf-8')


@pytest.mark.parametrize('endpoint', [
    ('Things(10)',),
    ('Locations(10)',),
    ('HistoricalLocations(10)',),
    ('Sensors(10)',),
    ('ObservedProperties(10)',),
    ('Datastreams(10)',),
    ('Observations(10)',),
    ('FeaturesOfInterest(10)',),
])
@pytest.mark.django_db()
def test_sensorthings_get_endpoints_404(endpoint):
    client = Client()

    response = client.get(
        f'http://127.0.0.1:8000/sensorthings/core/v1.1/{endpoint}',
        {}
    )

    print(response.content)

    assert response.status_code == 404
