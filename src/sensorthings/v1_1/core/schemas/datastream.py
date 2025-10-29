from typing import Optional, Dict, List, Union, TYPE_CHECKING
from ninja import Field
from sensorthings.types import ISOIntervalString, example_iso_interval_string
from sensorthings.v1_1.conf import app_settings
from .base import iot, BaseSchema, BaseEntitySchema, BaseCollectionSchema, IdSchema

if TYPE_CHECKING:
    from .thing import ThingResponse, ThingPostBody
    from .sensor import SensorResponse, SensorPostBody
    from .observed_property import ObservedPropertyResponse, ObservedPropertyPostBody
    from .observation import ObservationResponse
    from .unit_of_measurement import UnitOfMeasurement


class DatastreamFields(BaseSchema):
    name: Optional[str] = None
    description: Optional[str] = None
    unit_of_measurement: Optional["UnitOfMeasurement"] = None
    observation_type: Optional[app_settings.OBSERVATION_TYPE_VALUE_LITERAL] = None
    properties: Optional[app_settings.PROPERTIES_SCHEMAS.get("Datastream", Dict)] = None
    observed_area: Optional[Dict] = None
    phenomenon_time: Optional[ISOIntervalString] = Field(None, example=example_iso_interval_string)
    result_time: Optional[ISOIntervalString] = Field(None, example=example_iso_interval_string)


class DatastreamResponse(DatastreamFields, BaseEntitySchema):
    _entity = iot.DATASTREAMS
    _related_entities = [iot.THING, iot.SENSOR, iot.OBSERVED_PROPERTY, iot.OBSERVATIONS]

    thing_link: Optional[str] = Field(None, alias=iot.THINGS + iot.NAVIGATION_LINK)
    thing: Optional["ThingResponse"] = Field(None, alias=iot.THING)

    sensor_link: Optional[str] = Field(None, alias=iot.SENSOR + iot.NAVIGATION_LINK)
    sensor: Optional["SensorResponse"] = Field(None, alias=iot.SENSOR)

    observed_property_link: Optional[str] = Field(None, alias=iot.OBSERVED_PROPERTY + iot.NAVIGATION_LINK)
    observed_property: Optional["ObservedPropertyResponse"] = Field(None, alias=iot.OBSERVED_PROPERTY)

    observations_link: Optional[str] = Field(None, alias=iot.OBSERVATIONS + iot.NAVIGATION_LINK)
    observations_count: Optional[int] = Field(None, alias=iot.OBSERVATIONS + iot.COUNT)
    observations: Optional[List["ObservationResponse"]] = Field(None, alias=iot.OBSERVATIONS)
    observations_next_link: Optional[str] = Field(None, alias=iot.OBSERVATIONS + iot.NEXT_LINK)


class DatastreamCollectionResponse(BaseCollectionSchema[DatastreamResponse]):
    _entity = iot.DATASTREAMS


class DatastreamPostBody(DatastreamFields):
    thing: Union[IdSchema, "ThingPostBody"] = Field(..., alias=iot.THING)
    sensor: Union[IdSchema, "SensorPostBody"] = Field(..., alias=iot.SENSOR)
    observed_property: Union[IdSchema, "ObservedPropertyPostBody"] = Field(..., alias=iot.OBSERVED_PROPERTY)


class DatastreamPatchBody(DatastreamFields):
    thing: IdSchema = Field(..., alias=iot.THING)
    sensor: IdSchema = Field(..., alias=iot.SENSOR)
    observed_property: IdSchema = Field(..., alias=iot.OBSERVED_PROPERTY)


DatastreamResponse.add_examples()
DatastreamCollectionResponse.add_examples()
