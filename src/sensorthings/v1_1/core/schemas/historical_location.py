from typing import Union, ClassVar, TYPE_CHECKING
from ninja import Field
from sensorthings.types import Absent, ISOTimeString, example_iso_time_string
from sensorthings.v1_1 import iot
from .base import (
    BaseSchema,
    BaseEntitySchema,
    BaseCollectionSchema,
    IdSchema,
    PartialMetaclass,
)

if TYPE_CHECKING:
    from .thing import ThingResponse, ThingPostBody
    from .location import LocationResponse, LocationPostBody


class HistoricalLocationFields(BaseSchema):
    """Base schema for `HistoricalLocation` entity fields."""

    time: ISOTimeString = Field(..., example=example_iso_time_string)


class HistoricalLocationResponse(
    HistoricalLocationFields, BaseEntitySchema, metaclass=PartialMetaclass
):
    """GET response schema representing a `HistoricalLocation` entity."""

    _entity: ClassVar[str] = iot.HISTORICAL_LOCATIONS
    _related_entities: ClassVar[list[str]] = [iot.THING, iot.LOCATIONS]

    thing_link: str = Field(Absent, alias=iot.THING + iot.NAVIGATION_LINK)
    thing: Union["ThingResponse", IdSchema] = Field(Absent, alias=iot.THING)

    locations_link: str = Field(Absent, alias=iot.LOCATIONS + iot.NAVIGATION_LINK)
    locations_count: int = Field(Absent, alias=iot.LOCATIONS + iot.COUNT)
    locations: list["LocationResponse"] = Field(Absent, alias=iot.LOCATIONS)
    locations_next_link: str = Field(Absent, alias=iot.LOCATIONS + iot.NEXT_LINK)


class HistoricalLocationCollectionResponse(
    BaseCollectionSchema[HistoricalLocationResponse]
):
    """GET response schema representing a collection of `HistoricalLocation` entities."""

    _entity = iot.HISTORICAL_LOCATIONS


class HistoricalLocationPostBody(HistoricalLocationFields):
    """POST body schema for creating a new `HistoricalLocation` entity."""

    thing: Union[IdSchema, "ThingPostBody"] = Field(..., alias=iot.THING)
    locations: list[Union[IdSchema, "LocationPostBody"]] = Field(
        Absent, alias=iot.LOCATIONS
    )


class HistoricalLocationPatchBody(HistoricalLocationFields, metaclass=PartialMetaclass):
    """PATCH body schema for partially updating `HistoricalLocation` entities."""

    thing: IdSchema = Field(Absent, alias=iot.THING)
    locations: list[IdSchema] = Field(Absent, alias=iot.LOCATIONS)


HistoricalLocationResponse.add_examples()
HistoricalLocationCollectionResponse.add_examples()
HistoricalLocationPatchBody.model_rebuild(force=True)
