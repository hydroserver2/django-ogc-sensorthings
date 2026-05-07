from ninja import Field
from sensorthings.types import ISOTimeString, example_iso_time_string
from .base import BaseSchema


class HistoricalLocationFields(BaseSchema):
    """Base schema for `HistoricalLocation` entity fields."""

    time: ISOTimeString = Field(..., examples=[example_iso_time_string])
