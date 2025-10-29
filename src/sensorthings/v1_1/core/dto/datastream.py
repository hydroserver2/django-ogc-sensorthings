from typing import Dict, Optional
from dataclasses import dataclass
from sensorthings.v1_1.core import iot
from sensorthings.types import ISOIntervalString
from sensorthings.v1_1.conf import app_settings
from .base import BaseEntityDTO


@dataclass
class DatastreamDTO(BaseEntityDTO):
    name: Optional[str] = None
    description: Optional[str] = None
    unit_of_measurement: Optional[Dict] = None
    observation_type: Optional[app_settings.OBSERVATION_TYPE_VALUE_LITERAL] = None
    properties: Optional[app_settings.PROPERTIES_SCHEMAS.get("Datastream", Dict)] = None
    observed_area: Optional[Dict] = None
    phenomenon_time: Optional[ISOIntervalString] = None
    result_time: Optional[ISOIntervalString] = None

    iot_thing_id: Optional[app_settings.ID_TYPE] = None
    iot_observed_property_id: Optional[app_settings.ID_TYPE] = None
    iot_sensor_id: Optional[app_settings.ID_TYPE] = None

    _entity = iot.DATASTREAMS
    _related_entities = [iot.THING, iot.OBSERVED_PROPERTY, iot.SENSOR, iot.OBSERVATIONS]
