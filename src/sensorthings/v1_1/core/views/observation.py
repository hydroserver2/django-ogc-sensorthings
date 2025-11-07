from ninja import Router, Path, Query
from django.http import HttpRequest, HttpResponse
from sensorthings.v1_1.core import iot
from sensorthings.v1_1.core.service import sensorthings_service
from sensorthings.v1_1.core.schemas import (
    CollectionQuery,
    EntityQuery,
    ObservationCollectionResponse,
    ObservationResponse,
    ObservationPostBody,
    ObservationPatchBody,
)
from sensorthings.v1_1.http import (
    get_collection_error_responses,
    get_entity_error_responses,
    create_entity_error_responses,
    update_entity_error_responses,
    delete_entity_error_responses,
    http_error,
)
from sensorthings.v1_1.conf import app_settings

router = Router(tags=[iot.OBSERVATIONS])


@router.get(
    iot.OBSERVATIONS,
    auth=app_settings.AUTH_HANDLERS.get(
        "get_observation_collection", app_settings.DEFAULT_AUTH_HANDLER
    ),
    response={200: ObservationCollectionResponse, **get_collection_error_responses},
    by_alias=True,
    exclude_none=True,
    exclude_unset=True,
)
async def get_observation_collection(
    request: HttpRequest,
    query: Query[CollectionQuery],
) -> tuple[int, ObservationCollectionResponse]:
    """
    Retrieve a collection of `Observation` entities.
    """

    try:
        resource = await sensorthings_service.observations.get_collection(
            filter=query.filter,
            count=query.count,
            orderby=query.orderby,
            skip=query.skip,
            top=query.top,
            select=query.select,
            expand=query.expand,
            context=request,
        )
    except Exception as e:
        raise e

    return 200, resource


@router.post(
    iot.OBSERVATIONS,
    auth=app_settings.AUTH_HANDLERS.get(
        "create_observation", app_settings.DEFAULT_AUTH_HANDLER
    ),
    response={201: None, **create_entity_error_responses},
)
async def create_observation(
    request: HttpRequest,
    response: HttpResponse,
    entity: ObservationPostBody,
) -> tuple[int, None]:
    """
    Create a new `Observation` entity.
    """

    try:
        resource = await sensorthings_service.create_observation(
            entity=entity, context=request
        )
        response.headers["Location"] = resource.iot_self_link
    except Exception as e:
        raise http_error(e)

    return 201, None


@router.get(
    f"{iot.OBSERVATIONS}({app_settings.ID_DELIMITER}{{entity_id}}{app_settings.ID_DELIMITER})",
    auth=app_settings.AUTH_HANDLERS.get(
        "get_observation", app_settings.DEFAULT_AUTH_HANDLER
    ),
    response={200: ObservationResponse, **get_entity_error_responses},
    by_alias=True,
    exclude_none=True,
    exclude_unset=True,
)
async def get_observation(
    request: HttpRequest,
    query: Query[EntityQuery],
    entity_id: Path[app_settings.ID_TYPE],
) -> tuple[int, ObservationResponse]:
    """
    Retrieve a single `Observation` entity by ID.
    """

    try:
        resource = await sensorthings_service.get_observation(
            entity_id=entity_id,
            select=query.select,
            expand=query.expand,
            context=request,
        )
    except Exception as e:
        raise http_error(e)

    return 200, resource


@router.patch(
    f"{iot.OBSERVATIONS}({app_settings.ID_DELIMITER}{{entity_id}}{app_settings.ID_DELIMITER})",
    auth=app_settings.AUTH_HANDLERS.get(
        "update_observation", app_settings.DEFAULT_AUTH_HANDLER
    ),
    response={204: None, **update_entity_error_responses},
)
async def update_observation(
    request: HttpRequest,
    entity_id: Path[app_settings.ID_TYPE],
    entity: ObservationPatchBody,
) -> tuple[int, None]:
    """
    Update an existing `Observation` entity.
    """

    try:
        await sensorthings_service.update_observation(
            entity_id=entity_id, entity=entity, context=request
        )
    except Exception as e:
        raise http_error(e)

    return 204, None


@router.delete(
    f"{iot.OBSERVATIONS}({app_settings.ID_DELIMITER}{{entity_id}}{app_settings.ID_DELIMITER})",
    auth=app_settings.AUTH_HANDLERS.get(
        "delete_observation", app_settings.DEFAULT_AUTH_HANDLER
    ),
    response={204: None, **delete_entity_error_responses},
)
async def delete_observation(
    request: HttpRequest,
    entity_id: Path[app_settings.ID_TYPE],
) -> tuple[int, None]:
    """
    Delete an `Observation` entity by ID.
    """

    try:
        await sensorthings_service.delete_observation(entity_id=entity_id, context=request)
    except Exception as e:
        raise http_error(e)

    return 204, None
