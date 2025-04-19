from ninja import Query
from django.http import HttpResponse
from sensorthings import settings
from sensorthings.router import SensorThingsRouter
from sensorthings.http import SensorThingsHttpRequest
from sensorthings.schemas import GetQueryParams, ListQueryParams
from sensorthings.components.datastreams.schemas import Datastream
from sensorthings.factories import SensorThingsRouterFactory, SensorThingsEndpointFactory
from .schemas import (Observation, ObservationPostBody, ObservationPatchBody, ObservationListResponse,
                      ObservationGetResponse)


id_qualifier = settings.ST_API_ID_QUALIFIER
id_type = settings.ST_API_ID_TYPE


def list_observations(
        request: SensorThingsHttpRequest,
        params: ListQueryParams = Query(...)
):
    """
    Get a collection of Observation entities.

    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/observation/properties" target="_blank">\
      Observation Properties</a> -
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/observation/relations" target="_blank">\
      Observation Relations</a>
    """

    return request.engine.list_entities(
        component=Observation,
        query_params=params.dict()
    )


list_observations_endpoint = SensorThingsEndpointFactory(
    router_name='observation',
    endpoint_route='/Observations',
    view_function=list_observations,
    view_method=SensorThingsRouter.st_list,
    view_response_schema=ObservationListResponse,
)


def get_observation(
        request: SensorThingsHttpRequest,
        observation_id: id_type,
        params: GetQueryParams = Query(...)
):
    """
    Get an Observation entity.

    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/observation/properties" target="_blank">\
      Observation Properties</a> -
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/observation/relations" target="_blank">\
      Observation Relations</a>
    """

    return request.engine.get_entity(
        component=Observation,
        entity_id=observation_id,
        query_params=params.dict()
    )


get_observation_endpoint = SensorThingsEndpointFactory(
    router_name='observation',
    endpoint_route=f'/Observations({id_qualifier}{{observation_id}}{id_qualifier})',
    view_function=get_observation,
    view_method=SensorThingsRouter.st_get,
    view_response_schema=ObservationGetResponse,
)


def create_observation(
        request: SensorThingsHttpRequest,
        response: HttpResponse,
        observation: ObservationPostBody
):
    """
    Create a new Observation entity.

    Links:
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/observation/properties" target="_blank">\
      Observation Properties</a> -
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/observation/relations" target="_blank">\
      Observation Relations</a> -
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/create-update-delete/create-entity" target="_blank">\
      Create Entity</a>
    """

    request.engine.create_entity(
        component=Observation,
        response=response,
        entity_body=observation
    )

    request.engine.update_related_components(
        component=Datastream, related_entity_id=observation.datastream.id
    )

    return 201, None


create_observation_endpoint = SensorThingsEndpointFactory(
    router_name='observation',
    endpoint_route='/Observations',
    view_function=create_observation,
    view_method=SensorThingsRouter.st_post,
)


def update_observation(
        request: SensorThingsHttpRequest,
        observation_id: id_type,
        observation: ObservationPatchBody
):
    """
    Update an existing Observation entity.

    Links:
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/observation/properties" target="_blank">\
      Observation Properties</a> -
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/observation/relations" target="_blank">\
      Observation Relations</a> -
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/create-update-delete/update-entity" target="_blank">\
      Update Entity</a>
    """

    request.engine.update_entity(
        component=Observation,
        entity_id=observation_id,
        entity_body=observation
    )

    return 204, None


update_observation_endpoint = SensorThingsEndpointFactory(
    router_name='observation',
    endpoint_route=f'/Observations({id_qualifier}{{observation_id}}{id_qualifier})',
    view_function=update_observation,
    view_method=SensorThingsRouter.st_patch,
)


def delete_observation(
        request: SensorThingsHttpRequest,
        observation_id: id_type
):
    """
    Delete a Observation entity.

    Links:
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/create-update-delete/delete-entity" target="_blank">\
      Delete Entity</a>
    """

    request.engine.delete_entity(
        component=Observation,
        entity_id=observation_id
    )

    return 204, None


delete_observation_endpoint = SensorThingsEndpointFactory(
    router_name='observation',
    endpoint_route=f'/Observations({id_qualifier}{{observation_id}}{id_qualifier})',
    view_function=delete_observation,
    view_method=SensorThingsRouter.st_delete,
)


observation_router_factory = SensorThingsRouterFactory(
    name='observation',
    tags=['Observations'],
    endpoints=[
        list_observations_endpoint,
        get_observation_endpoint,
        create_observation_endpoint,
        update_observation_endpoint,
        delete_observation_endpoint
    ]
)
