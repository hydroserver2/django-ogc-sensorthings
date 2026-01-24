from sensorthings.types import Absent
from sensorthings.v1_1.protocol import sta
from sensorthings.v1_1.conf import app_settings
from .base import BaseSchema
from .factory import (
    build_sta_entity_response_schema,
    build_sta_collection_response_schema,
    build_sta_post_body_schema,
    build_sta_patch_body_schema
)


class LocationFields(BaseSchema):
    """Base schema for `Location` entity fields."""

    name: str
    description: str
    encoding_type: app_settings.LOCATION_ENCODING_TYPE_VALUE_LITERAL
    location: app_settings.LOCATION_ENCODING_TYPE_SCHEMA
    properties: app_settings.PROPERTIES_SCHEMAS.get(str(sta.LOCATIONS), dict) = Absent


LocationResponse = build_sta_entity_response_schema(sta.LOCATION_ENTITY, LocationFields)
LocationCollectionResponse = build_sta_collection_response_schema(sta.LOCATION_ENTITY, LocationResponse)
LocationPostBody = build_sta_post_body_schema(sta.LOCATION_ENTITY, LocationFields)
LocationPatchBody = build_sta_patch_body_schema(sta.LOCATION_ENTITY, LocationFields)

LocationPatchBody.model_rebuild(force=True)
