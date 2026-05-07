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
    ThingCollectionResponse,
    ThingResponse,
    ThingPostBody,
    ThingPatchBody,
)


router_definition = RouterDefinition(
    router=Router(tags=[str(STA.THINGS)]),
    operations={}
)


async def get_thing_collection(
    request: HttpRequest,
    query: Query[CollectionQuery],
) -> tuple[int, ThingCollectionResponse]:
    """
    Retrieve a collection of `Thing` entities.
    """

    try:
        collection = await sensorthings_service.get_collection(
            entity_type=STA.THING_ENTITY,
            context=request,
            **query.dict(exclude_unset=True)
        )
    except Exception as e:
        raise http_error(e)

    return 200, collection


router_definition.operations["get_thing_collection"] = OperationDefinition(
    path=str(STA.THINGS),
    methods=["GET"],
    view_func=get_thing_collection,
    auth=app_settings.AUTH_HANDLERS.get(
        "get_thing_collection", app_settings.DEFAULT_AUTH_HANDLER
    ),
    response={
        200: ThingCollectionResponse, **get_collection_error_responses
    }
)


async def create_thing_entity(
    request: HttpRequest, response: HttpResponse, payload: ThingPostBody
) -> tuple[int, None]:
    """
    Create a new `Thing` entity.
    """

    try:
        entity = await sensorthings_service.create_entity(
            entity_type=STA.THING_ENTITY,
            payload=payload.dict(exclude_unset=True),
            context=request
        )
        response.headers["Location"] = entity["iot_self_link"]
    except Exception as e:
        raise http_error(e)

    return 201, None


router_definition.operations["create_thing_entity"] = OperationDefinition(
    path=str(STA.THINGS),
    methods=["POST"],
    view_func=create_thing_entity,
    auth=app_settings.AUTH_HANDLERS.get(
        "create_thing_entity", app_settings.DEFAULT_AUTH_HANDLER
    ),
    response={
        201: None, **create_entity_error_responses
    }
)


async def get_thing_entity(
    request: HttpRequest,
    query: Query[EntityQuery],
    entity_id: Path[app_settings.ID_TYPE],
) -> tuple[int, ThingResponse]:
    """
    Retrieve a single `Thing` entity by ID.
    """

    try:
        resource = await sensorthings_service.get_entity(
            entity_type=STA.THING_ENTITY,
            entity_id=entity_id,
            context=request,
            **query.dict(exclude_unset=True)
        )
    except Exception as e:
        raise http_error(e)

    return 200, resource


router_definition.operations["get_thing_entity"] = OperationDefinition(
    path=f"{str(STA.THINGS)}({app_settings.ID_DELIMITER}{{entity_id}}{app_settings.ID_DELIMITER})",
    methods=["GET"],
    view_func=get_thing_entity,
    auth=app_settings.AUTH_HANDLERS.get(
        "get_thing_entity", app_settings.DEFAULT_AUTH_HANDLER
    ),
    response={
        200: ThingResponse, **get_entity_error_responses
    }
)


async def update_thing_entity(
    request: HttpRequest,
    entity_id: Path[app_settings.ID_TYPE],
    payload: ThingPatchBody,
) -> tuple[int, None]:
    """
    Update an existing `Thing` entity.
    """

    try:
        await sensorthings_service.update_entity(
            entity_type=STA.THING_ENTITY,
            entity_id=entity_id,
            payload=payload.dict(exclude_unset=True),
            context=request
        )
    except Exception as e:
        raise http_error(e)

    return 204, None


router_definition.operations["update_thing_entity"] = OperationDefinition(
    path=f"{str(STA.THINGS)}({app_settings.ID_DELIMITER}{{entity_id}}{app_settings.ID_DELIMITER})",
    methods=["PATCH"],
    view_func=update_thing_entity,
    auth=app_settings.AUTH_HANDLERS.get(
        "update_thing_entity", app_settings.DEFAULT_AUTH_HANDLER
    ),
    response={
        204: None, **update_entity_error_responses
    }
)


async def delete_thing_entity(
    request: HttpRequest,
    entity_id: Path[app_settings.ID_TYPE],
) -> tuple[int, None]:
    """
    Delete a `Thing` entity by ID.
    """

    try:
        await sensorthings_service.delete_entity(
            entity_type=STA.THING_ENTITY,
            entity_id=entity_id,
            context=request
        )
    except Exception as e:
        raise http_error(e)

    return 204, None


router_definition.operations["delete_thing_entity"] = OperationDefinition(
    path=f"{str(STA.THINGS)}({app_settings.ID_DELIMITER}{{entity_id}}{app_settings.ID_DELIMITER})",
    methods=["DELETE"],
    view_func=delete_thing_entity,
    auth=app_settings.AUTH_HANDLERS.get(
        "delete_thing_entity", app_settings.DEFAULT_AUTH_HANDLER
    ),
    response={
        204: None, **delete_entity_error_responses
    }
)
