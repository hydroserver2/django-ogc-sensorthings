from typing import Union
from ninja import Field
from sensorthings.types import (
    Absent,
    ISOTimeString,
    ISOIntervalString,
    example_iso_time_string,
    example_iso_interval_string,
)
from sensorthings.versions.v1_1 import STA, app_settings
from .base import BaseSchema


class ObservationFields(BaseSchema):
    """Base schema for `Observation` entity fields."""

    phenomenon_time: Union[ISOTimeString, ISOIntervalString] = Field(
        ..., examples=[example_iso_time_string, example_iso_interval_string]
    )
    result: app_settings.OBSERVATION_TYPE_SCHEMA
    result_time: ISOTimeString = Field(..., examples=[example_iso_time_string])
    result_quality: dict | None = None
    valid_time: ISOIntervalString | None = Field(
        None, examples=[example_iso_interval_string]
    )
    parameters: app_settings.PROPERTIES_SCHEMAS.get(str(STA.OBSERVATIONS), dict) = Absent
