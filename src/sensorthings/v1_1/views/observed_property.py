from ninja import Router, Path, Query
from django.http import HttpRequest, HttpResponse
from sensorthings.v1_1.protocol import sta
from sensorthings.v1_1.service import sensorthings_service
from sensorthings.v1_1.schemas import (
    CollectionQuery,
    EntityQuery,
    ObservedPropertyCollectionResponse,
    ObservedPropertyResponse,
    ObservedPropertyPostBody,
    ObservedPropertyPatchBody,
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
    router=Router(tags=[str(sta.OBSERVED_PROPERTIES)]),
    operations={}
)


async def get_observed_property_collection(
    request: HttpRequest,
    query: Query[CollectionQuery],
) -> tuple[int, ObservedPropertyCollectionResponse]:
    """
    Retrieve a collection of `ObservedProperty` entities.
    """

    try:
        resource = await sensorthings_service.get_collection(
            entity_type=sta.OBSERVED_PROPERTY_ENTITY,
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

    return 200, resource


router_definition.operations["get_observed_property_collection"] = OperationDefinition(
    path=str(sta.OBSERVED_PROPERTIES),
    methods=["GET"],
    view_func=get_observed_property_collection,
    auth=app_settings.AUTH_HANDLERS.get(
        "get_observed_property_collection", app_settings.DEFAULT_AUTH_HANDLER
    ),
    response={
        200: ObservedPropertyCollectionResponse, **get_collection_error_responses
    }
)


async def create_observed_property_entity(
    request: HttpRequest, response: HttpResponse, payload: ObservedPropertyPostBody
) -> tuple[int, None]:
    """
    Create a new `ObservedProperty` entity.
    """

    try:
        entity = await sensorthings_service.create_entity(
            entity_type=sta.OBSERVED_PROPERTY_ENTITY,
            payload=payload,
            context=request
        )
        response.headers["ObservedProperty"] = entity.iot_self_link
    except Exception as e:
        raise http_error(e)

    return 201, None


router_definition.operations["create_observed_property_entity"] = OperationDefinition(
    path=str(sta.OBSERVED_PROPERTIES),
    methods=["POST"],
    view_func=create_observed_property_entity,
    auth=app_settings.AUTH_HANDLERS.get(
        "create_observed_property_entity", app_settings.DEFAULT_AUTH_HANDLER
    ),
    response={
        201: None, **create_entity_error_responses
    }
)


async def get_observed_property_entity(
    request: HttpRequest,
    query: Query[EntityQuery],
    entity_id: Path[app_settings.ID_TYPE],
) -> tuple[int, ObservedPropertyResponse]:
    """
    Retrieve a single `ObservedProperty` entity by ID.
    """

    try:
        entity = await sensorthings_service.get_entity_type(
            entity_type=sta.OBSERVED_PROPERTY_ENTITY,
            entity_id=entity_id,
            select=query.select,
            expand=query.expand,
            context=request,
        )
    except Exception as e:
        raise http_error(e)

    return 200, entity


router_definition.operations["get_observed_property_entity"] = OperationDefinition(
    path=f"{str(sta.OBSERVED_PROPERTIES)}({app_settings.ID_DELIMITER}{{entity_id}}{app_settings.ID_DELIMITER})",
    methods=["GET"],
    view_func=get_observed_property_entity,
    auth=app_settings.AUTH_HANDLERS.get(
        "get_observed_property_entity", app_settings.DEFAULT_AUTH_HANDLER
    ),
    response={
        200: ObservedPropertyResponse, **get_entity_error_responses
    }
)


async def update_observed_property_entity(
    request: HttpRequest,
    entity_id: Path[app_settings.ID_TYPE],
    payload: ObservedPropertyPatchBody,
) -> tuple[int, None]:
    """
    Update an existing `ObservedProperty` entity.
    """

    try:
        await sensorthings_service.update_entity(
            entity_type=sta.OBSERVED_PROPERTY_ENTITY,
            entity_id=entity_id,
            payload=payload,
            context=request
        )
    except Exception as e:
        raise http_error(e)

    return 204, None


router_definition.operations["update_observed_property_entity"] = OperationDefinition(
    path=f"{str(sta.OBSERVED_PROPERTIES)}({app_settings.ID_DELIMITER}{{entity_id}}{app_settings.ID_DELIMITER})",
    methods=["PATCH"],
    view_func=update_observed_property_entity,
    auth=app_settings.AUTH_HANDLERS.get(
        "update_observed_property_entity", app_settings.DEFAULT_AUTH_HANDLER
    ),
    response={
        204: None, **update_entity_error_responses
    }
)


async def delete_observed_property_entity(
    request: HttpRequest,
    entity_id: Path[app_settings.ID_TYPE],
) -> tuple[int, None]:
    """
    Delete a `ObservedProperty` entity by ID.
    """

    try:
        await sensorthings_service.delete_entity(
            entity_type=sta.OBSERVED_PROPERTY_ENTITY,
            entity_id=entity_id,
            context=request
        )
    except Exception as e:
        raise http_error(e)

    return 204, None


router_definition.operations["delete_observed_property_entity"] = OperationDefinition(
    path=f"{str(sta.OBSERVED_PROPERTIES)}({app_settings.ID_DELIMITER}{{entity_id}}{app_settings.ID_DELIMITER})",
    methods=["DELETE"],
    view_func=delete_observed_property_entity,
    auth=app_settings.AUTH_HANDLERS.get(
        "delete_observed_property_entity", app_settings.DEFAULT_AUTH_HANDLER
    ),
    response={
        204: None, **delete_entity_error_responses
    }
)
