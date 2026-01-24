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


class ObservedPropertyFields(BaseSchema):
    """Base schema for `ObservedProperty` entity fields."""

    name: str
    definition: str
    description: str
    properties: app_settings.PROPERTIES_SCHEMAS.get(str(sta.OBSERVED_PROPERTIES), dict) = (
        Absent
    )


ObservedPropertyResponse = build_sta_entity_response_schema(sta.OBSERVED_PROPERTY_ENTITY, ObservedPropertyFields)
ObservedPropertyCollectionResponse = build_sta_collection_response_schema(
    sta.OBSERVED_PROPERTY_ENTITY, ObservedPropertyResponse
)
ObservedPropertyPostBody = build_sta_post_body_schema(sta.OBSERVED_PROPERTY_ENTITY, ObservedPropertyFields)
ObservedPropertyPatchBody = build_sta_patch_body_schema(sta.OBSERVED_PROPERTY_ENTITY, ObservedPropertyFields)

ObservedPropertyPatchBody.model_rebuild(force=True)
