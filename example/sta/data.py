things = {
    1: {
        'id': 1,
        'name': 'THING_1',
        'description': 'Thing 1',
        'properties': {},
        'location_ids': [1]
    },
    2: {
        'id': 2,
        'name': 'THING_2',
        'description': 'Thing 2',
        'properties': {
            'code': 'THING'
        },
        'location_ids': [2, 3]
    }
}


locations = {
    1: {
        'id': 1,
        'name': 'LOCATION_1',
        'description': 'Location 1',
        'encoding_type': 'application/geo+json',
        'location': {
            'type': 'Feature',
            'properties': {},
            'geometry': {
                'type': 'Point',
                'coordinates': [41.740004, -111.793743]
            }
        },
        'properties': {},
        'thing_ids': [1],
        'historical_location_ids': [],
    },
    2: {
        'id': 2,
        'name': 'LOCATION_2',
        'description': 'Location 2',
        'encoding_type': 'application/geo+json',
        'location': {
            'type': 'Feature',
            'properties': {},
            'geometry': {
                'type': 'Point',
                'coordinates': [41.745527, -111.813398]
            }
        },
        'properties': {
            'code': 'LOCATION'
        },
        'thing_ids': [2],
        'historical_location_ids': [1, 2]
    },
    3: {
        'id': 3,
        'name': 'LOCATION_3',
        'description': 'Location 3',
        'encoding_type': 'application/geo+json',
        'location': {
            'type': 'Feature',
            'properties': {},
            'geometry': {
                'type': 'Point',
                'coordinates': [41.742053, -111.809579]
            }
        },
        'properties': {},
        'thing_ids': [2],
        'historical_location_ids': [2],
    }
}


historical_locations = {
    1: {
        'id': 1,
        'time': '2024-01-01T00:00:00Z',
        'thing_id': 2,
        'location_ids': [2]
    },
    2: {
        'id': 2,
        'time': '2024-01-02T00:00:00Z',
        'thing_id': 2,
        'location_ids': [2, 3]
    }
}

sensors = {
    1: {
        'id': 1,
        'name': 'SENSOR_1',
        'description': 'Sensor 1',
        'encoding_type': 'text/html',
        'metadata': 'TEST',
        'properties': {}
    },
    2: {
        'id': 2,
        'name': 'SENSOR_2',
        'description': 'Sensor 2',
        'encoding_type': 'text/html',
        'metadata': 'TEST',
        'properties': {
            'code': 'SENSOR'
        }
    }
}


observed_properties = {
    1: {
        'id': 1,
        'name': 'OBSERVED_PROPERTY_1',
        'definition': 'https://www.example.com/observed-properties/1',
        'description': 'Observed Property 1',
        'properties': {}
    },
    2: {
        'id': 2,
        'name': 'OBSERVED_PROPERTY_2',
        'definition': 'https://www.example.com/observed-properties/2',
        'description': 'Observed Property 2',
        'properties': {
            'code': 'OBSERVED_PROPERTY'
        }
    }
}


features_of_interest = {
    1: {
        'id': 1,
        'name': 'FEATURE_OF_INTEREST_1',
        'description': 'Feature of Interest 1',
        'encoding_type': 'application/geo+json',
        'feature': {
            'type': 'Feature',
            'properties': {},
            'geometry': {
                'type': 'Point',
                'coordinates': [41.745527, -111.813398]
            }
        },
        'properties': {}
    },
    2: {
        'id': 2,
        'name': 'FEATURE_OF_INTEREST_2',
        'description': 'Feature of Interest 2',
        'encoding_type': 'application/geo+json',
        'feature': {
            'type': 'Feature',
            'properties': {},
            'geometry': {
                'type': 'Point',
                'coordinates': [41.742053, -111.809579]
            }
        },
        'properties': {
            'code': 'FEATURE_OF_INTEREST'
        }
    }
}


datastreams = {
    1: {
        'id': 1,
        'name': 'DATASTREAM_1',
        'description': 'Datastream 1',
        'thing_id': 1,
        'sensor_id': 1,
        'observed_property_id': 1,
        'unit_of_measurement': {
            'name': 'Unit 1',
            'symbol': 'U',
            'definition': 'https://www.example.com/units/1',
        },
        'observation_type': 'http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement',
        'phenomenon_time': '2024-01-01T00:00:00Z/2024-01-02T00:00:00Z',
        'result_time': '2024-01-01T00:00:00Z/2024-01-02T00:00:00Z',
        'properties': {}
    },
    2: {
        'id': 2,
        'name': 'DATASTREAM_2',
        'description': 'Datastream 2',
        'thing_id': 2,
        'sensor_id': 2,
        'observed_property_id': 2,
        'unit_of_measurement': {
            'name': 'Unit 2',
            'symbol': 'U',
            'definition': 'https://www.example.com/units/2',
        },
        'observation_type': 'http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement',
        'phenomenon_time': '2024-01-01T00:00:00Z/2024-01-02T00:00:00Z',
        'result_time': '2024-01-01T00:00:00Z/2024-01-02T00:00:00Z',
        'properties': {
            'code': 'DATASTREAM'
        }
    }
}

observations = {
    1: {
        'id': 1,
        'phenomenon_time': '2024-01-01T00:00:00Z',
        'result_time': '2024-01-01T00:00:00Z',
        'result': 10,
        'datastream_id': 1,
        'feature_of_interest_id': 1,
        'properties': {}
    },
    2: {
        'id': 2,
        'phenomenon_time': '2024-01-02T00:00:00Z',
        'result_time': '2024-01-02T00:00:00Z',
        'result': 15,
        'datastream_id': 1,
        'feature_of_interest_id': 1,
        'properties': {
            'code': 'OBSERVATION'
        }
    },
    3: {
        'id': 3,
        'phenomenon_time': '2024-01-01T00:00:00Z',
        'result_time': '2024-01-01T00:00:00Z',
        'result': 20,
        'datastream_id': 2,
        'feature_of_interest_id': 2,
        'properties': {}
    },
    4: {
        'id': 4,
        'phenomenon_time': '2024-01-02T00:00:00Z',
        'result_time': '2024-01-02T00:00:00Z',
        'result': 25,
        'datastream_id': 2,
        'feature_of_interest_id': 2,
        'properties': {
            'code': 'OBSERVATION'
        }
    },
}
