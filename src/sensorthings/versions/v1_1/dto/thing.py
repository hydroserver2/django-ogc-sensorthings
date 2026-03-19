from typing import Dict
from dataclasses import dataclass
from sensorthings.types import Absent
from sensorthings.versions.v1_1 import app_settings
from .base import BaseEntityDTO


@dataclass
class ThingDTO(BaseEntityDTO):
    name: str = Absent
    description: str = Absent
    properties: app_settings.PROPERTIES_SCHEMAS.get("Sensor", Dict) = Absent
