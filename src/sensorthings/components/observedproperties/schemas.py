from typing import TYPE_CHECKING, List, Optional
from pydantic import Field, ConfigDict
from ninja import Schema
from sensorthings.schemas import EntityId, BaseComponent, BaseListResponse, BaseGetResponse, BasePostBody, BasePatchBody
from sensorthings.types import AnyHttpUrlString

if TYPE_CHECKING:
    from sensorthings.components.datastreams.schemas import Datastream


class ObservedPropertyFields(Schema):
    """
    A schema representing the fields of an observed property.

    Attributes
    ----------
    name : str
        The name of the observed property.
    definition : AnyHttpUrlString
        The definition of the observed property.
    description : str
        The description of the observed property.
    properties : dict
        Additional properties of the observed property.
    """

    name: str = Field(..., alias='name')
    definition: AnyHttpUrlString = Field(..., alias='definition')
    description: str = Field(..., alias='description')
    properties: Optional[dict] = Field(None, alias='properties')


class ObservedPropertyRelations(Schema):
    """
    A schema representing the relations of an observed property to other components.

    Attributes
    ----------
    datastreams : List['Datastream']
        The datastreams associated with the observed property.
    """

    datastreams: List['Datastream'] = Field(
        [], alias='Datastreams', json_schema_extra={'relationship': 'one_to_many', 'back_ref': 'observed_property_id'}
    )


class ObservedProperty(BaseComponent, ObservedPropertyFields, ObservedPropertyRelations):
    """
    A schema representing an observed property.

    This class combines the fields and relations of an observed property, and extends the BaseComponent class.
    """

    model_config = ConfigDict(json_schema_extra={'name_ref': ('ObservedProperties', 'observed_property', 'observed_properties')})


class ObservedPropertyPostBody(BasePostBody, ObservedPropertyFields):
    """
    A schema for the body of a POST request to create a new observed property.

    Attributes
    ----------
    datastreams : List[EntityId]
        The IDs of the datastreams associated with the observed property.
    """

    datastreams: List[EntityId] = Field(
        [], alias='Datastreams', json_schema_extra={'nested_class': 'DatastreamPostBody'}
    )


class ObservedPropertyPatchBody(BasePatchBody, ObservedPropertyFields):
    """
    A schema for the body of a PATCH request to update an existing observed property.
    """

    pass


class ObservedPropertyGetResponse(ObservedPropertyFields, BaseGetResponse):
    """
    A schema for the response of a GET request for an observed property.

    Attributes
    ----------
    datastreams_link : AnyHttpUrlString
        The navigation link for the datastreams associated with the observed property.
    datastreams_rel : List[dict]
        The relationship details for the datastreams associated with the observed property.
    """

    datastreams_link: AnyHttpUrlString = Field(None, alias='Datastreams@iot.navigationLink')
    datastreams_rel: List[dict] = Field(
        None, alias='Datastreams', json_schema_extra={'nested_class': 'DatastreamGetResponse'}
    )


class ObservedPropertyListResponse(BaseListResponse):
    """
    A schema for the response of a GET request for a list of observed properties.

    Attributes
    ----------
    value : List[ObservedPropertyGetResponse]
        The list of observed properties.
    """

    value: List[ObservedPropertyGetResponse]
