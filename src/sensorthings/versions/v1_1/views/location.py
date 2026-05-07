from ninja import Router, Path, Query
from django.http import HttpRequest, HttpResponse
from sensorthings.http import (
    RouterDefinition,
    OperationDefinition,
    get_collection_error_responses,
    get_entity_error_responses,
    create_entity_error_responses,
    update_entity_error_responses,
    delete_entity_error_responses,
    http_error,
)
from sensorthings.versions.v1_1 import STA, app_settings, sensorthings_service

from sensorthings.versions.v1_1.schemas import (
    CollectionQuery,
    EntityQuery,
    LocationCollectionResponse,
    LocationResponse,
    LocationPostBody,
    LocationPatchBody,
)


router_definition = RouterDefinition(
    router=Router(tags=[str(STA.LOCATIONS)]),
    operations={}
)


async def get_location_collection(
    request: HttpRequest,
    query: Query[CollectionQuery],
) -> tuple[int, LocationCollectionResponse]:
    """
    Retrieve a collection of `Location` entities.
    """

    try:
        collection = await sensorthings_service.get_collection(
            entity_type=STA.LOCATION_ENTITY,
            context=request,
            **query.dict(exclude_unset=True)
        )
    except Exception as e:
        raise http_error(e)

    return 200, collection


router_definition.operations["get_location_collection"] = OperationDefinition(
    path=str(STA.LOCATIONS),
    methods=["GET"],
    view_func=get_location_collection,
    auth=app_settings.AUTH_HANDLERS.get(
        "get_location_collection", app_settings.DEFAULT_AUTH_HANDLER
    ),
    response={
        200: LocationCollectionResponse, **get_collection_error_responses
    }
)


async def create_location_entity(
    request: HttpRequest, response: HttpResponse, payload: LocationPostBody
) -> tuple[int, None]:
    """
    Create a new `Location` entity.
    """

    try:
        entity = await sensorthings_service.create_entity(
            entity_type=STA.LOCATION_ENTITY,
            payload=payload.dict(exclude_unset=True),
            context=request
        )
        response.headers["Location"] = entity["iot_self_link"]
    except Exception as e:
        raise http_error(e)

    return 201, None


router_definition.operations["create_location_entity"] = OperationDefinition(
    path=str(STA.LOCATIONS),
    methods=["POST"],
    view_func=create_location_entity,
    auth=app_settings.AUTH_HANDLERS.get(
        "create_location_entity", app_settings.DEFAULT_AUTH_HANDLER
    ),
    response={
        201: None, **create_entity_error_responses
    }
)


async def get_location_entity(
    request: HttpRequest,
    query: Query[EntityQuery],
    entity_id: Path[app_settings.ID_TYPE],
) -> tuple[int, LocationResponse]:
    """
    Retrieve a single `Location` entity by ID.
    """

    try:
        entity = await sensorthings_service.get_entity(
            entity_type=STA.LOCATION_ENTITY,
            entity_id=entity_id,
            context=request,
            **query.dict(exclude_unset=True)
        )
    except Exception as e:
        raise http_error(e)

    return 200, entity


router_definition.operations["get_location_entity"] = OperationDefinition(
    path=f"{str(STA.LOCATIONS)}({app_settings.ID_DELIMITER}{{entity_id}}{app_settings.ID_DELIMITER})",
    methods=["GET"],
    view_func=get_location_entity,
    auth=app_settings.AUTH_HANDLERS.get(
        "get_location_entity", app_settings.DEFAULT_AUTH_HANDLER
    ),
    response={
        200: LocationResponse, **get_entity_error_responses
    }
)


async def update_location_entity(
    request: HttpRequest,
    entity_id: Path[app_settings.ID_TYPE],
    payload: LocationPatchBody,
) -> tuple[int, None]:
    """
    Update an existing `Location` entity.
    """

    try:
        await sensorthings_service.update_entity(
            entity_type=STA.LOCATION_ENTITY,
            entity_id=entity_id,
            payload=payload,
            context=request
        )
    except Exception as e:
        raise http_error(e)

    return 204, None


router_definition.operations["update_location_entity"] = OperationDefinition(
    path=f"{str(STA.LOCATIONS)}({app_settings.ID_DELIMITER}{{entity_id}}{app_settings.ID_DELIMITER})",
    methods=["PATCH"],
    view_func=update_location_entity,
    auth=app_settings.AUTH_HANDLERS.get(
        "update_location_entity", app_settings.DEFAULT_AUTH_HANDLER
    ),
    response={
        204: None, **update_entity_error_responses
    }
)


async def delete_location_entity(
    request: HttpRequest,
    entity_id: Path[app_settings.ID_TYPE],
) -> tuple[int, None]:
    """
    Delete a `Location` entity by ID.
    """

    try:
        await sensorthings_service.delete_entity(
            entity_type=STA.LOCATION_ENTITY,
            entity_id=entity_id,
            context=request
        )
    except Exception as e:
        raise http_error(e)

    return 204, None


router_definition.operations["delete_location_entity"] = OperationDefinition(
    path=f"{str(STA.LOCATIONS)}({app_settings.ID_DELIMITER}{{entity_id}}{app_settings.ID_DELIMITER})",
    methods=["DELETE"],
    view_func=delete_location_entity,
    auth=app_settings.AUTH_HANDLERS.get(
        "delete_location_entity", app_settings.DEFAULT_AUTH_HANDLER
    ),
    response={
        204: None, **delete_entity_error_responses
    }
)
