from typing import Optional, Dict, List
from dataclasses import dataclass
from sensorthings.v1_1.core import iot
from sensorthings.v1_1.conf import app_settings
from .base import BaseEntityDTO


@dataclass
class ThingDTO(BaseEntityDTO):
    name: str = None
    description: Optional[str] = None
    properties: Optional[Dict] = None

    iot_location_ids: Optional[List[app_settings.ID_TYPE]] = None

    _entity = iot.THINGS
    _related_entities = [iot.LOCATIONS, iot.HISTORICAL_LOCATIONS, iot.DATASTREAMS]
