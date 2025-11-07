from ninja import Router, Path, Query
from django.http import HttpRequest, HttpResponse
from sensorthings.v1_1.core import iot
from sensorthings.v1_1.core.service import sensorthings_service
from sensorthings.v1_1.core.schemas import (
    CollectionQuery,
    EntityQuery,
    SensorCollectionResponse,
    SensorResponse,
    SensorPostBody,
    SensorPatchBody,
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

router = Router(tags=[iot.SENSORS])


@router.get(
    iot.SENSORS,
    auth=app_settings.AUTH_HANDLERS.get(
        "get_sensor_collection", app_settings.DEFAULT_AUTH_HANDLER
    ),
    response={200: SensorCollectionResponse, **get_collection_error_responses},
    by_alias=True,
    exclude_none=True,
    exclude_unset=True,
)
async def get_sensor_collection(
    request: HttpRequest,
    query: Query[CollectionQuery],
) -> tuple[int, SensorCollectionResponse]:
    """
    Retrieve a collection of `Sensor` entities.
    """

    try:
        resource = await sensorthings_service.sensors.get_collection(
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
    iot.SENSORS,
    auth=app_settings.AUTH_HANDLERS.get(
        "create_sensor", app_settings.DEFAULT_AUTH_HANDLER
    ),
    response={201: None, **create_entity_error_responses},
)
async def create_sensor(
    request: HttpRequest,
    response: HttpResponse,
    entity: SensorPostBody,
) -> tuple[int, None]:
    """
    Create a new `Sensor` entity.
    """

    try:
        resource = await sensorthings_service.sensors.create_entity(entity=entity, context=request)
        response.headers["Location"] = resource.iot_self_link
    except Exception as e:
        raise http_error(e)

    return 201, None


@router.get(
    f"{iot.SENSORS}({app_settings.ID_DELIMITER}{{entity_id}}{app_settings.ID_DELIMITER})",
    auth=app_settings.AUTH_HANDLERS.get(
        "get_sensor", app_settings.DEFAULT_AUTH_HANDLER
    ),
    response={200: SensorResponse, **get_entity_error_responses},
    by_alias=True,
    exclude_none=True,
    exclude_unset=True,
)
async def get_sensor(
    request: HttpRequest,
    query: Query[EntityQuery],
    entity_id: Path[app_settings.ID_TYPE],
) -> tuple[int, SensorResponse]:
    """
    Retrieve a single `Sensor` entity by ID.
    """

    try:
        resource = await sensorthings_service.sensors.get_entity(
            entity_id=entity_id,
            select=query.select,
            expand=query.expand,
            context=request,
        )
    except Exception as e:
        raise http_error(e)

    return 200, resource


@router.patch(
    f"{iot.SENSORS}({app_settings.ID_DELIMITER}{{entity_id}}{app_settings.ID_DELIMITER})",
    auth=app_settings.AUTH_HANDLERS.get(
        "update_sensor", app_settings.DEFAULT_AUTH_HANDLER
    ),
    response={204: None, **update_entity_error_responses},
)
async def update_sensor(
    request: HttpRequest,
    entity_id: Path[app_settings.ID_TYPE],
    entity: SensorPatchBody,
) -> tuple[int, None]:
    """
    Update an existing `Sensor` entity.
    """

    try:
        await sensorthings_service.sensors.update_entity(
            entity_id=entity_id, entity=entity, context=request
        )
    except Exception as e:
        raise http_error(e)

    return 204, None


@router.delete(
    f"{iot.SENSORS}({app_settings.ID_DELIMITER}{{entity_id}}{app_settings.ID_DELIMITER})",
    auth=app_settings.AUTH_HANDLERS.get(
        "delete_sensor", app_settings.DEFAULT_AUTH_HANDLER
    ),
    response={204: None, **delete_entity_error_responses},
)
async def delete_sensor(
    request: HttpRequest,
    entity_id: Path[app_settings.ID_TYPE],
) -> tuple[int, None]:
    """
    Delete a `Sensor` entity by ID.
    """

    try:
        await sensorthings_service.sensors.delete_entity(entity_id=entity_id, context=request)
    except Exception as e:
        raise http_error(e)

    return 204, None
