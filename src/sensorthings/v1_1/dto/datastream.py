from typing import Dict
from dataclasses import dataclass
from sensorthings.types import Absent
from sensorthings.types import ISOIntervalString
from sensorthings.v1_1.conf import app_settings
from .base import BaseEntityDTO


@dataclass
class DatastreamDTO(BaseEntityDTO):
    name: str = Absent
    description: str = Absent
    unit_of_measurement: dict = Absent
    observation_type: app_settings.OBSERVATION_TYPE_VALUE_LITERAL = Absent
    properties: app_settings.PROPERTIES_SCHEMAS.get("Datastream", Dict) = Absent
    observed_area: Dict = Absent
    phenomenon_time: ISOIntervalString = Absent
    result_time: ISOIntervalString = Absent
