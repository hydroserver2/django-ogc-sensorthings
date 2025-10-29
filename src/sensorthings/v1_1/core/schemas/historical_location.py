from typing import Optional, List, Union, TYPE_CHECKING
from ninja import Field
from sensorthings.types import ISOTimeString, example_iso_time_string
from .base import iot, BaseSchema, BaseEntitySchema, BaseCollectionSchema, IdSchema

if TYPE_CHECKING:
    from .thing import ThingResponse, ThingPostBody
    from .location import LocationResponse, LocationPostBody


class HistoricalLocationFields(BaseSchema):
    time: ISOTimeString = Field(..., example=example_iso_time_string)


class HistoricalLocationResponse(HistoricalLocationFields, BaseEntitySchema):
    _entity = iot.HISTORICAL_LOCATIONS
    _related_entities = [iot.THING, iot.LOCATIONS]

    thing_link: Optional[str] = Field(None, alias=iot.THING + iot.NAVIGATION_LINK)
    thing: Optional["ThingResponse"] = Field(None, alias=iot.THING)

    locations_link: Optional[str] = Field(None, alias=iot.LOCATIONS + iot.NAVIGATION_LINK)
    locations_count: Optional[int] = Field(None, alias=iot.LOCATIONS + iot.COUNT)
    locations: Optional[List["LocationResponse"]] = Field(None, alias=iot.LOCATIONS)
    locations_next_link: Optional[str] = Field(None, alias=iot.LOCATIONS + iot.NEXT_LINK)


class HistoricalLocationCollectionResponse(BaseCollectionSchema[HistoricalLocationResponse]):
    _entity = iot.HISTORICAL_LOCATIONS


class HistoricalLocationPostBody(HistoricalLocationFields):
    thing: Union[IdSchema, "ThingPostBody"] = Field(..., alias=iot.THING)
    locations: List[Union[IdSchema, "LocationPostBody"]] = Field(None, alias=iot.LOCATIONS)


class HistoricalLocationPatchBody(HistoricalLocationFields):
    thing: IdSchema = Field(..., alias=iot.THING)
    locations: List[IdSchema] = Field(None, alias=iot.LOCATIONS)


HistoricalLocationResponse.add_examples()
HistoricalLocationCollectionResponse.add_examples()
