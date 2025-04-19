from ninja import Query
from django.http import HttpResponse
from sensorthings import settings
from sensorthings.router import SensorThingsRouter
from sensorthings.http import SensorThingsHttpRequest
from sensorthings.schemas import ListQueryParams, GetQueryParams
from sensorthings.factories import SensorThingsRouterFactory, SensorThingsEndpointFactory
from .schemas import (ObservedProperty, ObservedPropertyPostBody, ObservedPropertyPatchBody,
                      ObservedPropertyListResponse, ObservedPropertyGetResponse)


id_qualifier = settings.ST_API_ID_QUALIFIER
id_type = settings.ST_API_ID_TYPE


def list_observed_properties(
        request: SensorThingsHttpRequest,
        params: ListQueryParams = Query(...)
):
    """
    Get a collection of Observed Property entities.

    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/observed-property/properties" target="_blank">\
      Observed Property Properties</a> -
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/observed-property/relations" target="_blank">\
      Observed Property Relations</a>
    """

    return request.engine.list_entities(
        component=ObservedProperty,
        query_params=params.dict()
    )


list_observed_properties_endpoint = SensorThingsEndpointFactory(
    router_name='observed_property',
    endpoint_route='/ObservedProperties',
    view_function=list_observed_properties,
    view_method=SensorThingsRouter.st_list,
    view_response_schema=ObservedPropertyListResponse,
)


def get_observed_property(
        request: SensorThingsHttpRequest,
        observed_property_id: id_type,
        params: GetQueryParams = Query(...)
):
    """
    Get an Observed Property entity.

    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/observed-property/properties" target="_blank">\
      Observed Property Properties</a> -
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/observed-property/relations" target="_blank">\
      Observed Property Relations</a>
    """

    return request.engine.get_entity(
        component=ObservedProperty,
        entity_id=observed_property_id,
        query_params=params.dict()
    )


get_observed_property_endpoint = SensorThingsEndpointFactory(
    router_name='observed_property',
    endpoint_route=f'/ObservedProperties({id_qualifier}{{observed_property_id}}{id_qualifier})',
    view_function=get_observed_property,
    view_method=SensorThingsRouter.st_get,
    view_response_schema=ObservedPropertyGetResponse,
)


def create_observed_property(
        request: SensorThingsHttpRequest,
        response: HttpResponse,
        observed_property: ObservedPropertyPostBody
):
    """
    Create a new Observed Property entity.

    Links:
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/observed-property/properties" target="_blank">\
      Observed Property Properties</a> -
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/observed-property/relations" target="_blank">\
      Observed Property Relations</a> -
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/create-update-delete/create-entity" target="_blank">\
      Create Entity</a>
    """

    request.engine.create_entity(
        component=ObservedProperty,
        entity_body=observed_property,
        response=response
    )

    return 201, None


create_observed_property_endpoint = SensorThingsEndpointFactory(
    router_name='observed_property',
    endpoint_route='/ObservedProperties',
    view_function=create_observed_property,
    view_method=SensorThingsRouter.st_post,
)


def update_observed_property(
        request: SensorThingsHttpRequest,
        observed_property_id: id_type,
        observed_property: ObservedPropertyPatchBody
):
    """
    Update an existing Observed Property entity.

    Links:
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/observed-property/properties" target="_blank">\
      Thing Properties</a> -
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/observed-property/relations" target="_blank">\
      Thing Relations</a> -
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/create-update-delete/update-entity" target="_blank">\
      Update Entity</a>
    """

    request.engine.update_entity(
        component=ObservedProperty,
        entity_id=observed_property_id,
        entity_body=observed_property
    )

    return 204, None


update_observed_property_endpoint = SensorThingsEndpointFactory(
    router_name='observed_property',
    endpoint_route=f'/ObservedProperties({id_qualifier}{{observed_property_id}}{id_qualifier})',
    view_function=update_observed_property,
    view_method=SensorThingsRouter.st_patch,
)


def delete_observed_property(request: SensorThingsHttpRequest, observed_property_id: id_type):
    """
    Delete an Observed Property entity.

    Links:
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/create-update-delete/delete-entity" target="_blank">\
      Delete Entity</a>
    """

    request.engine.delete_entity(
        component=ObservedProperty,
        entity_id=observed_property_id
    )

    return 204, None


delete_observed_property_endpoint = SensorThingsEndpointFactory(
    router_name='observed_property',
    endpoint_route=f'/ObservedProperties({id_qualifier}{{observed_property_id}}{id_qualifier})',
    view_function=delete_observed_property,
    view_method=SensorThingsRouter.st_delete,
)


observed_property_router_factory = SensorThingsRouterFactory(
    name='observed_property',
    tags=['Observed Properties'],
    endpoints=[
        list_observed_properties_endpoint,
        get_observed_property_endpoint,
        create_observed_property_endpoint,
        update_observed_property_endpoint,
        delete_observed_property_endpoint
    ]
)
