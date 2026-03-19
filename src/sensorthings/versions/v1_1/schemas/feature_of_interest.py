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


class FeatureOfInterestFields(BaseSchema):
    """Base schema for `FeatureOfInterest` entity fields."""

    name: str
    description: str
    encoding_type: app_settings.FEATURE_OF_INTEREST_ENCODING_TYPE_VALUE_LITERAL
    feature: app_settings.FEATURE_OF_INTEREST_ENCODING_TYPE_SCHEMA
    properties: app_settings.PROPERTIES_SCHEMAS.get(str(sta.FEATURES_OF_INTEREST), dict) = (
        Absent
    )


FeatureOfInterestResponse = build_sta_entity_response_schema(sta.FEATURE_OF_INTEREST_ENTITY, FeatureOfInterestFields)
FeatureOfInterestCollectionResponse = build_sta_collection_response_schema(
    sta.FEATURE_OF_INTEREST_ENTITY, FeatureOfInterestResponse
)
FeatureOfInterestPostBody = build_sta_post_body_schema(sta.FEATURE_OF_INTEREST_ENTITY, FeatureOfInterestFields)
FeatureOfInterestPatchBody = build_sta_patch_body_schema(sta.FEATURE_OF_INTEREST_ENTITY, FeatureOfInterestFields)

FeatureOfInterestPatchBody.model_rebuild(force=True)
