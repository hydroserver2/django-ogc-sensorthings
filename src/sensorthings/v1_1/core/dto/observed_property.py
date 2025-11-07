from typing import Optional, Dict
from dataclasses import dataclass
from sensorthings.v1_1.core import iot
from .base import BaseEntityDTO


@dataclass
class ObservedPropertyDTO(BaseEntityDTO):
    name: Optional[str] = None
    definition: Optional[str] = None
    description: Optional[str] = None
    properties: Optional[Dict] = None

    _entity = iot.OBSERVED_PROPERTIES
