from typing import Optional, Dict, List, Union, TYPE_CHECKING
from ninja import Field
from sensorthings.v1_1.conf import app_settings
from .base import iot, BaseSchema, BaseEntitySchema, BaseCollectionSchema, IdSchema

if TYPE_CHECKING:
    from .observation import ObservationResponse, ObservationPostBody


class FeatureOfInterestFields(BaseSchema):
    name: str
    description: str
    encoding_type: app_settings.FEATURE_OF_INTEREST_ENCODING_TYPE_VALUE_LITERAL
    feature: app_settings.FEATURE_OF_INTEREST_ENCODING_TYPE_SCHEMA
    properties: Optional[app_settings.PROPERTIES_SCHEMAS.get("FeatureOfInterest", Dict)] = None


class FeatureOfInterestResponse(FeatureOfInterestFields, BaseEntitySchema):
    _entity = iot.FEATURES_OF_INTEREST
    _related_entities = [iot.OBSERVATIONS]

    observations_link: Optional[str] = Field(None, alias=iot.OBSERVATIONS + iot.NAVIGATION_LINK)
    observations_count: Optional[int] = Field(None, alias=iot.OBSERVATIONS + iot.COUNT)
    observations: Optional[List["ObservationResponse"]] = Field(None, alias=iot.OBSERVATIONS)
    observations_next_link: Optional[str] = Field(None, alias=iot.OBSERVATIONS + iot.NEXT_LINK)


class FeatureOfInterestCollectionResponse(BaseCollectionSchema[FeatureOfInterestResponse]):
    _entity = iot.FEATURES_OF_INTEREST


class FeatureOfInterestPostBody(FeatureOfInterestFields):
    observations: List[Union[IdSchema, "ObservationPostBody"]] = Field(None, alias=iot.OBSERVATIONS)


class FeatureOfInterestPatchBody(FeatureOfInterestFields):
    observations: List[IdSchema] = Field(None, alias=iot.OBSERVATIONS)


FeatureOfInterestResponse.add_examples()
FeatureOfInterestCollectionResponse.add_examples()
