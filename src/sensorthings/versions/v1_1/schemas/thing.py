from sensorthings.types import Absent
from sensorthings.versions.v1_1 import sta
from sensorthings.versions.v1_1 import app_settings
from .base import BaseSchema


class ThingFields(BaseSchema):
    """Base schema for `Thing` entity fields."""

    name: str
    description: str
    properties: app_settings.PROPERTIES_SCHEMAS.get(str(sta.THINGS), dict) = Absent
