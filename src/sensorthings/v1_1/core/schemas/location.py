from typing import Union, ClassVar, TYPE_CHECKING
from ninja import Field
from sensorthings.types import Absent
from sensorthings.v1_1 import iot
from sensorthings.v1_1.conf import app_settings
from .base import (
    BaseSchema,
    BaseEntitySchema,
    BaseCollectionSchema,
    IdSchema,
    PartialMetaclass,
)

if TYPE_CHECKING:
    from .thing import ThingResponse, ThingPostBody
    from .historical_location import (
        HistoricalLocationResponse,
        HistoricalLocationPostBody,
    )


class LocationFields(BaseSchema):
    """Base schema for `Location` entity fields."""

    name: str
    description: str
    encoding_type: app_settings.LOCATION_ENCODING_TYPE_VALUE_LITERAL
    location: app_settings.LOCATION_ENCODING_TYPE_SCHEMA
    properties: app_settings.PROPERTIES_SCHEMAS.get(iot.LOCATION, dict) = Absent


class LocationResponse(LocationFields, BaseEntitySchema, metaclass=PartialMetaclass):
    """GET response schema representing a `Location` entity."""

    _entity: ClassVar[str] = iot.LOCATIONS
    _related_entities: ClassVar[list[str]] = [iot.THINGS, iot.HISTORICAL_LOCATIONS]

    things_link: str = Field(Absent, alias=iot.THINGS + iot.NAVIGATION_LINK)
    things_count: int = Field(Absent, alias=iot.THINGS + iot.COUNT)
    things: list["ThingResponse"] = Field(Absent, alias=iot.THINGS)
    things_next_link: str = Field(Absent, alias=iot.THINGS + iot.NEXT_LINK)

    historical_locations_link: str = Field(
        Absent, alias=iot.HISTORICAL_LOCATIONS + iot.NAVIGATION_LINK
    )
    historical_locations_count: int = Field(
        Absent, alias=iot.HISTORICAL_LOCATIONS + iot.COUNT
    )
    historical_locations: list["HistoricalLocationResponse"] = Field(
        Absent, alias=iot.HISTORICAL_LOCATIONS
    )
    historical_locations_next_link: str = Field(
        Absent, alias=iot.HISTORICAL_LOCATIONS + iot.NEXT_LINK
    )


class LocationCollectionResponse(BaseCollectionSchema[LocationResponse]):
    """GET response schema representing a collection of `Location` entities."""

    _entity = iot.LOCATIONS


class LocationPostBody(LocationFields):
    """POST body schema for creating a new `Location` entity."""

    things: list[Union[IdSchema, "ThingPostBody"]] = Field(Absent, alias=iot.THINGS)
    historical_locations: list[Union[IdSchema, "HistoricalLocationPostBody"]] = Field(
        Absent, alias=iot.HISTORICAL_LOCATIONS
    )


class LocationPatchBody(LocationFields, metaclass=PartialMetaclass):
    """PATCH body schema for partially updating `Location` entities."""

    things: list[IdSchema] = Field(Absent, alias=iot.THINGS)
    historical_locations: list[IdSchema] = Field(Absent, alias=iot.HISTORICAL_LOCATIONS)


LocationResponse.add_examples()
LocationCollectionResponse.add_examples()
LocationPatchBody.model_rebuild(force=True)
