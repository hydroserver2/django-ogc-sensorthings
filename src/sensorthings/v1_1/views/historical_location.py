from ninja import Router, Path, Query
from django.http import HttpRequest, HttpResponse
from sensorthings.v1_1.protocol import sta
from sensorthings.v1_1.service import sensorthings_service
from sensorthings.v1_1.schemas import (
    CollectionQuery,
    EntityQuery,
    HistoricalLocationCollectionResponse,
    HistoricalLocationResponse,
    HistoricalLocationPostBody,
    HistoricalLocationPatchBody,
)
from sensorthings.v1_1.http import (
    RouterDefinition,
    OperationDefinition,
    get_collection_error_responses,
    get_entity_error_responses,
    create_entity_error_responses,
    update_entity_error_responses,
    delete_entity_error_responses,
    http_error,
)
from sensorthings.v1_1.conf import app_settings

router_definition = RouterDefinition(
    router=Router(tags=[str(sta.HISTORICAL_LOCATIONS)]),
    operations={}
)


async def get_historical_location_collection(
    request: HttpRequest,
    query: Query[CollectionQuery],
) -> tuple[int, HistoricalLocationCollectionResponse]:
    """
    Retrieve a collection of `HistoricalLocation` entities.
    """

    try:
        collection = await sensorthings_service.get_collection(
            entity_type=sta.HISTORICAL_LOCATION_ENTITY,
            filters=query.filters,
            count=query.count,
            order_by=query.order_by,
            skip=query.skip,
            top=query.top,
            select=query.select,
            expand=query.expand,
            context=request,
        )
    except Exception as e:
        raise http_error(e)

    return 200, collection


router_definition.operations["get_historical_location_collection"] = OperationDefinition(
    path=str(sta.HISTORICAL_LOCATIONS),
    methods=["GET"],
    view_func=get_historical_location_collection,
    auth=app_settings.AUTH_HANDLERS.get(
        "get_historical_location_collection", app_settings.DEFAULT_AUTH_HANDLER
    ),
    response={
        200: HistoricalLocationCollectionResponse, **get_collection_error_responses
    }
)


async def create_historical_location_entity(
    request: HttpRequest, response: HttpResponse, payload: HistoricalLocationPostBody
) -> tuple[int, None]:
    """
    Create a new `HistoricalLocation` entity.
    """

    try:
        entity = await sensorthings_service.create_entity(
            entity_type=sta.HISTORICAL_LOCATION_ENTITY,
            payload=payload,
            context=request
        )
        response.headers["Location"] = entity.iot_self_link
    except Exception as e:
        raise http_error(e)

    return 201, None


router_definition.operations["create_historical_location_entity"] = OperationDefinition(
    path=str(sta.HISTORICAL_LOCATIONS),
    methods=["POST"],
    view_func=create_historical_location_entity,
    auth=app_settings.AUTH_HANDLERS.get(
        "create_historical_location_entity", app_settings.DEFAULT_AUTH_HANDLER
    ),
    response={
        201: None, **create_entity_error_responses
    }
)


async def get_historical_location_entity(
    request: HttpRequest,
    query: Query[EntityQuery],
    entity_id: Path[app_settings.ID_TYPE],
) -> tuple[int, HistoricalLocationResponse]:
    """
    Retrieve a single `HistoricalLocation` entity by ID.
    """

    try:
        entity = await sensorthings_service.get_entity_type(
            entity_type=sta.HISTORICAL_LOCATION_ENTITY,
            entity_id=entity_id,
            select=query.select,
            expand=query.expand,
            context=request,
        )
    except Exception as e:
        raise http_error(e)

    return 200, entity


router_definition.operations["get_historical_location_entity"] = OperationDefinition(
    path=f"{str(sta.HISTORICAL_LOCATIONS)}({app_settings.ID_DELIMITER}{{entity_id}}{app_settings.ID_DELIMITER})",
    methods=["GET"],
    view_func=get_historical_location_entity,
    auth=app_settings.AUTH_HANDLERS.get(
        "get_historical_location_entity", app_settings.DEFAULT_AUTH_HANDLER
    ),
    response={
        200: HistoricalLocationResponse, **get_entity_error_responses
    }
)


async def update_historical_location_entity(
    request: HttpRequest,
    entity_id: Path[app_settings.ID_TYPE],
    payload: HistoricalLocationPatchBody,
) -> tuple[int, None]:
    """
    Update an existing `HistoricalLocation` entity.
    """

    try:
        await sensorthings_service.update_entity(
            entity_type=sta.HISTORICAL_LOCATION_ENTITY,
            entity_id=entity_id,
            payload=payload,
            context=request
        )
    except Exception as e:
        raise http_error(e)

    return 204, None


router_definition.operations["update_historical_location_entity"] = OperationDefinition(
    path=f"{str(sta.HISTORICAL_LOCATIONS)}({app_settings.ID_DELIMITER}{{entity_id}}{app_settings.ID_DELIMITER})",
    methods=["PATCH"],
    view_func=update_historical_location_entity,
    auth=app_settings.AUTH_HANDLERS.get(
        "update_historical_location_entity", app_settings.DEFAULT_AUTH_HANDLER
    ),
    response={
        204: None, **update_entity_error_responses
    }
)


async def delete_historical_location_entity(
    request: HttpRequest,
    entity_id: Path[app_settings.ID_TYPE],
) -> tuple[int, None]:
    """
    Delete a `HistoricalLocation` entity by ID.
    """

    try:
        await sensorthings_service.delete_entity(
            entity_type=sta.HISTORICAL_LOCATION_ENTITY,
            entity_id=entity_id,
            context=request
        )
    except Exception as e:
        raise http_error(e)

    return 204, None


router_definition.operations["delete_historical_location_entity"] = OperationDefinition(
    path=f"{str(sta.HISTORICAL_LOCATIONS)}({app_settings.ID_DELIMITER}{{entity_id}}{app_settings.ID_DELIMITER})",
    methods=["DELETE"],
    view_func=delete_historical_location_entity,
    auth=app_settings.AUTH_HANDLERS.get(
        "delete_historical_location_entity", app_settings.DEFAULT_AUTH_HANDLER
    ),
    response={
        204: None, **delete_entity_error_responses
    }
)
