from ninja import Field
from sensorthings.types import Absent, ISOIntervalString, example_iso_interval_string
from sensorthings.versions.v1_1 import STA, app_settings
from .base import BaseSchema
from .unit_of_measurement import UnitOfMeasurement


class DatastreamFields(BaseSchema):
    """Base schema for `Datastream` entity fields."""

    name: str
    description: str
    unit_of_measurement: UnitOfMeasurement
    observation_type: app_settings.OBSERVATION_TYPE_VALUE_LITERAL
    properties: app_settings.PROPERTIES_SCHEMAS.get(str(STA.DATASTREAMS), dict) = Absent
    observed_area: dict | None = None
    phenomenon_time: ISOIntervalString | None = Field(
        None, examples=[example_iso_interval_string]
    )
    result_time: ISOIntervalString | None = Field(
        None, examples=[example_iso_interval_string]
    )
