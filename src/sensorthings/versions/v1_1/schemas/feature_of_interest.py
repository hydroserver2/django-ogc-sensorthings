from sensorthings.types import Absent
from sensorthings.versions.v1_1 import STA, app_settings
from .base import BaseSchema


class FeatureOfInterestFields(BaseSchema):
    """Base schema for `FeatureOfInterest` entity fields."""

    name: str
    description: str
    encoding_type: app_settings.FEATURE_OF_INTEREST_ENCODING_TYPE_VALUE_LITERAL
    feature: app_settings.FEATURE_OF_INTEREST_ENCODING_TYPE_SCHEMA
    properties: app_settings.PROPERTIES_SCHEMAS.get(str(STA.FEATURES_OF_INTEREST), dict) = Absent
