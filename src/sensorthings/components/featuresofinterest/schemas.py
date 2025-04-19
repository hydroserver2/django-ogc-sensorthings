from typing import TYPE_CHECKING, Literal, List, Optional
from pydantic import Field, ConfigDict
from geojson_pydantic import Feature
from ninja import Schema
from sensorthings.schemas import EntityId, BaseComponent, BaseListResponse, BaseGetResponse, BasePostBody, BasePatchBody
from sensorthings.types import AnyHttpUrlString

if TYPE_CHECKING:
    from sensorthings.components.observations.schemas import Observation


featureEncodingTypes = Literal['application/geo+json']


class FeatureOfInterestFields(Schema):
    """
    A schema representing the fields of a feature of interest.

    Attributes
    ----------
    name : str
        The name of the feature of interest.
    description : str
        The description of the feature of interest.
    encoding_type : featureEncodingTypes
        The encoding type of the feature.
    feature : Feature
        The GeoJSON feature.
    properties : dict, optional
        Additional properties of the feature of interest.
    """

    name: str = Field(..., alias='name')
    description: str = Field(..., alias='description')
    encoding_type: featureEncodingTypes = Field(..., alias='encodingType')
    feature: Feature = Field(..., alias='feature')
    properties: Optional[dict] = Field(None, alias='properties')


class FeatureOfInterestRelations(Schema):
    """
    A schema representing the relations of a feature of interest to other components.

    Attributes
    ----------
    observations : List['Observation']
        The list of observations related to the feature of interest.
    """

    observations: List['Observation'] = Field(
        [], alias='Observations',
        json_schema_extra={'relationship': 'one_to_many', 'back_ref': 'feature_of_interest_id'}
    )


class FeatureOfInterest(BaseComponent, FeatureOfInterestFields, FeatureOfInterestRelations):
    """
    A schema representing a feature of interest.

    This class combines the fields and relations of a feature of interest, and extends the BaseComponent class.
    """

    model_config = ConfigDict(
        json_schema_extra={'name_ref': ('FeaturesOfInterest', 'feature_of_interest', 'features_of_interest')}
    )


class FeatureOfInterestPostBody(BasePostBody, FeatureOfInterestFields):
    """
    A schema for the body of a POST request to create a new feature of interest.

    Attributes
    ----------
    observations : List[EntityId]
        The list of observation IDs related to the feature of interest.
    """

    observations: List[EntityId] = Field(
        [], alias='Observations', json_schema_extra={'nested_class': 'ObservationPostBody'}
    )


class FeatureOfInterestPatchBody(FeatureOfInterestFields, BasePatchBody):
    """
    A schema for the body of a PATCH request to update an existing feature of interest.
    """
    pass


class FeatureOfInterestGetResponse(FeatureOfInterestFields, BaseGetResponse):
    """
    A schema for the response of a GET request for a feature of interest.

    Attributes
    ----------
    observations_link : AnyHttpUrlString, optional
        The navigation link for the observations related to the feature of interest.
    observations_rel : List[dict], optional
        The relationship details for the observations related to the feature of interest.
    """

    observations_link: AnyHttpUrlString = Field(None, alias='Observations@iot.navigationLink')
    observations_rel: List[dict] = Field(
        None, alias='Observations', json_schema_extra={'nested_class': 'ObservationGetResponse'}
    )


class FeatureOfInterestListResponse(BaseListResponse):
    """
    A schema for the response of a GET request for a list of features of interest.

    Attributes
    ----------
    value : List[FeatureOfInterestGetResponse]
        The list of features of interest.
    """

    value: List[FeatureOfInterestGetResponse]
