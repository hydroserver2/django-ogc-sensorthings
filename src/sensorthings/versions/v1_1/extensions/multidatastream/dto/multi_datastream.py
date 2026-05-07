from dataclasses import dataclass
from sensorthings.types import Absent
from sensorthings.versions.v1_1.conf import app_settings
from sensorthings.versions.v1_1.dto.base import BaseEntityDTO


@dataclass
class MultiDatastreamDTO(BaseEntityDTO):
    name: str | type[Absent] = Absent
    description: str | type[Absent] = Absent
    unit_of_measurements: list | type[Absent] = Absent
    observation_type: str | type[Absent] = Absent
    multi_observation_data_types: list | type[Absent] = Absent
    observed_area: dict | type[Absent] = Absent
    phenomenon_time: str | type[Absent] = Absent
    result_time: str | type[Absent] = Absent
    properties: dict | type[Absent] = Absent
    thing_id: app_settings.ID_TYPE | None = None
    sensor_id: app_settings.ID_TYPE | None = None
    observed_property_id: app_settings.ID_TYPE | None = None
