from typing import Optional, Dict, List, Union, TYPE_CHECKING
from ninja import Field
from sensorthings.v1_1.conf import app_settings
from .base import iot, BaseSchema, BaseEntitySchema, BaseCollectionSchema, IdSchema

if TYPE_CHECKING:
    from .thing import ThingResponse, ThingPostBody
    from .historical_location import HistoricalLocationResponse, HistoricalLocationPostBody


class LocationFields(BaseSchema):
    name: str
    description: str
    encoding_type: app_settings.LOCATION_ENCODING_TYPE_VALUE_LITERAL
    location: app_settings.LOCATION_ENCODING_TYPE_SCHEMA
    properties: Optional[app_settings.PROPERTIES_SCHEMAS.get("Location", Dict)] = None


class LocationResponse(LocationFields, BaseEntitySchema):
    _entity = iot.LOCATIONS
    _related_entities = [iot.THINGS, iot.HISTORICAL_LOCATIONS]

    things_link: Optional[str] = Field(None, alias=iot.THINGS + iot.NAVIGATION_LINK)
    things_count: Optional[int] = Field(None, alias=iot.THINGS + iot.COUNT)
    things: Optional[List["ThingResponse"]] = Field(None, alias=iot.THINGS)
    things_next_link: Optional[str] = Field(None, alias=iot.THINGS + iot.NEXT_LINK)

    historical_locations_link: Optional[str] = Field(None, alias=iot.HISTORICAL_LOCATIONS + iot.NAVIGATION_LINK)
    historical_locations_count: Optional[int] = Field(None, alias=iot.HISTORICAL_LOCATIONS + iot.COUNT)
    historical_locations: Optional[List["HistoricalLocationResponse"]] = Field(None, alias=iot.HISTORICAL_LOCATIONS)
    historical_locations_next_link: Optional[str] = Field(None, alias=iot.HISTORICAL_LOCATIONS + iot.NEXT_LINK)


class LocationCollectionResponse(BaseCollectionSchema[LocationResponse]):
    _entity = iot.LOCATIONS


class LocationPostBody(LocationFields):
    things: List[Union[IdSchema, "ThingPostBody"]] = Field(None, alias=iot.THINGS)
    historical_locations: List[Union[IdSchema, "HistoricalLocationPostBody"]] = Field(
        None, alias=iot.HISTORICAL_LOCATIONS
    )


class LocationPatchBody(LocationFields):
    things: List[IdSchema] = Field(None, alias=iot.THINGS)
    historical_locations: List[IdSchema] = Field(None, alias=iot.HISTORICAL_LOCATIONS)


LocationResponse.add_examples()
LocationCollectionResponse.add_examples()
