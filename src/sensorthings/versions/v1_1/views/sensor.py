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
from sensorthings.versions.v1_1 import sta
from sensorthings.versions.v1_1 import sensorthings_service
from sensorthings.versions.v1_1.schemas import (
    CollectionQuery,
    EntityQuery,
    SensorCollectionResponse,
    SensorResponse,
    SensorPostBody,
    SensorPatchBody,
)
from sensorthings.versions.v1_1 import app_settings

router_definition = RouterDefinition(
    router=Router(tags=[str(sta.SENSORS)]),
    operations={}
)


async def get_sensor_collection(
    request: HttpRequest,
    query: Query[CollectionQuery],
) -> tuple[int, SensorCollectionResponse]:
    """
    Retrieve a collection of `Sensor` entities.
    """

    try:
        collection = await sensorthings_service.get_collection(
            entity_type=sta.SENSOR_ENTITY,
            context=request,
            **query.dict(exclude_unset=True)
        )
    except Exception as e:
        raise http_error(e)

    return 200, collection


router_definition.operations["get_sensor_collection"] = OperationDefinition(
    path=str(sta.SENSORS),
    methods=["GET"],
    view_func=get_sensor_collection,
    auth=app_settings.AUTH_HANDLERS.get(
        "get_sensor_collection", app_settings.DEFAULT_AUTH_HANDLER
    ),
    response={
        200: SensorCollectionResponse, **get_collection_error_responses
    }
)


async def create_sensor_entity(
    request: HttpRequest, response: HttpResponse, payload: SensorPostBody
) -> tuple[int, None]:
    """
    Create a new `Sensor` entity.
    """

    try:
        entity = await sensorthings_service.create_entity(
            entity_type=sta.SENSOR_ENTITY,
            payload=payload.dict(exclude_unset=True),
            context=request
        )
        response.headers["Location"] = entity["iot_self_link"]
    except Exception as e:
        raise http_error(e)

    return 201, None


router_definition.operations["create_sensor_entity"] = OperationDefinition(
    path=str(sta.SENSORS),
    methods=["POST"],
    view_func=create_sensor_entity,
    auth=app_settings.AUTH_HANDLERS.get(
        "create_sensor_entity", app_settings.DEFAULT_AUTH_HANDLER
    ),
    response={
        201: None, **create_entity_error_responses
    }
)


async def get_sensor_entity(
    request: HttpRequest,
    query: Query[EntityQuery],
    entity_id: Path[app_settings.ID_TYPE],
) -> tuple[int, SensorResponse]:
    """
    Retrieve a single `Sensor` entity by ID.
    """

    try:
        entity = await sensorthings_service.get_entity(
            entity_type=sta.SENSOR_ENTITY,
            entity_id=entity_id,
            context=request,
            **query.dict(exclude_unset=True)
        )
    except Exception as e:
        raise http_error(e)

    return 200, entity


router_definition.operations["get_sensor_entity"] = OperationDefinition(
    path=f"{str(sta.SENSORS)}({app_settings.ID_DELIMITER}{{entity_id}}{app_settings.ID_DELIMITER})",
    methods=["GET"],
    view_func=get_sensor_entity,
    auth=app_settings.AUTH_HANDLERS.get(
        "get_sensor_entity", app_settings.DEFAULT_AUTH_HANDLER
    ),
    response={
        200: SensorResponse, **get_entity_error_responses
    }
)


async def update_sensor_entity(
    request: HttpRequest,
    entity_id: Path[app_settings.ID_TYPE],
    payload: SensorPatchBody,
) -> tuple[int, None]:
    """
    Update an existing `Sensor` entity.
    """

    try:
        await sensorthings_service.update_entity(
            entity_type=sta.SENSOR_ENTITY,
            entity_id=entity_id,
            payload=payload.dict(exclude_unset=True),
            context=request
        )
    except Exception as e:
        raise http_error(e)

    return 204, None


router_definition.operations["update_sensor_entity"] = OperationDefinition(
    path=f"{str(sta.SENSORS)}({app_settings.ID_DELIMITER}{{entity_id}}{app_settings.ID_DELIMITER})",
    methods=["PATCH"],
    view_func=update_sensor_entity,
    auth=app_settings.AUTH_HANDLERS.get(
        "update_sensor_entity", app_settings.DEFAULT_AUTH_HANDLER
    ),
    response={
        204: None, **update_entity_error_responses
    }
)


async def delete_sensor_entity(
    request: HttpRequest,
    entity_id: Path[app_settings.ID_TYPE],
) -> tuple[int, None]:
    """
    Delete a `Sensor` entity by ID.
    """

    try:
        await sensorthings_service.delete_entity(
            entity_type=sta.SENSOR_ENTITY,
            entity_id=entity_id,
            context=request
        )
    except Exception as e:
        raise http_error(e)

    return 204, None


router_definition.operations["delete_sensor_entity"] = OperationDefinition(
    path=f"{str(sta.SENSORS)}({app_settings.ID_DELIMITER}{{entity_id}}{app_settings.ID_DELIMITER})",
    methods=["DELETE"],
    view_func=delete_sensor_entity,
    auth=app_settings.AUTH_HANDLERS.get(
        "delete_sensor_entity", app_settings.DEFAULT_AUTH_HANDLER
    ),
    response={
        204: None, **delete_entity_error_responses
    }
)
