from typing import Union
from ninja import Query
from django.http import HttpRequest, HttpResponse
from sensorthings.http import (
    OperationDefinition,
    get_collection_error_responses,
    create_entity_error_responses,
    http_error,
)
from sensorthings.versions.v1_1 import sta
from sensorthings.versions.v1_1 import sensorthings_service
from sensorthings.versions.v1_1.schemas import ObservationCollectionResponse
from sensorthings.versions.v1_1.extensions.dataarray.schemas import (
    ObservationDataArrayCollectionQuery,
    ObservationDataArrayCollectionResponse,
    ObservationDataArrayPostBody
)
from sensorthings.versions.v1_1 import app_settings


async def get_observation_collection(
    request: HttpRequest,
    query: Query[ObservationDataArrayCollectionQuery],
) -> tuple[int, Union[ObservationDataArrayCollectionResponse, ObservationCollectionResponse]]:
    """
    Retrieve a collection of `Observation` entities.
    """

    try:
        collection = await sensorthings_service.get_collection(
            entity_type=sta.OBSERVATION_ENTITY,
            filters=query.filters,
            count=query.count,
            orderby=query.orderby,
            skip=query.skip,
            top=query.top,
            select=query.select,
            expand=query.expand,
            result_format=query.result_format,
            context=request,
        )
    except Exception as e:
        raise http_error(e)

    return 200, collection


get_observation_collection_operation = OperationDefinition(
    path=str(sta.OBSERVATIONS),
    methods=["GET"],
    view_func=get_observation_collection,
    auth=app_settings.AUTH_HANDLERS.get(
        "get_observation_collection", app_settings.DEFAULT_AUTH_HANDLER
    ),
    response={
        200: Union[ObservationDataArrayCollectionResponse, ObservationCollectionResponse],
        **get_collection_error_responses
    }
)


async def create_observation_entities(
    request: HttpRequest, response: HttpResponse, payload: ObservationDataArrayPostBody
) -> tuple[int, None]:
    """
    Create new `Observation` entities.
    """

    try:
        entity = await sensorthings_service.observations.create_entity(
            entity_type=sta.OBSERVATION_ENTITY,
            payload=payload,
            context=request
        )
        response.headers["Observation"] = entity.iot_self_link
    except Exception as e:
        raise http_error(e)

    return 201, None


create_observations_operation = OperationDefinition(
    path=f"Create{str(sta.OBSERVATIONS)}",
    methods=["POST"],
    view_func=create_observation_entities,
    auth=app_settings.AUTH_HANDLERS.get(
        "create_observation_entity", app_settings.DEFAULT_AUTH_HANDLER
    ),
    response={
        201: None, **create_entity_error_responses
    }
)
