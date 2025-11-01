from typing import Union, TYPE_CHECKING, ClassVar
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
    from .datastream import DatastreamResponse, DatastreamPostBody


class SensorFields(BaseSchema):
    """Base schema for `Sensor` entity fields."""

    name: str
    description: str
    encoding_type: app_settings.SENSOR_METADATA_ENCODING_TYPE_VALUE_LITERAL
    metadata: app_settings.SENSOR_METADATA_ENCODING_TYPE_SCHEMA
    properties: app_settings.PROPERTIES_SCHEMAS.get(iot.SENSOR, dict) = Absent


class SensorResponse(SensorFields, BaseEntitySchema, metaclass=PartialMetaclass):
    """GET response schema representing a `Sensor` entity."""

    _entity: ClassVar[str] = iot.SENSORS
    _related_entities: ClassVar[list[str]] = [iot.DATASTREAMS]

    datastreams_link: str = Field(Absent, alias=iot.DATASTREAMS + iot.NAVIGATION_LINK)
    datastreams_count: int = Field(Absent, alias=iot.DATASTREAMS + iot.COUNT)
    datastreams: list["DatastreamResponse"] = Field(Absent, alias=iot.DATASTREAMS)
    datastreams_next_link: str = Field(Absent, alias=iot.DATASTREAMS + iot.NEXT_LINK)


class SensorCollectionResponse(BaseCollectionSchema[SensorResponse]):
    """GET response schema representing a collection of `Sensor` entities."""

    _entity: ClassVar[str] = iot.SENSORS


class SensorPostBody(SensorFields):
    """POST body schema for creating a new `Sensor` entity."""

    datastreams: list[Union[IdSchema, "DatastreamPostBody"]] = Field(
        Absent, alias=iot.DATASTREAMS
    )


class SensorPatchBody(SensorFields, metaclass=PartialMetaclass):
    """PATCH body schema for partially updating `Sensor` entities, including updating related entity links."""

    datastreams: list[IdSchema] = Field(Absent, alias=iot.DATASTREAMS)


SensorResponse.add_examples()
SensorCollectionResponse.add_examples()
SensorPatchBody.model_rebuild(force=True)
