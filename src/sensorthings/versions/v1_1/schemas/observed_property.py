from sensorthings.types import Absent
from sensorthings.versions.v1_1 import sta
from sensorthings.versions.v1_1 import app_settings
from .base import BaseSchema


class ObservedPropertyFields(BaseSchema):
    """Base schema for `ObservedProperty` entity fields."""

    name: str
    definition: str
    description: str
    properties: app_settings.PROPERTIES_SCHEMAS.get(str(sta.OBSERVED_PROPERTIES), dict) = Absent
