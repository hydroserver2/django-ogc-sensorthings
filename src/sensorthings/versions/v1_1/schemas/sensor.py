from sensorthings.types import Absent
from sensorthings.versions.v1_1 import sta
from sensorthings.versions.v1_1 import app_settings
from .base import BaseSchema
from .factory import (
    build_sta_entity_response_schema,
    build_sta_collection_response_schema,
    build_sta_post_body_schema,
    build_sta_patch_body_schema
)


class SensorFields(BaseSchema):
    """Base schema for `Sensor` entity fields."""

    name: str
    description: str
    encoding_type: app_settings.SENSOR_METADATA_ENCODING_TYPE_VALUE_LITERAL
    metadata: app_settings.SENSOR_METADATA_ENCODING_TYPE_SCHEMA
    properties: app_settings.PROPERTIES_SCHEMAS.get(str(sta.SENSORS), dict) = Absent


SensorResponse = build_sta_entity_response_schema(sta.SENSOR_ENTITY, SensorFields)
SensorCollectionResponse = build_sta_collection_response_schema(sta.SENSOR_ENTITY, SensorResponse)
SensorPostBody = build_sta_post_body_schema(sta.SENSOR_ENTITY, SensorFields)
SensorPatchBody = build_sta_patch_body_schema(sta.SENSOR_ENTITY, SensorFields)

SensorPatchBody.model_rebuild(force=True)
