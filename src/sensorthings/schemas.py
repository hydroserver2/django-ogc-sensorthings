import urllib.parse
from pydantic import Field, ConfigDict, field_validator, model_validator
from typing import Union, Optional, Any
from ninja import Schema
from sensorthings.types import AnyHttpUrlString
from sensorthings.validators import PartialSchema, remove_whitespace
from sensorthings import settings

id_type = settings.ST_API_ID_TYPE


class EntityId(Schema):
    """
    Schema for an entity identifier.

    Attributes
    ----------
    id : id_type
        The identifier for the entity, aliased as '@iot.id'.
    """

    model_config = ConfigDict(populate_by_name=True)

    id: id_type = Field(..., alias='@iot.id')


class EntityNotFound(Schema):
    """
    Schema for an entity not found response.

    Attributes
    ----------
    message : str
        The message describing the error.
    """

    message: str


class PermissionDenied(Schema):
    """
    Schema for a permission denied response.

    Attributes
    ----------
    detail : str
        The detail message describing the permission issue.
    """

    detail: str


class BaseGetResponse(EntityId, Schema, metaclass=PartialSchema):
    """
    Base schema for a GET response, including a self-link.

    Attributes
    ----------
    self_link : AnyHttpUrlString
        The self-link for the entity, aliased as '@iot.selfLink'.
    """

    model_config = ConfigDict(populate_by_name=True)

    self_link: AnyHttpUrlString = Field(..., alias='@iot.selfLink')

    @model_validator(mode='before')
    @classmethod
    def check_response_is_dict(cls, data: Any) -> Any:
        """
        Check that the response is a dictionary.

        Parameters
        ----------
        data : Any
            The data to validate.

        Returns
        -------
        Any
            The validated data.
        """

        assert isinstance(data._obj, dict)  # noqa
        return data


class BasePostBody(Schema):
    """
    Base schema for a POST request body.

    Includes a validator to remove leading and trailing whitespace from all fields.
    """

    model_config = ConfigDict(populate_by_name=True, extra='forbid')

    _whitespace_validator = field_validator(
        '*',
        check_fields=False
    )(remove_whitespace)


class BasePatchBody(Schema, metaclass=PartialSchema):
    """
    Base schema for a PATCH request body.

    Includes a validator to remove leading and trailing whitespace from all fields and disables
    required field validation.
    """

    model_config = ConfigDict(populate_by_name=True, extra='forbid')

    _whitespace_validator = field_validator(
        '*',
        check_fields=False
    )(remove_whitespace)


class BaseComponent(Schema):
    """
    Base schema for a component.

    Methods
    -------
    get_related_components():
        Returns related components based on the 'relationship' field.
    """

    @classmethod
    def get_related_components(cls):
        """
        Get related components based on the 'relationship' field.

        Returns
        -------
        dict
            A dictionary of related components.
        """

        return {
            name: field for name, field in cls.model_fields.items()
            if field.json_schema_extra and field.json_schema_extra.get('relationship') is not None
        }


class BaseListResponse(Schema):
    """
    Base schema for a list response.

    Attributes
    ----------
    count : Union[int, None]
        The count of items, aliased as '@iot.count'.
    value : list
        The list of items.
    next_link : Union[AnyHttpUrlString, None]
        The next link for pagination, aliased as '@iot.nextLink'.
    """

    model_config = ConfigDict(populate_by_name=True)

    count: Union[int, None] = Field(None, alias='@iot.count')
    value: list = []
    next_link: Optional[AnyHttpUrlString] = Field(None, alias='@iot.nextLink')


class GetQueryParams(Schema):
    """
    Schema for query parameters used in GET requests.

    Attributes
    ----------
    expand : str
        The expand parameter, aliased as '$expand'.
    select : str
        The select parameter, aliased as '$select'.
    """

    expand: Optional[str] = Field(None, alias='$expand')
    select: Optional[str] = Field(None, alias='$select')


class ListQueryParams(GetQueryParams):
    """
    Schema for query parameters used in list requests.

    Attributes
    ----------
    filters : str
        The filter parameter, aliased as '$filter'.
    count : bool
        The count parameter, aliased as '$count'.
    order_by : str
        The order by parameter, aliased as '$orderby'.
    skip : int
        The skip parameter, aliased as '$skip'.
    top : int
        The top parameter, aliased as '$top'.
    select : str
        The select parameter, aliased as '$select'.
    """

    model_config = ConfigDict(populate_by_name=True)

    filters: Optional[str] = Field(None, alias='$filter')
    count: Optional[bool] = Field(None, alias='$count')
    order_by: Optional[str] = Field(None, alias='$orderby')
    skip: Optional[int] = Field(0, alias='$skip')
    top: Optional[int] = Field(None, alias='$top')
    select: Optional[str] = Field(None, alias='$select')

    def get_query_string(self):
        """
        Generate the query string from the provided parameters.

        Returns
        -------
        str
            The generated query string.
        """

        query_string = '&'.join([
            f'{model.alias}={urllib.parse.quote(str(getattr(self, field)), safe="~")}'
            for field, model in self.model_fields.items() if getattr(self, field, None) is not None
        ])

        if query_string:
            query_string = '?' + query_string

        return query_string
