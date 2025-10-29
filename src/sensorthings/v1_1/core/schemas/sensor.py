from typing import Optional, Dict, List, Union, TYPE_CHECKING
from ninja import Field
from sensorthings.v1_1.conf import app_settings
from .base import iot, BaseSchema, BaseEntitySchema, BaseCollectionSchema, IdSchema

if TYPE_CHECKING:
    from .datastream import DatastreamResponse, DatastreamPostBody


class SensorFields(BaseSchema):
    name: str
    description: str
    encoding_type: app_settings.SENSOR_METADATA_ENCODING_TYPE_VALUE_LITERAL
    metadata: app_settings.SENSOR_METADATA_ENCODING_TYPE_SCHEMA
    properties: Optional[app_settings.PROPERTIES_SCHEMAS.get("Sensor", Dict)] = None


class SensorResponse(SensorFields, BaseEntitySchema):
    _entity = iot.SENSORS
    _related_entities = [iot.DATASTREAMS]

    datastreams_link: Optional[str] = Field(None, alias=iot.DATASTREAMS + iot.NAVIGATION_LINK)
    datastreams_count: Optional[int] = Field(None, alias=iot.DATASTREAMS + iot.COUNT)
    datastreams: Optional[List["DatastreamResponse"]] = Field(None, alias=iot.DATASTREAMS)
    datastreams_next_link: Optional[str] = Field(None, alias=iot.DATASTREAMS + iot.NEXT_LINK)


class SensorCollectionResponse(BaseCollectionSchema[SensorResponse]):
    _entity = iot.SENSORS


class SensorPostBody(SensorFields):
    datastreams: List[Union[IdSchema, "DatastreamPostBody"]] = Field(None, alias=iot.DATASTREAMS)


class SensorPatchBody(SensorFields):
    datastreams: List[IdSchema] = Field(None, alias=iot.DATASTREAMS)


SensorResponse.add_examples()
SensorCollectionResponse.add_examples()
