from typing import Dict
from dataclasses import dataclass
from sensorthings.types import Absent
from sensorthings.v1_1.conf import app_settings
from .base import BaseEntityDTO


@dataclass
class SensorDTO(BaseEntityDTO):
    name: str = Absent
    description: str = Absent
    encoding_type: app_settings.SENSOR_METADATA_ENCODING_TYPE_VALUE_LITERAL = Absent
    metadata: app_settings.SENSOR_METADATA_ENCODING_TYPE_SCHEMA = Absent
    properties: app_settings.PROPERTIES_SCHEMAS.get("Sensor", Dict) = Absent
