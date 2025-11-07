from typing import Union, ClassVar, TYPE_CHECKING
from ninja import Field
from sensorthings.types import Absent, ISOIntervalString, example_iso_interval_string
from sensorthings.v1_1 import iot
from sensorthings.v1_1.conf import app_settings
from .base import (
    BaseSchema,
    BaseEntitySchema,
    BaseCollectionSchema,
    IdSchema,
    PartialMetaclass,
)
from .unit_of_measurement import UnitOfMeasurement

if TYPE_CHECKING:
    from .thing import ThingResponse, ThingPostBody
    from .sensor import SensorResponse, SensorPostBody
    from .observed_property import ObservedPropertyResponse, ObservedPropertyPostBody
    from .observation import ObservationResponse, ObservationPostBody


class DatastreamFields(BaseSchema):
    """Base schema for `Datastream` entity fields."""

    name: str
    description: str
    unit_of_measurement: UnitOfMeasurement
    observation_type: app_settings.OBSERVATION_TYPE_VALUE_LITERAL
    properties: app_settings.PROPERTIES_SCHEMAS.get(iot.DATASTREAM, dict) = Absent
    observed_area: dict | None = None
    phenomenon_time: ISOIntervalString | None = Field(
        None, example=example_iso_interval_string
    )
    result_time: ISOIntervalString | None = Field(
        None, example=example_iso_interval_string
    )


class DatastreamResponse(
    DatastreamFields, BaseEntitySchema, metaclass=PartialMetaclass
):
    """GET response schema representing a `Datastream` entity."""

    _entity: ClassVar[str] = iot.DATASTREAMS
    _related_entities: ClassVar[list[str]] = [
        iot.THING,
        iot.SENSOR,
        iot.OBSERVED_PROPERTY,
        iot.OBSERVATIONS,
    ]

    thing_link: str = Field(Absent, alias=iot.THING + iot.NAVIGATION_LINK)
    thing: Union["ThingResponse", IdSchema] = Field(Absent, alias=iot.THING)

    sensor_link: str = Field(Absent, alias=iot.SENSOR + iot.NAVIGATION_LINK)
    sensor: Union["SensorResponse", IdSchema] = Field(Absent, alias=iot.SENSOR)

    observed_property_link: str = Field(
        Absent, alias=iot.OBSERVED_PROPERTY + iot.NAVIGATION_LINK
    )
    observed_property: Union["ObservedPropertyResponse", IdSchema] = Field(
        Absent, alias=iot.OBSERVED_PROPERTY
    )

    observations_link: str = Field(Absent, alias=iot.OBSERVATIONS + iot.NAVIGATION_LINK)
    observations_count: int = Field(Absent, alias=iot.OBSERVATIONS + iot.COUNT)
    observations: list["ObservationResponse"] | None = Field(
        Absent, alias=iot.OBSERVATIONS
    )
    observations_next_link: str = Field(Absent, alias=iot.OBSERVATIONS + iot.NEXT_LINK)


class DatastreamCollectionResponse(BaseCollectionSchema[DatastreamResponse]):
    """GET response schema representing a collection of `Datastream` entities."""

    _entity: ClassVar[str] = iot.DATASTREAMS


class DatastreamPostBody(DatastreamFields):
    """POST body schema for creating a new `Datastream` entity."""

    thing: Union[IdSchema, "ThingPostBody"] = Field(..., alias=iot.THING)
    sensor: Union[IdSchema, "SensorPostBody"] = Field(..., alias=iot.SENSOR)
    observed_property: Union[IdSchema, "ObservedPropertyPostBody"] = Field(
        ..., alias=iot.OBSERVED_PROPERTY
    )

    observations: list[Union[IdSchema, "ObservationPostBody"]] = Field(
        Absent, alias=iot.OBSERVATIONS
    )


class DatastreamPatchBody(DatastreamFields, metaclass=PartialMetaclass):
    """PATCH body schema for partially updating `Datastream` entities."""

    thing: IdSchema = Field(Absent, alias=iot.THING)
    sensor: IdSchema = Field(Absent, alias=iot.SENSOR)
    observed_property: IdSchema = Field(Absent, alias=iot.OBSERVED_PROPERTY)


DatastreamResponse.add_examples()
DatastreamCollectionResponse.add_examples()
DatastreamPatchBody.model_rebuild(force=True)
