from typing import Union, ClassVar, TYPE_CHECKING
from ninja import Field
from sensorthings.types import (
    Absent,
    ISOTimeString,
    ISOIntervalString,
    example_iso_time_string,
    example_iso_interval_string,
)
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
    from .feature_of_interest import (
        FeatureOfInterestResponse,
        FeatureOfInterestPostBody,
    )


class ObservationFields(BaseSchema):
    """Base schema for `Observation` entity fields."""

    phenomenon_time: Union[ISOTimeString, ISOIntervalString] = Field(
        ..., examples=[example_iso_time_string, example_iso_interval_string]
    )
    result: app_settings.OBSERVATION_TYPE_SCHEMA
    result_time: ISOTimeString = Field(..., example=example_iso_time_string)
    result_quality: dict | None = None
    valid_time: ISOIntervalString | None = Field(
        None, example=example_iso_interval_string
    )
    parameters: dict = Absent


class ObservationResponse(
    ObservationFields, BaseEntitySchema, metaclass=PartialMetaclass
):
    """GET response schema representing a `Observation` entity."""

    _entity = iot.OBSERVATIONS
    _related_entities = [iot.DATASTREAM, iot.FEATURE_OF_INTEREST]

    datastream_link: str = Field(Absent, alias=iot.DATASTREAM + iot.NAVIGATION_LINK)
    datastream: Union["DatastreamResponse", IdSchema] = Field(
        Absent, alias=iot.DATASTREAM
    )

    feature_of_interest_link: str = Field(
        Absent, alias=iot.FEATURE_OF_INTEREST + iot.NAVIGATION_LINK
    )
    feature_of_interest: Union["FeatureOfInterestResponse", IdSchema] = Field(
        Absent, alias=iot.FEATURE_OF_INTEREST
    )


class ObservationCollectionResponse(BaseCollectionSchema[ObservationResponse]):
    """GET response schema representing a collection of `Observation` entities."""

    _entity: ClassVar[str] = iot.OBSERVATIONS


class ObservationPostBody(ObservationFields):
    """POST body schema for creating a new `Observation` entity."""

    datastream: Union[IdSchema, "DatastreamPostBody"] = Field(..., alias=iot.DATASTREAM)
    feature_of_interest: Union[IdSchema, "FeatureOfInterestPostBody", None] = Field(
        None, alias=iot.FEATURE_OF_INTEREST
    )


class ObservationPatchBody(ObservationFields, metaclass=PartialMetaclass):
    """PATCH body schema for partially updating `Observation` entities."""

    datastream: IdSchema = Field(Absent, alias=iot.DATASTREAM)
    feature_of_interest: IdSchema = Field(Absent, alias=iot.FEATURE_OF_INTEREST)


ObservationResponse.add_examples()
ObservationCollectionResponse.add_examples()
ObservationPatchBody.model_rebuild(force=True)
