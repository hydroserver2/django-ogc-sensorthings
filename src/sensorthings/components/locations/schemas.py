from typing import TYPE_CHECKING, Literal, List, Union, Optional
from pydantic import Field, ConfigDict
from geojson_pydantic import Feature
from ninja import Schema
from sensorthings.schemas import (BaseComponent, BaseListResponse, BaseGetResponse, BasePostBody, BasePatchBody,
                                  EntityId)
from sensorthings.types import AnyHttpUrlString

if TYPE_CHECKING:
    from sensorthings.components.things.schemas import Thing
    from sensorthings.components.historicallocations.schemas import HistoricalLocation


locationEncodingTypes = Literal['application/geo+json']


class LocationFields(Schema):
    """
    A schema representing the fields of a location.

    Attributes
    ----------
    name : str
        The name of the location.
    description : str
        The description of the location.
    encoding_type : locationEncodingTypes
        The encoding type of the location, typically 'application/geo+json'.
    location : Feature
        The GeoJSON feature representing the location.
    properties : dict
        Additional properties of the location.
    """

    name: str = Field(..., alias='name')
    description: str = Field(..., alias='description')
    encoding_type: locationEncodingTypes = Field(..., alias='encodingType')
    location: Feature = Field(..., alias='location')
    properties: Optional[dict] = Field(None, alias='properties')


class LocationRelations(Schema):
    """
    A schema representing the relations of a location to other components.

    Attributes
    ----------
    things : List['Thing']
        The list of things associated with the location.
    historical_locations : List['HistoricalLocation']
        The list of historical locations associated with the location.
    """

    things: List['Thing'] = Field(
        [], alias='Things',
        json_schema_extra={'relationship': 'many_to_many', 'back_ref': 'location_id'}
    )
    historical_locations: List['HistoricalLocation'] = Field(
        [], alias='HistoricalLocations',
        json_schema_extra={'relationship': 'many_to_many', 'back_ref': 'location_id'}
    )


class Location(BaseComponent, LocationFields, LocationRelations):
    """
    A schema representing a location.

    This class combines the fields and relations of a location, and extends the BaseComponent class.
    """

    model_config = ConfigDict(json_schema_extra={'name_ref': ('Locations', 'location', 'locations')})


class LocationPostBody(BasePostBody, LocationFields):
    """
    A schema for the body of a POST request to create a new location.

    Attributes
    ----------
    things : List[Union[EntityId]]
        The list of thing IDs associated with the location.
    historical_locations : List[Union[EntityId]]
        The list of historical location IDs associated with the location.
    """

    things: List[Union[EntityId]] = Field(
        [], alias='Things', json_schema_extra={'nested_class': 'ThingPostBody'}
    )
    historical_locations: List[Union[EntityId]] = Field(
        [], alias='HistoricalLocations', json_schema_extra={'nested_class': 'HistoricalLocationPostBody'}
    )


class LocationPatchBody(LocationFields, BasePatchBody):
    """
    A schema for the body of a PATCH request to update an existing location.

    Attributes
    ----------
    things : List[EntityId]
        The list of thing IDs associated with the location.
    historical_locations : List[EntityId]
        The list of historical location IDs associated with the location.
    """

    things: List[EntityId] = Field([], alias='Things')
    historical_locations: List[EntityId] = Field([], alias='HistoricalLocations')


class LocationGetResponse(LocationFields, BaseGetResponse):
    """
    A schema for the response of a GET request for a location.

    Attributes
    ----------
    things_link : AnyHttpUrlString, optional
        The navigation link for the things associated with the location.
    things_rel : List[dict], optional
        The relationship details for the things associated with the location.
    historical_locations_link : AnyHttpUrlString, optional
        The navigation link for the historical locations.
    historical_locations_rel : List[dict], optional
        The relationship details for the historical locations.
    """

    things_link: AnyHttpUrlString = Field(None, alias='Things@iot.navigationLink')
    things_rel: List[dict] = Field(None, alias='Things', json_schema_extra={'nested_class': 'ThingGetResponse'})
    historical_locations_link: AnyHttpUrlString = Field(None, alias='HistoricalLocations@iot.navigationLink')
    historical_locations_rel: List[dict] = Field(
        None, alias='HistoricalLocations',
        json_schema_extra={'nested_class': 'HistoricalLocationGetResponse'}
    )


class LocationListResponse(BaseListResponse):
    """
    A schema for the response of a GET request for a list of locations.

    Attributes
    ----------
    value : List[LocationGetResponse]
        The list of locations.
    """

    value: List[LocationGetResponse]
