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
    from .datastream import DatastreamResponse, DatastreamPostBody


class ObservedPropertyFields(BaseSchema):
    """Base schema for `ObservedProperty` entity fields."""

    name: str
    definition: str
    description: str
    properties: app_settings.PROPERTIES_SCHEMAS.get(iot.OBSERVED_PROPERTY, dict) = (
        Absent
    )


class ObservedPropertyResponse(
    ObservedPropertyFields, BaseEntitySchema, metaclass=PartialMetaclass
):
    """GET response schema representing a `ObservedProperty` entity."""

    _entity: ClassVar[str] = iot.OBSERVED_PROPERTIES
    _related_entities: ClassVar[list[str]] = [iot.DATASTREAMS]

    datastreams_link: str = Field(Absent, alias=iot.DATASTREAMS + iot.NAVIGATION_LINK)
    datastreams_count: int = Field(Absent, alias=iot.DATASTREAMS + iot.COUNT)
    datastreams: list["DatastreamResponse"] = Field(Absent, alias=iot.DATASTREAMS)
    datastreams_next_link: str = Field(Absent, alias=iot.DATASTREAMS + iot.NEXT_LINK)


class ObservedPropertyCollectionResponse(
    BaseCollectionSchema[ObservedPropertyResponse]
):
    """GET response schema representing a collection of `ObservedProperty` entities."""

    _entity: ClassVar[str] = iot.OBSERVED_PROPERTIES


class ObservedPropertyPostBody(ObservedPropertyFields):
    """POST body schema for creating a new `ObservedProperty` entity."""

    datastreams: list[Union[IdSchema, "DatastreamPostBody"]] = Field(
        Absent, alias=iot.DATASTREAMS
    )


class ObservedPropertyPatchBody(ObservedPropertyFields, metaclass=PartialMetaclass):
    """PATCH body schema for partially updating `ObservedProperty` entities."""

    datastreams: list[IdSchema] = Field(Absent, alias=iot.DATASTREAMS)


ObservedPropertyResponse.add_examples()
ObservedPropertyCollectionResponse.add_examples()
ObservedPropertyPatchBody.model_rebuild(force=True)
