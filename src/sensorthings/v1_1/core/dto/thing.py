from dataclasses import dataclass
from sensorthings.types import Absent
from sensorthings.v1_1.core import iot
from .base import BaseEntityDTO


@dataclass
class ThingDTO(BaseEntityDTO):
    name: str = Absent
    description: str = Absent
    properties: dict = Absent

    _entity = iot.THINGS
