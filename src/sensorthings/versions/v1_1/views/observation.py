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
    ObservationCollectionResponse,
    ObservationResponse,
    ObservationPostBody,
    ObservationPatchBody,
)


router_definition = RouterDefinition(
    router=Router(tags=[str(STA.OBSERVATIONS)]),
    operations={}
)


async def get_observation_collection(
    request: HttpRequest,
    query: Query[CollectionQuery],
) -> tuple[int, ObservationCollectionResponse]:
    """
    Retrieve a collection of `Observation` entities.
    """

    try:
        collection = await sensorthings_service.get_collection(
            entity_type=STA.OBSERVATION_ENTITY,
            context=request,
            **query.dict(exclude_unset=True)
        )
    except Exception as e:
        raise http_error(e)

    return 200, collection


router_definition.operations["get_observation_collection"] = OperationDefinition(
    path=str(STA.OBSERVATIONS),
    methods=["GET"],
    view_func=get_observation_collection,
    auth=app_settings.AUTH_HANDLERS.get(
        "get_observation_collection", app_settings.DEFAULT_AUTH_HANDLER
    ),
    response={
        200: ObservationCollectionResponse, **get_collection_error_responses
    }
)


async def create_observation_entity(
    request: HttpRequest, response: HttpResponse, payload: ObservationPostBody
) -> tuple[int, None]:
    """
    Create a new `Observation` entity.
    """

    try:
        entity = await sensorthings_service.create_entity(
            entity_type=STA.OBSERVATION_ENTITY,
            payload=payload.dict(exclude_unset=True),
            context=request
        )
        response.headers["Location"] = entity["iot_self_link"]
    except Exception as e:
        raise http_error(e)

    return 201, None


router_definition.operations["create_observation_entity"] = OperationDefinition(
    path=str(STA.OBSERVATIONS),
    methods=["POST"],
    view_func=create_observation_entity,
    auth=app_settings.AUTH_HANDLERS.get(
        "create_observation_entity", app_settings.DEFAULT_AUTH_HANDLER
    ),
    response={
        201: None, **create_entity_error_responses
    }
)


async def get_observation_entity(
    request: HttpRequest,
    query: Query[EntityQuery],
    entity_id: Path[app_settings.ID_TYPE],
) -> tuple[int, ObservationResponse]:
    """
    Retrieve a single `Observation` entity by ID.
    """

    try:
        entity = await sensorthings_service.get_entity(
            entity_type=STA.OBSERVATION_ENTITY,
            entity_id=entity_id,
            context=request,
            **query.dict(exclude_unset=True)
        )
    except Exception as e:
        raise http_error(e)

    return 200, entity


router_definition.operations["get_observation_entity"] = OperationDefinition(
    path=f"{str(STA.OBSERVATIONS)}({app_settings.ID_DELIMITER}{{entity_id}}{app_settings.ID_DELIMITER})",
    methods=["GET"],
    view_func=get_observation_entity,
    auth=app_settings.AUTH_HANDLERS.get(
        "get_observation_entity", app_settings.DEFAULT_AUTH_HANDLER
    ),
    response={
        200: ObservationResponse, **get_entity_error_responses
    }
)


async def update_observation_entity(
    request: HttpRequest,
    entity_id: Path[app_settings.ID_TYPE],
    payload: ObservationPatchBody,
) -> tuple[int, None]:
    """
    Update an existing `Observation` entity.
    """

    try:
        await sensorthings_service.update_entity(
            entity_type=STA.OBSERVATION_ENTITY,
            entity_id=entity_id,
            payload=payload.dict(exclude_unset=True),
            context=request
        )
    except Exception as e:
        raise http_error(e)

    return 204, None


router_definition.operations["update_observation_entity"] = OperationDefinition(
    path=f"{str(STA.OBSERVATIONS)}({app_settings.ID_DELIMITER}{{entity_id}}{app_settings.ID_DELIMITER})",
    methods=["PATCH"],
    view_func=update_observation_entity,
    auth=app_settings.AUTH_HANDLERS.get(
        "update_observation_entity", app_settings.DEFAULT_AUTH_HANDLER
    ),
    response={
        204: None, **update_entity_error_responses
    }
)


async def delete_observation_entity(
    request: HttpRequest,
    entity_id: Path[app_settings.ID_TYPE],
) -> tuple[int, None]:
    """
    Delete an `Observation` entity by ID.
    """

    try:
        await sensorthings_service.delete_entity(
            entity_type=STA.OBSERVATION_ENTITY,
            entity_id=entity_id,
            context=request
        )
    except Exception as e:
        raise http_error(e)

    return 204, None


router_definition.operations["delete_observation_entity"] = OperationDefinition(
    path=f"{str(STA.OBSERVATIONS)}({app_settings.ID_DELIMITER}{{entity_id}}{app_settings.ID_DELIMITER})",
    methods=["DELETE"],
    view_func=delete_observation_entity,
    auth=app_settings.AUTH_HANDLERS.get(
        "delete_observation_entity", app_settings.DEFAULT_AUTH_HANDLER
    ),
    response={
        204: None, **delete_entity_error_responses
    }
)
