from ninja import Query
from django.http import HttpResponse
from sensorthings import settings
from sensorthings.router import SensorThingsRouter
from sensorthings.http import SensorThingsHttpRequest
from sensorthings.schemas import ListQueryParams, GetQueryParams
from sensorthings.factories import SensorThingsRouterFactory, SensorThingsEndpointFactory
from .schemas import Datastream, DatastreamPostBody, DatastreamPatchBody, DatastreamListResponse, DatastreamGetResponse


id_qualifier = settings.ST_API_ID_QUALIFIER
id_type = settings.ST_API_ID_TYPE


def list_datastreams(
        request: SensorThingsHttpRequest,
        params: ListQueryParams = Query(...)
):
    """
    Get a collection of Datastream entities.

    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/datastream/properties" target="_blank">\
      Datastream Properties</a> -
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/datastream/relations" target="_blank">\
      Datastream Relations</a>
    """

    return request.engine.list_entities(
        component=Datastream,
        query_params=params.dict()
    )


list_datastreams_endpoint = SensorThingsEndpointFactory(
    router_name='datastream',
    endpoint_route='/Datastreams',
    view_function=list_datastreams,
    view_method=SensorThingsRouter.st_list,
    view_response_schema=DatastreamListResponse
)


def get_datastream(
        request: SensorThingsHttpRequest,
        datastream_id: id_type,
        params: GetQueryParams = Query(...)
):
    """
    Get a Datastream entity.

    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/datastream/properties" target="_blank">\
      Datastream Properties</a> -
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/datastream/relations" target="_blank">\
      Datastream Relations</a>
    """

    return request.engine.get_entity(
        component=Datastream,
        entity_id=datastream_id,
        query_params=params.dict()
    )


get_datastream_endpoint = SensorThingsEndpointFactory(
    router_name='datastream',
    endpoint_route=f'/Datastreams({id_qualifier}{{datastream_id}}{id_qualifier})',
    view_function=get_datastream,
    view_method=SensorThingsRouter.st_get,
    view_response_schema=DatastreamGetResponse
)


def create_datastream(
        request: SensorThingsHttpRequest,
        response: HttpResponse,
        datastream: DatastreamPostBody
):
    """
    Create a new Datastream entity.

    Links:
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/datastream/properties" target="_blank">\
      Datastream Properties</a> -
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/datastream/relations" target="_blank">\
      Datastream Relations</a> -
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/create-update-delete/create-entity" target="_blank">\
      Create Entity</a>
    """

    request.engine.create_entity(
        component=Datastream,
        entity_body=datastream,
        response=response
    )

    return 201, None


create_datastream_endpoint = SensorThingsEndpointFactory(
    router_name='datastream',
    endpoint_route='/Datastreams',
    view_function=create_datastream,
    view_method=SensorThingsRouter.st_post,
)


def update_datastream(
        request: SensorThingsHttpRequest,
        datastream_id: id_type,
        datastream: DatastreamPatchBody
):
    """
    Update an existing Datastream entity.

    Links:
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/datastream/properties" target="_blank">\
      Datastream Properties</a> -
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/datastream/relations" target="_blank">\
      Datastream Relations</a> -
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/create-update-delete/update-entity" target="_blank">\
      Update Entity</a>
    """

    request.engine.update_entity(
        component=Datastream,
        entity_id=datastream_id,
        entity_body=datastream
    )

    return 204, None


update_datastream_endpoint = SensorThingsEndpointFactory(
    router_name='datastream',
    endpoint_route=f'/Datastreams({id_qualifier}{{datastream_id}}{id_qualifier})',
    view_function=update_datastream,
    view_method=SensorThingsRouter.st_patch,
)


def delete_datastream(
        request: SensorThingsHttpRequest,
        datastream_id: id_type
):
    """
    Delete a Datastream entity.

    Links:
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/create-update-delete/delete-entity" target="_blank">\
      Delete Entity</a>
    """

    request.engine.delete_entity(
        component=Datastream,
        entity_id=datastream_id
    )

    return 204, None


delete_datastream_endpoint = SensorThingsEndpointFactory(
    router_name='datastream',
    endpoint_route=f'/Datastreams({id_qualifier}{{datastream_id}}{id_qualifier})',
    view_function=delete_datastream,
    view_method=SensorThingsRouter.st_delete,
)


datastream_router_factory = SensorThingsRouterFactory(
    name='datastream',
    tags=['Datastreams'],
    endpoints=[
        list_datastreams_endpoint,
        get_datastream_endpoint,
        create_datastream_endpoint,
        update_datastream_endpoint,
        delete_datastream_endpoint
    ]
)
