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
)
from sensorthings.versions.v1_1 import app_settings
from ..schemas import (
    MultiDatastreamCollectionResponse,
    MultiDatastreamResponse,
    MultiDatastreamPostBody,
    MultiDatastreamPatchBody,
)

router_definition = RouterDefinition(
    router=Router(tags=[str(sta.MULTI_DATASTREAMS)]),
    operations={}
)


async def get_multi_datastream_collection(
    request: HttpRequest,
    query: Query[CollectionQuery],
) -> tuple[int, MultiDatastreamCollectionResponse]:
    """
    Retrieve a collection of `MultiDatastream` entities.
    """

    try:
        collection = await sensorthings_service.get_collection(
            entity_type=sta.MULTI_DATASTREAM_ENTITY,
            filters=query.filters,
            count=query.count,
            orderby=query.orderby,
            skip=query.skip,
            top=query.top,
            select=query.select,
            expand=query.expand,
            context=request,
        )
    except Exception as e:
        raise http_error(e)

    return 200, collection


router_definition.operations["get_multi_datastream_collection"] = OperationDefinition(
    path=str(sta.MULTI_DATASTREAMS),
    methods=["GET"],
    view_func=get_multi_datastream_collection,
    auth=app_settings.AUTH_HANDLERS.get(
        "get_multi_datastream_collection", app_settings.DEFAULT_AUTH_HANDLER
    ),
    response={
        200: MultiDatastreamCollectionResponse, **get_collection_error_responses
    }
)


async def create_multi_datastream_entity(
    request: HttpRequest, response: HttpResponse, payload: MultiDatastreamPostBody
) -> tuple[int, None]:
    """
    Create a new `MultiDatastream` entity.
    """

    try:
        entity = await sensorthings_service.create_entity(
            entity_type=sta.MULTI_DATASTREAM_ENTITY,
            payload=payload,
            context=request
        )
        response.headers["Location"] = entity.iot_self_link
    except Exception as e:
        raise http_error(e)

    return 201, None


router_definition.operations["create_multi_datastream_entity"] = OperationDefinition(
    path=str(sta.MULTI_DATASTREAMS),
    methods=["POST"],
    view_func=create_multi_datastream_entity,
    auth=app_settings.AUTH_HANDLERS.get(
        "create_multi_datastream_entity", app_settings.DEFAULT_AUTH_HANDLER
    ),
    response={
        201: None, **create_entity_error_responses
    }
)


async def get_multi_datastream_entity(
    request: HttpRequest,
    query: Query[EntityQuery],
    entity_id: Path[app_settings.ID_TYPE],
) -> tuple[int, MultiDatastreamResponse]:
    """
    Retrieve a single `MultiDatastream` entity by ID.
    """

    try:
        entity = await sensorthings_service.get_entity_type(
            entity_type=sta.MULTI_DATASTREAM_ENTITY,
            entity_id=entity_id,
            select=query.select,
            expand=query.expand,
            context=request,
        )
    except Exception as e:
        raise http_error(e)

    return 200, entity


router_definition.operations["get_multi_datastream_entity"] = OperationDefinition(
    path=f"{str(sta.MULTI_DATASTREAMS)}({app_settings.ID_DELIMITER}{{entity_id}}{app_settings.ID_DELIMITER})",
    methods=["GET"],
    view_func=get_multi_datastream_entity,
    auth=app_settings.AUTH_HANDLERS.get(
        "get_multi_datastream_entity", app_settings.DEFAULT_AUTH_HANDLER
    ),
    response={
        200: MultiDatastreamResponse, **get_entity_error_responses
    }
)


async def update_multi_datastream_entity(
    request: HttpRequest,
    entity_id: Path[app_settings.ID_TYPE],
    payload: MultiDatastreamPatchBody,
) -> tuple[int, None]:
    """
    Update an existing `MultiDatastream` entity.
    """

    try:
        await sensorthings_service.update_entity(
            entity_id=entity_id, payload=payload, context=request
        )
    except Exception as e:
        raise http_error(e)

    return 204, None


router_definition.operations["update_multi_datastream_entity"] = OperationDefinition(
    path=f"{str(sta.MULTI_DATASTREAMS)}({app_settings.ID_DELIMITER}{{entity_id}}{app_settings.ID_DELIMITER})",
    methods=["PATCH"],
    view_func=update_multi_datastream_entity,
    auth=app_settings.AUTH_HANDLERS.get(
        "update_multi_datastream_entity", app_settings.DEFAULT_AUTH_HANDLER
    ),
    response={
        204: None, **update_entity_error_responses
    }
)


async def delete_multi_datastream_entity(
    request: HttpRequest,
    entity_id: Path[app_settings.ID_TYPE],
) -> tuple[int, None]:
    """
    Delete a `MultiDatastream` entity by ID.
    """

    try:
        await sensorthings_service.delete_entity(
            entity_type=sta.MULTI_DATASTREAM_ENTITY,
            entity_id=entity_id,
            context=request
        )
    except Exception as e:
        raise http_error(e)

    return 204, None


router_definition.operations["delete_multi_datastream_entity"] = OperationDefinition(
    path=f"{str(sta.MULTI_DATASTREAMS)}({app_settings.ID_DELIMITER}{{entity_id}}{app_settings.ID_DELIMITER})",
    methods=["DELETE"],
    view_func=delete_multi_datastream_entity,
    auth=app_settings.AUTH_HANDLERS.get(
        "delete_multi_datastream_entity", app_settings.DEFAULT_AUTH_HANDLER
    ),
    response={
        204: None, **delete_entity_error_responses
    }
)
