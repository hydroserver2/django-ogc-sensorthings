from typing import TYPE_CHECKING, Literal, Union, List, Dict, Optional
from pydantic import Field, ConfigDict
from ninja import Schema
from sensorthings.schemas import (BaseComponent, BaseListResponse, BaseGetResponse, BasePostBody, BasePatchBody,
                                  EntityId)
from sensorthings.types import ISOTimeString, ISOIntervalString, AnyHttpUrlString

if TYPE_CHECKING:
    from sensorthings.components.datastreams.schemas import Datastream
    from sensorthings.components.featuresofinterest.schemas import FeatureOfInterest


observationTypes = Literal[
    'http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_CategoryObservation',
    'http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_CountObservation',
    'http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement',
    'http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Observation',
    'http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_TruthObservation'
]


observationComponents = Literal[
    '@iot.id', 'phenomenonTime', 'result', 'resultTime', 'resultQuality', 'validTime', 'parameters',
    'FeatureOfInterest/id'
]


class ObservationFields(Schema):
    """
    A schema representing the fields of an observation.

    Attributes
    ----------
    phenomenon_time : Union[ISOTimeString, ISOIntervalString]
        The time when the observation phenomenon occurred.
    result : float
        The result of the observation.
    result_time : Union[ISOTimeString, None], optional
        The time when the observation result was generated.
    result_quality : dict
        The quality of the observation result.
    valid_time : Union[ISOIntervalString, None], optional
        The time period during which the observation result is valid.
    parameters : dict
        Additional parameters for the observation.
    """

    model_config = ConfigDict(populate_by_name=True)

    phenomenon_time: Union[ISOTimeString, ISOIntervalString] = Field(..., alias='phenomenonTime')
    result: float = Field(..., alias='result')
    result_time: Optional[ISOTimeString] = Field(None, alias='resultTime')
    result_quality: Optional[dict] = Field(None, alias='resultQuality')
    valid_time: Optional[ISOIntervalString] = Field(None, alias='validTime')
    parameters: Optional[dict] = Field(None, alias='parameters')


class ObservationRelations(Schema):
    """
    A schema representing the relations of an observation to other components.

    Attributes
    ----------
    datastream : 'Datastream'
        The datastream associated with the observation.
    feature_of_interest : 'FeatureOfInterest'
        The feature of interest associated with the observation.
    """

    model_config = ConfigDict(populate_by_name=True)

    datastream: 'Datastream' = Field(
        ..., alias='Datastream', json_schema_extra={'relationship': 'many_to_one', 'back_ref': 'datastream_id'}
    )
    feature_of_interest: 'FeatureOfInterest' = Field(
        ..., alias='FeatureOfInterest',
        json_schema_extra={'relationship': 'many_to_one', 'back_ref': 'feature_of_interest_id'}
    )


class Observation(BaseComponent, ObservationFields, ObservationRelations):
    """
    A schema representing an observation.

    This class combines the fields and relations of an observation, and extends the BaseComponent class.
    """

    model_config = ConfigDict(json_schema_extra={'name_ref': ('Observations', 'observation', 'observations')})


class ObservationPostBody(BasePostBody, ObservationFields):
    """
    A schema for the body of a POST request to create a new observation.

    Attributes
    ----------
    datastream : Union[EntityId]
        The ID of the datastream associated with the observation.
    feature_of_interest : Union[EntityId, None], optional
        The ID of the feature of interest associated with the observation.
    """

    model_config = ConfigDict(populate_by_name=True)

    datastream: Union[EntityId] = Field(
        ..., alias='Datastream', json_schema_extra={'nested_class': 'DatastreamPostBody'}
    )
    feature_of_interest: Union[EntityId, None] = Field(
        None, alias='FeatureOfInterest', json_schema_extra={'nested_class': 'FeatureOfInterestPostBody'}
    )


class ObservationPatchBody(BasePatchBody, ObservationFields):
    """
    A schema for the body of a PATCH request to update an existing observation.

    Attributes
    ----------
    datastream : Optional[EntityId], optional
        The ID of the datastream associated with the observation.
    feature_of_interest : Optional[EntityId], optional
        The ID of the feature of interest associated with the observation.
    """

    model_config = ConfigDict(populate_by_name=True)

    datastream: Optional[EntityId] = Field(None, alias='Datastream')
    feature_of_interest: Optional[EntityId] = Field(None, alias='FeatureOfInterest')


class ObservationGetResponse(ObservationFields, BaseGetResponse):
    """
    A schema for the response of a GET request for an observation.

    Attributes
    ----------
    datastream_link : AnyHttpUrlString, optional
        The navigation link for the datastream associated with the observation.
    datastream_rel : Dict, optional
        The relationship details for the datastream associated with the observation.
    feature_of_interest_link : AnyHttpUrlString, optional
        The navigation link for the feature of interest associated with the observation.
    feature_of_interest_rel : Dict, optional
        The relationship details for the feature of interest associated with the observation.
    """

    model_config = ConfigDict(populate_by_name=True)

    datastream_link: AnyHttpUrlString = Field(None, alias='Datastream@iot.navigationLink')
    datastream_rel: Dict = Field(
        None, alias='Datastream', json_schema_extra={'nested_class': 'DatastreamGetResponse'}
    )
    feature_of_interest_link: AnyHttpUrlString = Field(None, alias='FeatureOfInterest@iot.navigationLink')
    feature_of_interest_rel: Dict = Field(
        None, alias='FeatureOfInterest',
        json_schema_extra={'nested_class': 'FeatureOfInterestGetResponse'}
    )


class ObservationListResponse(BaseListResponse):
    """
    A schema for the response of a GET request for a list of observations.

    Attributes
    ----------
    value : List[ObservationGetResponse]
        The list of observations.
    """

    value: List[ObservationGetResponse]
