from dataclasses import dataclass
from sensorthings.types import Absent
from sensorthings.types import ISOTimeString
from sensorthings.versions.v1_1 import app_settings
from .base import BaseEntityDTO


@dataclass
class HistoricalLocationDTO(BaseEntityDTO):
    time: ISOTimeString = Absent

    thing_id: app_settings.ID_TYPE = Absent
