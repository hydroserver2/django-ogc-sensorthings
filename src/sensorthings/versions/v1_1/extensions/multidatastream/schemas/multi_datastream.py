from ninja import Field
from sensorthings.types import Absent, ISOIntervalString, example_iso_interval_string
from sensorthings.versions.v1_1 import STA
from sensorthings.versions.v1_1 import app_settings
from sensorthings.versions.v1_1.schemas.base import BaseSchema
from sensorthings.versions.v1_1.schemas.unit_of_measurement import UnitOfMeasurement


class MultiDatastreamFields(BaseSchema):
    """Base schema for `MultiDatastream` entity fields."""

    name: str
    description: str
    unit_of_measurements: list[UnitOfMeasurement]
    observation_type: app_settings.OBSERVATION_TYPE_VALUE_LITERAL
    observed_area: dict | None = None
    phenomenon_time: ISOIntervalString | None = Field(
        None, examples=[example_iso_interval_string]
    )
    result_time: ISOIntervalString | None = Field(
        None, examples=[example_iso_interval_string]
    )
    multi_observation_data_types: list
    properties: app_settings.PROPERTIES_SCHEMAS.get("MultiDatastreams", dict) = Absent
