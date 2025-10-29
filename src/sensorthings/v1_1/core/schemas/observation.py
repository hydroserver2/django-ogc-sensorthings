from typing import Optional, Dict, Union, TYPE_CHECKING
from ninja import Field
from sensorthings.types import (ISOTimeString, ISOIntervalString, example_iso_time_string,
                                example_iso_interval_string)
from sensorthings.v1_1.conf import app_settings
from .base import iot, BaseSchema, BaseEntitySchema, BaseCollectionSchema, IdSchema

if TYPE_CHECKING:
    from .datastream import DatastreamResponse, DatastreamPostBody
    from .feature_of_interest import FeatureOfInterestResponse, FeatureOfInterestPostBody


class ObservationFields(BaseSchema):
    phenomenon_time: Union[ISOTimeString, ISOIntervalString] = Field(
        ..., examples=[example_iso_time_string, example_iso_interval_string]
    )
    result: app_settings.OBSERVATION_TYPE_SCHEMA
    result_time: ISOTimeString = Field(..., example=example_iso_time_string)
    result_quality: Optional[Dict] = None
    valid_time: Optional[ISOIntervalString] = Field(None, example=example_iso_interval_string)
    parameters: Optional[Dict] = None


class ObservationResponse(ObservationFields, BaseEntitySchema):
    _entity = iot.OBSERVATIONS
    _related_entities = [iot.DATASTREAM, iot.FEATURE_OF_INTEREST]

    datastream_link: Optional[str] = Field(None, alias=iot.DATASTREAM + iot.NAVIGATION_LINK)
    datastream: Optional["DatastreamResponse"] = Field(None, alias=iot.DATASTREAM)

    feature_of_interest_link: Optional[str] = Field(None, alias=iot.FEATURE_OF_INTEREST + iot.NAVIGATION_LINK)
    feature_of_interest: Optional["FeatureOfInterestResponse"] = Field(None, alias=iot.FEATURE_OF_INTEREST)


class ObservationCollectionResponse(BaseCollectionSchema[ObservationResponse]):
    _entity = iot.OBSERVATIONS


class ObservationPostBody(ObservationFields):
    datastream: Union[IdSchema, "DatastreamPostBody"] = Field(..., alias=iot.DATASTREAM)
    feature_of_interest: Union[IdSchema, "FeatureOfInterestPostBody"] = Field(..., alias=iot.FEATURE_OF_INTEREST)


class ObservationPatchBody(ObservationFields):
    datastream: IdSchema = Field(..., alias=iot.DATASTREAM)
    feature_of_interest: IdSchema = Field(..., alias=iot.FEATURE_OF_INTEREST)


ObservationResponse.add_examples()
ObservationCollectionResponse.add_examples()
