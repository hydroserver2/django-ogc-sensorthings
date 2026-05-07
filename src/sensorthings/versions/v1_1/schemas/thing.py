from sensorthings.types import Absent
from sensorthings.versions.v1_1 import STA, app_settings
from .base import BaseSchema


class ThingFields(BaseSchema):
    """Base schema for `Thing` entity fields."""

    name: str
    description: str
    properties: app_settings.PROPERTIES_SCHEMAS.get(str(STA.THINGS), dict) = Absent
