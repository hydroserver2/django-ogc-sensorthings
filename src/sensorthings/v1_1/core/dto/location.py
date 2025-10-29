from typing import Optional, Dict, List
from dataclasses import dataclass
from sensorthings.v1_1.core import iot
from sensorthings.v1_1.conf import app_settings
from .base import BaseEntityDTO


@dataclass
class LocationDTO(BaseEntityDTO):
    name: Optional[str] = None
    description: Optional[str] = None
    encoding_type: Optional[app_settings.LOCATION_ENCODING_TYPE_VALUE_LITERAL] = None
    location: Optional[app_settings.LOCATION_ENCODING_TYPE_SCHEMA] = None
    properties: Optional[app_settings.PROPERTIES_SCHEMAS.get("Location", Dict)] = None

    iot_thing_ids: Optional[List[app_settings.ID_TYPE]] = None
    iot_historical_location_ids: Optional[List[app_settings.ID_TYPE]] = None

    _entity = iot.LOCATIONS
    _related_entities = [iot.THINGS, iot.HISTORICAL_LOCATIONS]
