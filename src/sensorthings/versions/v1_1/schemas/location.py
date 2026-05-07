from sensorthings.types import Absent
from sensorthings.versions.v1_1 import STA, app_settings
from .base import BaseSchema


class LocationFields(BaseSchema):
    """Base schema for `Location` entity fields."""

    name: str
    description: str
    encoding_type: app_settings.LOCATION_ENCODING_TYPE_VALUE_LITERAL
    location: app_settings.LOCATION_ENCODING_TYPE_SCHEMA
    properties: app_settings.PROPERTIES_SCHEMAS.get(str(STA.LOCATIONS), dict) = Absent
