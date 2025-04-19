from django.conf import settings

ST_VERSION = '1.1'

ST_CONFORMANCE = getattr(settings, 'ST_CONFORMANCE', [
    'http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel',
    'http://www.opengis.net/spec/iot_sensing/1.1/req/resource-path/resource-path-to-entities',
    'http://www.opengis.net/spec/iot_sensing/1.1/req/request-data',
    'http://www.opengis.net/spec/iot_sensing/1.1/req/create-update-delete/create-entity',
    'http://www.opengis.net/spec/iot_sensing/1.1/req/create-update-delete/link-to-existing-entities',
    'http://www.opengis.net/spec/iot_sensing/1.1/req/create-update-delete/deep-insert',
    'http://www.opengis.net/spec/iot_sensing/1.1/req/create-update-delete/deep-insert-status-code',
    'http://www.opengis.net/spec/iot_sensing/1.1/req/create-update-delete/update-entity',
    'http://www.opengis.net/spec/iot_sensing/1.1/req/create-update-delete/delete-entity',
    'http://www.opengis.net/spec/iot_sensing/1.1/req/create-update-delete/historical-location-auto-creation'
])

ST_API_PREFIX = getattr(settings, 'ST_API_PREFIX', 'sensorthings')
ST_API_ID_QUALIFIER = getattr(settings, 'ST_API_ID_QUALIFIER', '')
ST_API_ID_TYPE = getattr(settings, 'ST_API_ID_TYPE', str)

ST_CAPABILITIES = getattr(settings, 'ST_CAPABILITIES', [
    {
        'NAME': 'Things',
        'SINGULAR_NAME': 'Thing',
        'VIEW': 'list_things'
    },
    {
        'NAME': 'Locations',
        'SINGULAR_NAME': 'Location',
        'VIEW': 'list_locations'
    },
    {
        'NAME': 'HistoricalLocations',
        'SINGULAR_NAME': 'HistoricalLocation',
        'VIEW': 'list_historical_locations'
    },
    {
        'NAME': 'Datastreams',
        'SINGULAR_NAME': 'Datastream',
        'VIEW': 'list_datastreams'
    },
    {
        'NAME': 'Sensors',
        'SINGULAR_NAME': 'Sensor',
        'VIEW': 'list_sensors'
    },
    {
        'NAME': 'Observations',
        'SINGULAR_NAME': 'Observation',
        'VIEW': 'list_observations'
    },
    {
        'NAME': 'ObservedProperties',
        'SINGULAR_NAME': 'ObservedProperty',
        'VIEW': 'list_observed_properties'
    },
    {
        'NAME': 'FeaturesOfInterest',
        'SINGULAR_NAME': 'FeatureOfInterest',
        'VIEW': 'list_features_of_interest'
    },
])

PROXY_BASE_URL = getattr(settings, 'PROXY_BASE_URL', None)
