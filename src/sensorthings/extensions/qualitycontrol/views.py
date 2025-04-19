from typing import List
from sensorthings import settings
from sensorthings.router import SensorThingsRouter
from sensorthings.http import SensorThingsHttpRequest
from sensorthings.factories import SensorThingsEndpointFactory
from sensorthings.components.datastreams.schemas import Datastream
from sensorthings.extensions.qualitycontrol.schemas import DeleteObservationsPostBody
from sensorthings.types.iso_string import parse_iso_interval
from sensorthings.schemas import PermissionDenied


id_qualifier = settings.ST_API_ID_QUALIFIER
id_type = settings.ST_API_ID_TYPE


def delete_observations(
        request: SensorThingsHttpRequest,
        datastreams: List[DeleteObservationsPostBody]
):
    """
    Delete Observation entities.
    """

    for datastream in datastreams:
        start_time, end_time = (
            parse_iso_interval(datastream.phenomenon_time)
            if datastream.phenomenon_time else (None, None)
        )
        request.engine.delete_observations( # noqa
            datastream_id=datastream.datastream.id,
            start_time=start_time,
            end_time=end_time
        )

    datastream_ids = list(set([
        datastream.datastream.id for datastream in datastreams
    ]))

    for datastream_id in datastream_ids:
        request.engine.update_related_components(
            component=Datastream, related_entity_id=datastream_id
        )

    return 204, None


quality_control_endpoints = [SensorThingsEndpointFactory(
    router_name='observation',
    endpoint_route='/DeleteObservations',
    view_function=delete_observations,
    view_method=SensorThingsRouter.st_post,
    view_response_override={
        204: None,
        403: PermissionDenied,
    }
)]
