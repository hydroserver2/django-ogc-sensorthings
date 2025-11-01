from ninja import Router, Path, Query
from django.http import HttpRequest, HttpResponse
from sensorthings.v1_1.core import iot
from sensorthings.v1_1.core.service import sensorthings_service
from sensorthings.v1_1.core.schemas import (
    CollectionQuery,
    EntityQuery,
    HistoricalLocationCollectionResponse,
    HistoricalLocationResponse,
    HistoricalLocationPostBody,
    HistoricalLocationPatchBody,
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

router = Router(tags=[iot.HISTORICAL_LOCATIONS])


@router.get(
    iot.HISTORICAL_LOCATIONS,
    auth=app_settings.AUTH_HANDLERS.get(
        "get_historical_location_collection", app_settings.DEFAULT_AUTH_HANDLER
    ),
    response={
        200: HistoricalLocationCollectionResponse,
        **get_collection_error_responses,
    },
    by_alias=True,
    exclude_none=True,
    exclude_unset=True,
)
async def get_historical_location_collection(
    request: HttpRequest,
    query: Query[CollectionQuery],
) -> tuple[int, HistoricalLocationCollectionResponse]:
    """
    Retrieve a collection of `HistoricalLocation` entities.
    """

    try:
        resource = await sensorthings_service.get_historical_location_collection(
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
    iot.HISTORICAL_LOCATIONS,
    auth=app_settings.AUTH_HANDLERS.get(
        "create_historical_location", app_settings.DEFAULT_AUTH_HANDLER
    ),
    response={201: None, **create_entity_error_responses},
)
async def create_historical_location(
    request: HttpRequest, response: HttpResponse, entity: HistoricalLocationPostBody
) -> tuple[int, None]:
    """
    Create a new `HistoricalLocation` entity.
    """

    try:
        resource = await sensorthings_service.create_historical_location(
            entity=entity, context=request
        )
        response.headers["Location"] = resource.iot_self_link
    except Exception as e:
        raise http_error(e)

    return 201, None


@router.get(
    f"{iot.HISTORICAL_LOCATIONS}({app_settings.ID_DELIMITER}{{entity_id}}{app_settings.ID_DELIMITER})",
    auth=app_settings.AUTH_HANDLERS.get(
        "get_historical_location", app_settings.DEFAULT_AUTH_HANDLER
    ),
    response={200: HistoricalLocationResponse, **get_entity_error_responses},
    by_alias=True,
    exclude_none=True,
    exclude_unset=True,
)
async def get_historical_location(
    request: HttpRequest,
    query: Query[EntityQuery],
    entity_id: Path[app_settings.ID_TYPE],
) -> tuple[int, HistoricalLocationResponse]:
    """
    Retrieve a single `HistoricalLocation` entity by ID.
    """

    try:
        resource = await sensorthings_service.get_historical_location(
            entity_id=entity_id,
            select=query.select,
            expand=query.expand,
            context=request,
        )
    except Exception as e:
        raise http_error(e)

    return 200, resource


@router.patch(
    f"{iot.HISTORICAL_LOCATIONS}({app_settings.ID_DELIMITER}{{entity_id}}{app_settings.ID_DELIMITER})",
    auth=app_settings.AUTH_HANDLERS.get(
        "update_historical_location", app_settings.DEFAULT_AUTH_HANDLER
    ),
    response={204: None, **update_entity_error_responses},
)
async def update_historical_location(
    request: HttpRequest,
    entity_id: Path[app_settings.ID_TYPE],
    entity: HistoricalLocationPatchBody,
) -> tuple[int, None]:
    """
    Update an existing `HistoricalLocation` entity.
    """

    try:
        await sensorthings_service.update_historical_location(
            entity_id=entity_id, entity=entity, context=request
        )
    except Exception as e:
        raise http_error(e)

    return 204, None


@router.delete(
    f"{iot.HISTORICAL_LOCATIONS}({app_settings.ID_DELIMITER}{{entity_id}}{app_settings.ID_DELIMITER})",
    auth=app_settings.AUTH_HANDLERS.get(
        "delete_historical_location", app_settings.DEFAULT_AUTH_HANDLER
    ),
    response={204: None, **delete_entity_error_responses},
)
async def delete_historical_location(
    request: HttpRequest,
    entity_id: Path[app_settings.ID_TYPE],
) -> tuple[int, None]:
    """
    Delete a `HistoricalLocation` entity by ID.
    """

    try:
        await sensorthings_service.delete_historical_location(
            entity_id=entity_id, context=request
        )
    except Exception as e:
        raise http_error(e)

    return 204, None
