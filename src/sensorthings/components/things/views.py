from ninja import Query
from django.http import HttpResponse
from sensorthings import settings
from sensorthings.router import SensorThingsRouter
from sensorthings.http import SensorThingsHttpRequest
from sensorthings.schemas import ListQueryParams, GetQueryParams
from sensorthings.factories import SensorThingsRouterFactory, SensorThingsEndpointFactory
from .schemas import Thing, ThingPostBody, ThingPatchBody, ThingListResponse, ThingGetResponse


id_qualifier = settings.ST_API_ID_QUALIFIER
id_type = settings.ST_API_ID_TYPE


def list_things(
        request: SensorThingsHttpRequest,
        params: ListQueryParams = Query(...)
):
    """
    Get a collection of Thing entities.

    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/thing/properties" target="_blank">\
      Thing Properties</a> -
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/thing/relations" target="_blank">\
      Thing Relations</a>
    """

    return request.engine.list_entities(
        component=Thing,
        query_params=params.dict()
    )


list_things_endpoint = SensorThingsEndpointFactory(
    router_name='thing',
    endpoint_route='/Things',
    view_function=list_things,
    view_method=SensorThingsRouter.st_list,
    view_response_schema=ThingListResponse,
)


def get_thing(
        request: SensorThingsHttpRequest,
        thing_id: id_type,
        params: GetQueryParams = Query(...)
):
    """
    Get a Thing entity.

    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/thing/properties" target="_blank">\
      Thing Properties</a> -
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/thing/relations" target="_blank">\
      Thing Relations</a>
    """

    response = request.engine.get_entity(
        component=Thing,
        entity_id=thing_id,
        query_params=params.dict()
    )

    return response


get_thing_endpoint = SensorThingsEndpointFactory(
    router_name='thing',
    endpoint_route=f'/Things({id_qualifier}{{thing_id}}{id_qualifier})',
    view_function=get_thing,
    view_method=SensorThingsRouter.st_get,
    view_response_schema=ThingGetResponse,
)


def create_thing(
        request: SensorThingsHttpRequest,
        response: HttpResponse,
        thing: ThingPostBody
):
    """
    Create a new Thing entity.

    Links:
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/thing/properties" target="_blank">\
      Thing Properties</a> -
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/thing/relations" target="_blank">\
      Thing Relations</a> -
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/create-update-delete/create-entity" target="_blank">\
      Create Entity</a>
    """

    request.engine.create_entity(
        component=Thing,
        entity_body=thing,
        response=response
    )

    return 201, None


create_thing_endpoint = SensorThingsEndpointFactory(
    router_name='thing',
    endpoint_route='/Things',
    view_function=create_thing,
    view_method=SensorThingsRouter.st_post,
)


def update_thing(
        request: SensorThingsHttpRequest,
        thing_id: id_type,
        thing: ThingPatchBody
):
    """
    Update an existing Thing entity.

    Links:
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/thing/properties" target="_blank">\
      Thing Properties</a> -
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/thing/relations" target="_blank">\
      Thing Relations</a> -
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/create-update-delete/update-entity" target="_blank">\
      Update Entity</a>
    """

    request.engine.update_entity(
        component=Thing,
        entity_id=thing_id,
        entity_body=thing
    )

    return 204, None


update_thing_endpoint = SensorThingsEndpointFactory(
    router_name='sensor',
    endpoint_route=f'/Things({id_qualifier}{{thing_id}}{id_qualifier})',
    view_function=update_thing,
    view_method=SensorThingsRouter.st_patch,
)


def delete_thing(
        request: SensorThingsHttpRequest,
        thing_id: id_type
):
    """
    Delete a Thing entity.

    Links:
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/create-update-delete/delete-entity" target="_blank">\
      Delete Entity</a>
    """

    request.engine.delete_entity(
        component=Thing,
        entity_id=thing_id
    )

    return 204, None


delete_thing_endpoint = SensorThingsEndpointFactory(
    router_name='thing',
    endpoint_route=f'/Things({id_qualifier}{{thing_id}}{id_qualifier})',
    view_function=delete_thing,
    view_method=SensorThingsRouter.st_delete,
)


thing_router_factory = SensorThingsRouterFactory(
    name='thing',
    tags=['Things'],
    endpoints=[
        list_things_endpoint,
        get_thing_endpoint,
        create_thing_endpoint,
        update_thing_endpoint,
        delete_thing_endpoint
    ]
)
