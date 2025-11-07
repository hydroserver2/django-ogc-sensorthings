from typing import Optional, List
from dataclasses import dataclass
from sensorthings.v1_1.core import iot
from sensorthings.types import ISOTimeString
from sensorthings.v1_1.conf import app_settings
from .base import BaseEntityDTO


@dataclass
class HistoricalLocationDTO(BaseEntityDTO):
    time: Optional[ISOTimeString] = None

    iot_thing_id: Optional[app_settings.ID_TYPE] = None
    iot_location_ids: Optional[List[app_settings.ID_TYPE]] = None

    _entity = iot.HISTORICAL_LOCATIONS
