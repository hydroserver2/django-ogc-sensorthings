from sensorthings.versions.v1_1 import sta
from .base import PartialMetaclass, BaseSchema, BaseCollectionSchema, BaseEntitySchema, IdSchema
from .factory import SchemaFactory
from .root import ServiceRootSchema
from .query import EntityQuery, CollectionQuery
from .thing import ThingFields
from .location import LocationFields
from .historical_location import HistoricalLocationFields
from .datastream import DatastreamFields
from .sensor import SensorFields
from .observed_property import ObservedPropertyFields
from .observation import ObservationFields
from .feature_of_interest import FeatureOfInterestFields
from .unit_of_measurement import UnitOfMeasurement


schema_factory = SchemaFactory(fields_registry={
    "Thing": ThingFields,
    "Location": LocationFields,
    "HistoricalLocation": HistoricalLocationFields,
    "Datastream": DatastreamFields,
    "Sensor": SensorFields,
    "ObservedProperty": ObservedPropertyFields,
    "Observation": ObservationFields,
    "FeatureOfInterest": FeatureOfInterestFields,
})

ThingResponse = schema_factory.build_entity_response(sta.THING_ENTITY)
ThingCollectionResponse = schema_factory.build_collection_response(sta.THING_ENTITY)
ThingPostBody = schema_factory.build_post_body(sta.THING_ENTITY)
ThingPatchBody = schema_factory.build_patch_body(sta.THING_ENTITY)

LocationResponse = schema_factory.build_entity_response(sta.LOCATION_ENTITY)
LocationCollectionResponse = schema_factory.build_collection_response(sta.LOCATION_ENTITY)
LocationPostBody = schema_factory.build_post_body(sta.LOCATION_ENTITY)
LocationPatchBody = schema_factory.build_patch_body(sta.LOCATION_ENTITY)

HistoricalLocationResponse = schema_factory.build_entity_response(sta.HISTORICAL_LOCATION_ENTITY)
HistoricalLocationCollectionResponse = schema_factory.build_collection_response(sta.HISTORICAL_LOCATION_ENTITY)
HistoricalLocationPostBody = schema_factory.build_post_body(sta.HISTORICAL_LOCATION_ENTITY)
HistoricalLocationPatchBody = schema_factory.build_patch_body(sta.HISTORICAL_LOCATION_ENTITY)

DatastreamResponse = schema_factory.build_entity_response(sta.DATASTREAM_ENTITY)
DatastreamCollectionResponse = schema_factory.build_collection_response(sta.DATASTREAM_ENTITY)
DatastreamPostBody = schema_factory.build_post_body(sta.DATASTREAM_ENTITY)
DatastreamPatchBody = schema_factory.build_patch_body(sta.DATASTREAM_ENTITY)

SensorResponse = schema_factory.build_entity_response(sta.SENSOR_ENTITY)
SensorCollectionResponse = schema_factory.build_collection_response(sta.SENSOR_ENTITY)
SensorPostBody = schema_factory.build_post_body(sta.SENSOR_ENTITY)
SensorPatchBody = schema_factory.build_patch_body(sta.SENSOR_ENTITY)

ObservedPropertyResponse = schema_factory.build_entity_response(sta.OBSERVED_PROPERTY_ENTITY)
ObservedPropertyCollectionResponse = schema_factory.build_collection_response(sta.OBSERVED_PROPERTY_ENTITY)
ObservedPropertyPostBody = schema_factory.build_post_body(sta.OBSERVED_PROPERTY_ENTITY)
ObservedPropertyPatchBody = schema_factory.build_patch_body(sta.OBSERVED_PROPERTY_ENTITY)

ObservationResponse = schema_factory.build_entity_response(sta.OBSERVATION_ENTITY)
ObservationCollectionResponse = schema_factory.build_collection_response(sta.OBSERVATION_ENTITY)
ObservationPostBody = schema_factory.build_post_body(sta.OBSERVATION_ENTITY)
ObservationPatchBody = schema_factory.build_patch_body(sta.OBSERVATION_ENTITY)

FeatureOfInterestResponse = schema_factory.build_entity_response(sta.FEATURE_OF_INTEREST_ENTITY)
FeatureOfInterestCollectionResponse = schema_factory.build_collection_response(sta.FEATURE_OF_INTEREST_ENTITY)
FeatureOfInterestPostBody = schema_factory.build_post_body(sta.FEATURE_OF_INTEREST_ENTITY)
FeatureOfInterestPatchBody = schema_factory.build_patch_body(sta.FEATURE_OF_INTEREST_ENTITY)

# Build one-level excluded POST body variants for all entity set relationships.
# These prevent redundant required FK fields in deep-insert payloads (e.g.,
# ThingDatastreamPostBody omits the Thing FK so it isn't required twice).
# All are referenced by string forward refs and resolved below.
_unique_entity_types = {et.name: et for et in sta.entity_types.values()}.values()
for _entity_type in _unique_entity_types:
    for _related_set_name in _entity_type.related_entity_type_set_names:
        _related_type = sta.get_entity_type(_related_set_name)
        schema_factory.build_post_body(
            _related_type,
            exclude={_entity_type.name},
            parent_name=_entity_type.name,
        )

# Resolve all string forward references across response and POST body schemas.
_all_types = schema_factory.all_schemas()
for _schema in _all_types.values():
    _schema.model_rebuild(_types_namespace=_all_types)
