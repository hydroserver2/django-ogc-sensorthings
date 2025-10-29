from typing import Union, TYPE_CHECKING
from ninja import Field, Schema
from sensorthings.types import Absent
from sensorthings.v1_1.conf import app_settings
from .base import iot, BaseSchema, BaseEntitySchema, BaseCollectionSchema, IdSchema, PartialMetaclass

if TYPE_CHECKING:
    from .location import LocationResponse, LocationPostBody
    from .historical_location import HistoricalLocationResponse, HistoricalLocationPostBody
    from .datastream import DatastreamResponse, DatastreamPostBody


class ThingFields(Schema):
    name: str
    description: str
    properties: app_settings.PROPERTIES_SCHEMAS.get("Thing", dict) | None = None


class ThingResponse(ThingFields, BaseEntitySchema, metaclass=PartialMetaclass):
    _entity = iot.THINGS
    _related_entities = [iot.LOCATIONS, iot.HISTORICAL_LOCATIONS, iot.DATASTREAMS]

    locations_link: str = Field(Absent, alias=iot.LOCATIONS + iot.NAVIGATION_LINK)
    locations_count: int = Field(Absent, alias=iot.LOCATIONS + iot.COUNT)
    locations: list["LocationResponse"] = Field(Absent, alias=iot.LOCATIONS)
    locations_next_link: str = Field(Absent, alias=iot.LOCATIONS + iot.NEXT_LINK)

    historical_locations_link: str = Field(Absent, alias=iot.HISTORICAL_LOCATIONS + iot.NAVIGATION_LINK)
    historical_locations_count: int = Field(Absent, alias=iot.HISTORICAL_LOCATIONS + iot.COUNT)
    historical_locations: list["HistoricalLocationResponse"] = Field(Absent, alias=iot.HISTORICAL_LOCATIONS)
    historical_locations_next_link: str = Field(Absent, alias=iot.HISTORICAL_LOCATIONS + iot.NEXT_LINK)

    datastreams_link: str = Field(Absent, alias=iot.DATASTREAMS + iot.NAVIGATION_LINK)
    datastreams_count: int = Field(Absent, alias=iot.DATASTREAMS + iot.COUNT)
    datastreams: list["DatastreamResponse"] = Field(Absent, alias=iot.DATASTREAMS)
    datastreams_next_link: str = Field(Absent, alias=iot.DATASTREAMS + iot.NEXT_LINK)


class ThingCollectionResponse(BaseCollectionSchema[ThingResponse]):
    _entity = iot.THINGS


class ThingPostBody(ThingFields, BaseSchema):
    locations: list[Union[IdSchema, "LocationPostBody"]] = Field(None, alias=iot.LOCATIONS)
    historical_locations: list[Union[IdSchema, "HistoricalLocationPostBody"]] = Field(
        None, alias=iot.HISTORICAL_LOCATIONS
    )
    datastreams: list[Union[IdSchema, "DatastreamPostBody"]] = Field(None, alias=iot.DATASTREAMS)


class ThingPatchBody(ThingFields, metaclass=PartialMetaclass):
    locations: list[IdSchema] = Field(Absent, alias=iot.LOCATIONS)
    historical_locations: list[IdSchema] = Field(Absent, alias=iot.HISTORICAL_LOCATIONS)
    datastreams: list[IdSchema] = Field(Absent, alias=iot.DATASTREAMS)


ThingResponse.add_examples()
ThingCollectionResponse.add_examples()
