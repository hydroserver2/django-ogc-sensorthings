from typing import Optional, Dict
from dataclasses import dataclass
from sensorthings.v1_1.core import iot
from sensorthings.v1_1.conf import app_settings
from .base import BaseEntityDTO


@dataclass
class SensorDTO(BaseEntityDTO):
    name: Optional[str] = None
    description: Optional[str] = None
    encoding_type: Optional[app_settings.SENSOR_METADATA_ENCODING_TYPE_VALUE_LITERAL] = None
    metadata: Optional[app_settings.SENSOR_METADATA_ENCODING_TYPE_SCHEMA] = None
    properties: Optional[Dict] = None

    _entity = iot.SENSORS
    _related_entities = [iot.DATASTREAMS]
