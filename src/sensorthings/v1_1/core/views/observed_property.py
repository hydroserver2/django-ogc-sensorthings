from ninja import Router, Path, Query
from django.http import HttpRequest, HttpResponse
from sensorthings.v1_1.core import iot
from sensorthings.v1_1.core.service import sensorthings_service
from sensorthings.v1_1.core.schemas import (
    CollectionQuery,
    EntityQuery,
    ObservedPropertyCollectionResponse,
    ObservedPropertyResponse,
    ObservedPropertyPostBody,
    ObservedPropertyPatchBody,
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

router = Router(tags=[iot.OBSERVED_PROPERTIES])


@router.get(
    iot.OBSERVED_PROPERTIES,
    auth=app_settings.AUTH_HANDLERS.get(
        "get_observed_property_collection", app_settings.DEFAULT_AUTH_HANDLER
    ),
    response={
        200: ObservedPropertyCollectionResponse,
        **get_collection_error_responses,
    },
    by_alias=True,
    exclude_none=True,
    exclude_unset=True,
)
async def get_observed_property_collection(
    request: HttpRequest,
    query: Query[CollectionQuery],
) -> tuple[int, ObservedPropertyCollectionResponse]:
    """
    Retrieve a collection of `ObservedProperty` entities.
    """
    try:
        resource = await sensorthings_service.get_observed_property_collection(
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
    iot.OBSERVED_PROPERTIES,
    auth=app_settings.AUTH_HANDLERS.get(
        "create_observed_property", app_settings.DEFAULT_AUTH_HANDLER
    ),
    response={201: None, **create_entity_error_responses},
)
async def create_observed_property(
    request: HttpRequest,
    response: HttpResponse,
    entity: ObservedPropertyPostBody,
) -> tuple[int, None]:
    """
    Create a new `ObservedProperty` entity.
    """

    try:
        resource = await sensorthings_service.create_observed_property(
            entity=entity, context=request
        )
        response.headers["Location"] = resource.iot_self_link
    except Exception as e:
        raise http_error(e)

    return 201, None


@router.get(
    f"{iot.OBSERVED_PROPERTIES}({app_settings.ID_DELIMITER}{{entity_id}}{app_settings.ID_DELIMITER})",
    auth=app_settings.AUTH_HANDLERS.get(
        "get_observed_property", app_settings.DEFAULT_AUTH_HANDLER
    ),
    response={200: ObservedPropertyResponse, **get_entity_error_responses},
    by_alias=True,
    exclude_none=True,
    exclude_unset=True,
)
async def get_observed_property(
    request: HttpRequest,
    query: Query[EntityQuery],
    entity_id: Path[app_settings.ID_TYPE],
) -> tuple[int, ObservedPropertyResponse]:
    """
    Retrieve a single `ObservedProperty` entity by ID.
    """

    try:
        resource = await sensorthings_service.get_observed_property(
            entity_id=entity_id,
            select=query.select,
            expand=query.expand,
            context=request,
        )
    except Exception as e:
        raise http_error(e)

    return 200, resource


@router.patch(
    f"{iot.OBSERVED_PROPERTIES}({app_settings.ID_DELIMITER}{{entity_id}}{app_settings.ID_DELIMITER})",
    auth=app_settings.AUTH_HANDLERS.get(
        "update_observed_property", app_settings.DEFAULT_AUTH_HANDLER
    ),
    response={204: None, **update_entity_error_responses},
)
async def update_observed_property(
    request: HttpRequest,
    entity_id: Path[app_settings.ID_TYPE],
    entity: ObservedPropertyPatchBody,
) -> tuple[int, None]:
    """
    Update an existing `ObservedProperty` entity.
    """

    try:
        await sensorthings_service.update_observed_property(
            entity_id=entity_id, entity=entity, context=request
        )
    except Exception as e:
        raise http_error(e)

    return 204, None


@router.delete(
    f"{iot.OBSERVED_PROPERTIES}({app_settings.ID_DELIMITER}{{entity_id}}{app_settings.ID_DELIMITER})",
    auth=app_settings.AUTH_HANDLERS.get(
        "delete_observed_property", app_settings.DEFAULT_AUTH_HANDLER
    ),
    response={204: None, **delete_entity_error_responses},
)
async def delete_observed_property(
    request: HttpRequest,
    entity_id: Path[app_settings.ID_TYPE],
) -> tuple[int, None]:
    """
    Delete an `ObservedProperty` entity by ID.
    """

    try:
        await sensorthings_service.delete_observed_property(
            entity_id=entity_id, context=request
        )
    except Exception as e:
        raise http_error(e)

    return 204, None
