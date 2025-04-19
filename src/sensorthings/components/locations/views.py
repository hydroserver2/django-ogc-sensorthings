from ninja import Query
from django.http import HttpResponse
from sensorthings import settings
from sensorthings.router import SensorThingsRouter
from sensorthings.http import SensorThingsHttpRequest
from sensorthings.schemas import ListQueryParams, GetQueryParams
from sensorthings.factories import SensorThingsRouterFactory, SensorThingsEndpointFactory
from .schemas import Location, LocationPostBody, LocationPatchBody, LocationListResponse, LocationGetResponse


id_qualifier = settings.ST_API_ID_QUALIFIER
id_type = settings.ST_API_ID_TYPE


def list_locations(
        request: SensorThingsHttpRequest,
        params: ListQueryParams = Query(...)
):
    """
    Get a collection of Location entities.

    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/location/properties" target="_blank">\
      Location Properties</a> -
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/location/relations" target="_blank">\
      Location Relations</a>
    """

    return request.engine.list_entities(
        component=Location,
        query_params=params.dict()
    )


list_locations_endpoint = SensorThingsEndpointFactory(
    router_name='location',
    endpoint_route='/Locations',
    view_function=list_locations,
    view_method=SensorThingsRouter.st_list,
    view_response_schema=LocationListResponse,
)


def get_location(
        request: SensorThingsHttpRequest,
        location_id: id_type,
        params: GetQueryParams = Query(...)
):
    """
    Get a Location entity.

    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/location/properties" target="_blank">\
      Location Properties</a> -
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/location/relations" target="_blank">\
      Location Relations</a>
    """

    return request.engine.get_entity(
        component=Location,
        entity_id=location_id,
        query_params=params.dict()
    )


get_location_endpoint = SensorThingsEndpointFactory(
    router_name='location',
    endpoint_route=f'/Locations({id_qualifier}{{location_id}}{id_qualifier})',
    view_function=get_location,
    view_method=SensorThingsRouter.st_get,
    view_response_schema=LocationGetResponse,
)


def create_location(
        request: SensorThingsHttpRequest,
        response: HttpResponse,
        location: LocationPostBody
):
    """
    Create a new Location entity.

    Links:
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/location/properties" target="_blank">\
      Location Properties</a> -
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/location/relations" target="_blank">\
      Location Relations</a> -
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/create-update-delete/create-entity" target="_blank">\
      Create Entity</a>
    """

    request.engine.create_entity(
        component=Location,
        entity_body=location,
        response=response
    )

    return 201, None


create_location_endpoint = SensorThingsEndpointFactory(
    router_name='location',
    endpoint_route='/Locations',
    view_function=create_location,
    view_method=SensorThingsRouter.st_post,
)


def update_location(
        request: SensorThingsHttpRequest,
        location_id: id_type,
        location: LocationPatchBody
):
    """
    Update an existing Location entity.

    Links:
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/location/properties" target="_blank">\
      Location Properties</a> -
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/location/relations" target="_blank">\
      Location Relations</a> -
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/create-update-delete/update-entity" target="_blank">\
      Update Entity</a>
    """

    request.engine.update_entity(
        component=Location,
        entity_id=location_id,
        entity_body=location
    )

    return 204, None


update_location_endpoint = SensorThingsEndpointFactory(
    router_name='location',
    endpoint_route=f'/Locations({id_qualifier}{{location_id}}{id_qualifier})',
    view_function=update_location,
    view_method=SensorThingsRouter.st_patch,
)


def delete_location(
        request: SensorThingsHttpRequest,
        location_id: id_type
):
    """
    Delete a Location entity.

    Links:
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/create-update-delete/delete-entity" target="_blank">\
      Delete Entity</a>
    """

    request.engine.delete_entity(
        component=Location,
        entity_id=location_id
    )

    return 204, None


delete_location_endpoint = SensorThingsEndpointFactory(
    router_name='location',
    endpoint_route=f'/Locations({id_qualifier}{{location_id}}{id_qualifier})',
    view_function=delete_location,
    view_method=SensorThingsRouter.st_delete,
)


location_router_factory = SensorThingsRouterFactory(
    name='location',
    tags=['Locations'],
    endpoints=[
        list_locations_endpoint,
        get_location_endpoint,
        create_location_endpoint,
        update_location_endpoint,
        delete_location_endpoint
    ]
)
