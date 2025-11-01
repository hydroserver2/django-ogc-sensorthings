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
    from .observation import ObservationResponse, ObservationPostBody


class FeatureOfInterestFields(BaseSchema):
    """Base schema for `FeatureOfInterest` entity fields."""

    name: str
    description: str
    encoding_type: app_settings.FEATURE_OF_INTEREST_ENCODING_TYPE_VALUE_LITERAL
    feature: app_settings.FEATURE_OF_INTEREST_ENCODING_TYPE_SCHEMA
    properties: app_settings.PROPERTIES_SCHEMAS.get(iot.FEATURE_OF_INTEREST, dict) = (
        Absent
    )


class FeatureOfInterestResponse(
    FeatureOfInterestFields, BaseEntitySchema, metaclass=PartialMetaclass
):
    """GET response schema representing a `FeatureOfInterest` entity."""

    _entity: ClassVar[str] = iot.FEATURES_OF_INTEREST
    _related_entities: ClassVar[list[str]] = [iot.OBSERVATIONS]

    observations_link: str = Field(Absent, alias=iot.OBSERVATIONS + iot.NAVIGATION_LINK)
    observations_count: int = Field(Absent, alias=iot.OBSERVATIONS + iot.COUNT)
    observations: list["ObservationResponse"] = Field(Absent, alias=iot.OBSERVATIONS)
    observations_next_link: str = Field(Absent, alias=iot.OBSERVATIONS + iot.NEXT_LINK)


class FeatureOfInterestCollectionResponse(
    BaseCollectionSchema[FeatureOfInterestResponse]
):
    """GET response schema representing a collection of `FeatureOfInterest` entities."""

    _entity = iot.FEATURES_OF_INTEREST


class FeatureOfInterestPostBody(FeatureOfInterestFields):
    """POST body schema for creating a new `FeatureOfInterest` entity."""

    observations: list[Union[IdSchema, "ObservationPostBody"]] = Field(
        Absent, alias=iot.OBSERVATIONS
    )


class FeatureOfInterestPatchBody(FeatureOfInterestFields, metaclass=PartialMetaclass):
    """PATCH body schema for partially updating `FeatureOfInterest` entities."""

    observations: list[IdSchema] = Field(Absent, alias=iot.OBSERVATIONS)


FeatureOfInterestResponse.add_examples()
FeatureOfInterestCollectionResponse.add_examples()
FeatureOfInterestPatchBody.model_rebuild(force=True)
