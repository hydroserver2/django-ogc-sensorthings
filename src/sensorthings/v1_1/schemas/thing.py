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


class ThingFields(BaseSchema):
    """Base schema for `Thing` entity fields."""

    name: str
    description: str
    properties: app_settings.PROPERTIES_SCHEMAS.get(str(sta.THINGS), dict) = Absent


ThingResponse = build_sta_entity_response_schema(sta.THING_ENTITY, ThingFields)
ThingCollectionResponse = build_sta_collection_response_schema(sta.THING_ENTITY, ThingResponse)
ThingPostBody = build_sta_post_body_schema(sta.THING_ENTITY, ThingFields)
ThingPatchBody = build_sta_patch_body_schema(sta.THING_ENTITY, ThingFields)

ThingPatchBody.model_rebuild(force=True)
