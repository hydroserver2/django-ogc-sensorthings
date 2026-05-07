from sensorthings.types import Absent
from sensorthings.versions.v1_1 import STA, app_settings
from .base import BaseSchema


class SensorFields(BaseSchema):
    """Base schema for `Sensor` entity fields."""

    name: str
    description: str
    encoding_type: app_settings.SENSOR_METADATA_ENCODING_TYPE_VALUE_LITERAL
    metadata: app_settings.SENSOR_METADATA_ENCODING_TYPE_SCHEMA
    properties: app_settings.PROPERTIES_SCHEMAS.get(str(STA.SENSORS), dict) = Absent
