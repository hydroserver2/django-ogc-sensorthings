from typing import Optional, Dict, List, Union, TYPE_CHECKING
from ninja import Field
from sensorthings.v1_1.core import iot
from sensorthings.v1_1.conf import app_settings
from .base import BaseSchema, BaseEntitySchema, BaseCollectionSchema, IdSchema

if TYPE_CHECKING:
    from .datastream import DatastreamResponse, DatastreamPostBody


class ObservedPropertyFields(BaseSchema):
    name: str
    definition: str
    description: str
    properties: Optional[app_settings.PROPERTIES_SCHEMAS.get("ObservedProperty", Dict)] = None


class ObservedPropertyResponse(ObservedPropertyFields, BaseEntitySchema):
    _entity = iot.OBSERVED_PROPERTIES
    _related_entities = [iot.DATASTREAMS]

    datastreams_link: Optional[str] = Field(None, alias=iot.DATASTREAMS + iot.NAVIGATION_LINK)
    datastreams_count: Optional[int] = Field(None, alias=iot.DATASTREAMS + iot.COUNT)
    datastreams: Optional[List["DatastreamResponse"]] = Field(None, alias=iot.DATASTREAMS)
    datastreams_next_link: Optional[str] = Field(None, alias=iot.DATASTREAMS + iot.NEXT_LINK)


class ObservedPropertyCollectionResponse(BaseCollectionSchema[ObservedPropertyResponse]):
    _entity = iot.OBSERVED_PROPERTIES


class ObservedPropertyPostBody(ObservedPropertyFields):
    datastreams: List[Union[IdSchema, "DatastreamPostBody"]] = Field(None, alias=iot.DATASTREAMS)


class ObservedPropertyPatchBody(ObservedPropertyFields):
    datastreams: List[IdSchema] = Field(None, alias=iot.DATASTREAMS)


ObservedPropertyResponse.add_examples()
ObservedPropertyCollectionResponse.add_examples()
