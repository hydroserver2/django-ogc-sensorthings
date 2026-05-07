from typing import Dict
from dataclasses import dataclass
from sensorthings.types import Absent
from sensorthings.versions.v1_1 import app_settings
from .base import BaseEntityDTO


@dataclass
class LocationDTO(BaseEntityDTO):
    name: str = Absent
    description: str = Absent
    encoding_type: app_settings.LOCATION_ENCODING_TYPE_VALUE_LITERAL = Absent
    location: app_settings.LOCATION_ENCODING_TYPE_SCHEMA = Absent
    properties: app_settings.PROPERTIES_SCHEMAS.get("Locations", Dict) = Absent

    thing_ids: list = Absent
