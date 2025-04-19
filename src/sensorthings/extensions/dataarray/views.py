from typing import List
from sensorthings import settings
from sensorthings.router import SensorThingsRouter
from sensorthings.http import SensorThingsHttpRequest
from sensorthings.factories import SensorThingsEndpointFactory, SensorThingsEndpointHookFactory
from sensorthings.components.datastreams.schemas import Datastream
from sensorthings.components.observations.schemas import Observation
from sensorthings.extensions.dataarray.schemas import (ObservationDataArrayPostBody, ObservationQueryParams,
                                                       ObservationListResponse)


id_qualifier = settings.ST_API_ID_QUALIFIER
id_type = settings.ST_API_ID_TYPE


def create_observations(
        request: SensorThingsHttpRequest,
        observations: List[ObservationDataArrayPostBody]
):
    """
    Create new Observation entities.

    Links:
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/observation/properties" target="_blank">\
      Observation Properties</a> -
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/observation/relations" target="_blank">\
      Observation Relations</a> -
    <a href="https://docs.ogc.org/is/18-088/18-088.html#create-observation-dataarray" target="_blank">\
      Create Entities</a>
    """

    observation_ids = request.engine.create_observations( # noqa
        observations=request.engine.convert_from_data_array(observations) # noqa
    )

    datastream_ids = list(set([
        observation_group.datastream.id for observation_group in observations
    ]))

    for datastream_id in datastream_ids:
        request.engine.update_related_components(
            component=Datastream, related_entity_id=datastream_id
        )

    observation_links = [
        request.engine.build_ref_link(Observation, observation_id)
        for observation_id in observation_ids
    ]

    return 201, observation_links


def serialize_data_array(view_function):
    def wrapper(*args, **kwargs):
        response = view_function(*args, **kwargs)
        if getattr(kwargs['params'], 'result_format', None) == 'dataArray':
            response = args[0].engine.convert_to_data_array( # noqa
                response=response,
                select=getattr(kwargs['params'], 'select', None)
            )
        return response
    return wrapper


data_array_endpoints = [SensorThingsEndpointFactory(
    router_name='observation',
    endpoint_route='/CreateObservations',
    view_function=create_observations,
    view_method=SensorThingsRouter.st_post
)]

data_array_endpoint_hooks = [SensorThingsEndpointHookFactory(
    endpoint_name='list_observations',
    view_query_params=ObservationQueryParams,
    view_response_schema=ObservationListResponse,
    view_wrapper=serialize_data_array
)]
