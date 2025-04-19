from typing import List, Literal, Optional, Union
from pydantic import Field, ConfigDict, model_validator
from ninja import Schema
from sensorthings.schemas import BaseListResponse, EntityId, ListQueryParams
from sensorthings.types import ISOTimeString, ISOIntervalString, AnyHttpUrlString
from sensorthings.components.observations.schemas import (ObservationFields,
                                                          ObservationGetResponse as CoreObservationGetResponse,
                                                          observationComponents)
from sensorthings import settings


id_type = settings.ST_API_ID_TYPE
observationResultFormats = Literal['dataArray']
dataArray = List[List[Union[id_type, float, ISOTimeString, ISOIntervalString, dict]]]


class ObservationDataArrayFields(ObservationFields, EntityId):
    """
    Schema representing the fields of an observation in data array format.

    Attributes
    ----------
    datastream_id : id_type
        ID of the Datastream associated with the observation.
    feature_of_interest_id : Optional[id_type], optional
        ID of the Feature of Interest associated with the observation.
    """

    model_config = ConfigDict(populate_by_name=True)

    datastream_id: id_type = Field(..., alias='Datastream/id')
    feature_of_interest_id: Optional[id_type] = Field(None, alias='FeatureOfInterest/id')


class ObservationDataArrayResponse(Schema):
    """
    Response schema for an observation in data array format.

    Attributes
    ----------
    datastream : AnyHttpUrlString, optional
        Navigation link to the Datastream associated with the observation.
    components : List[observationComponents]
        List of observation components specified in the data array.
    data_array : List[list]
        List of lists representing the data array structure.
    """

    model_config = ConfigDict(populate_by_name=True)

    datastream: AnyHttpUrlString = Field(None, alias='Datastream@iot.navigationLink')
    components: List[observationComponents]
    data_array: dataArray = Field(..., alias='dataArray')


class ObservationDataArrayPostBody(Schema):
    """
    Schema for creating an observation in data array format.

    Attributes
    ----------
    datastream : EntityId
        ID of the Datastream associated with the observation.
    components : List[observationComponents]
        List of observation components specified in the data array.
    data_array : List[list]
        List of lists representing the data array structure.
    """

    model_config = ConfigDict(populate_by_name=True)

    datastream: EntityId = Field(..., alias='Datastream')
    components: List[observationComponents]
    data_array: dataArray = Field(..., alias='dataArray')


class ObservationQueryParams(ListQueryParams):
    """
    Query parameters schema for filtering observations.

    Attributes
    ----------
    result_format : Optional[observationResultFormats], optional
        Result format for the query, defaults to None.
    """

    model_config = ConfigDict(populate_by_name=True)

    result_format: Optional[observationResultFormats] = Field(None, alias='$resultFormat')


class ObservationGetResponse(CoreObservationGetResponse):
    """
    Response schema for an observation that can be used in conjunction with a data array response format.
    """

    @model_validator(mode='before')
    def check_no_components(cls, values):
        if 'components' in values._obj:  # noqa
            raise ValueError('Field "components" should not be included outside data array responses.')
        return values


class ObservationListResponse(BaseListResponse):
    """
    Response schema for a list of observations.

    Attributes
    ----------
    value : Union[List[ObservationDataArrayResponse], List[ObservationGetResponse]]
        List containing either ObservationDataArrayResponse or ObservationGetResponse objects.
    """

    value: Union[List[ObservationGetResponse], List[ObservationDataArrayResponse]]
