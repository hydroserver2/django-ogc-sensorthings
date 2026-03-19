from typing import Dict, Union
from dataclasses import dataclass
from sensorthings.types import Absent
from sensorthings.types import ISOTimeString, ISOIntervalString
from sensorthings.versions.v1_1 import app_settings
from .base import BaseEntityDTO


@dataclass
class ObservationDTO(BaseEntityDTO):
    phenomenon_time: Union[ISOTimeString, ISOIntervalString] = Absent
    result: app_settings.OBSERVATION_TYPE_SCHEMA = Absent
    result_time: ISOTimeString = Absent
    result_quality: dict = Absent
    valid_time: ISOIntervalString = Absent
    parameters: app_settings.PROPERTIES_SCHEMAS.get("Observation", Dict) = Absent

    datastream_id: app_settings.ID_TYPE = Absent
    feature_of_interest_id: app_settings.ID_TYPE = Absent
