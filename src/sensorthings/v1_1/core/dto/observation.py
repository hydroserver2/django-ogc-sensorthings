from typing import Dict, Union, Optional
from dataclasses import dataclass
from sensorthings.v1_1.core import iot
from sensorthings.types import ISOTimeString, ISOIntervalString
from sensorthings.v1_1.conf import app_settings
from .base import BaseEntityDTO


@dataclass
class ObservationDTO(BaseEntityDTO):
    phenomenon_time: Optional[Union[ISOTimeString, ISOIntervalString]] = None
    result: Optional[app_settings.OBSERVATION_TYPE_SCHEMA] = None
    result_time: Optional[ISOTimeString] = None
    result_quality: Optional[Dict] = None
    valid_time: Optional[ISOIntervalString] = None
    parameters: Optional[Dict] = None

    iot_datastream_id: Optional[app_settings.ID_TYPE] = None
    iot_feature_of_interest_id: Optional[app_settings.ID_TYPE] = None

    _entity = iot.OBSERVATIONS
    _related_entities = [iot.DATASTREAM, iot.FEATURE_OF_INTEREST]
