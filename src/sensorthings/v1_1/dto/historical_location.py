from dataclasses import dataclass
from sensorthings.types import Absent
from sensorthings.types import ISOTimeString
from .base import BaseEntityDTO


@dataclass
class HistoricalLocationDTO(BaseEntityDTO):
    time: ISOTimeString = Absent
