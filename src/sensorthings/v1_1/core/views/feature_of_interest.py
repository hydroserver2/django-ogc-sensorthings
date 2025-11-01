from ninja import Router, Path, Query
from django.http import HttpRequest, HttpResponse
from sensorthings.v1_1.core import iot
from sensorthings.v1_1.core.service import sensorthings_service
from sensorthings.v1_1.core.schemas import (
    CollectionQuery,
    EntityQuery,
    FeatureOfInterestCollectionResponse,
    FeatureOfInterestResponse,
    FeatureOfInterestPostBody,
    FeatureOfInterestPatchBody,
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

router = Router(tags=[iot.FEATURES_OF_INTEREST])


@router.get(
    iot.FEATURES_OF_INTEREST,
    auth=app_settings.AUTH_HANDLERS.get(
        "get_feature_of_interest_collection", app_settings.DEFAULT_AUTH_HANDLER
    ),
    response={
        200: FeatureOfInterestCollectionResponse,
        **get_collection_error_responses,
    },
    by_alias=True,
    exclude_none=True,
    exclude_unset=True,
)
def get_feature_of_interest_collection(
    request: HttpRequest,
    query: Query[CollectionQuery],
) -> tuple[int, FeatureOfInterestCollectionResponse]:
    """
    Retrieve a collection of `FeatureOfInterest` entities.
    """

    try:
        resource = sensorthings_service.get_feature_of_interest_collection(
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
    iot.FEATURES_OF_INTEREST,
    auth=app_settings.AUTH_HANDLERS.get(
        "create_feature_of_interest", app_settings.DEFAULT_AUTH_HANDLER
    ),
    response={201: None, **create_entity_error_responses},
)
def create_feature_of_interest(
    request: HttpRequest, response: HttpResponse, entity: FeatureOfInterestPostBody
) -> tuple[int, None]:
    """
    Create a new `FeatureOfInterest` entity.
    """

    try:
        resource = sensorthings_service.create_feature_of_interest(
            entity=entity, context=request
        )
        response.headers["Location"] = resource.iot_self_link
    except Exception as e:
        raise http_error(e)

    return 201, None


@router.get(
    f"{iot.FEATURES_OF_INTEREST}({app_settings.ID_DELIMITER}{{entity_id}}{app_settings.ID_DELIMITER})",
    auth=app_settings.AUTH_HANDLERS.get(
        "get_feature_of_interest", app_settings.DEFAULT_AUTH_HANDLER
    ),
    response={200: FeatureOfInterestResponse, **get_entity_error_responses},
    by_alias=True,
    exclude_none=True,
    exclude_unset=True,
)
def get_feature_of_interest(
    request: HttpRequest,
    query: Query[EntityQuery],
    entity_id: Path[app_settings.ID_TYPE],
) -> tuple[int, FeatureOfInterestResponse]:
    """
    Retrieve a single `FeatureOfInterest` entity by ID.
    """

    try:
        resource = sensorthings_service.get_feature_of_interest(
            entity_id=entity_id,
            select=query.select,
            expand=query.expand,
            context=request,
        )
    except Exception as e:
        raise http_error(e)

    return 200, resource


@router.patch(
    f"{iot.FEATURES_OF_INTEREST}({app_settings.ID_DELIMITER}{{entity_id}}{app_settings.ID_DELIMITER})",
    auth=app_settings.AUTH_HANDLERS.get(
        "update_feature_of_interest", app_settings.DEFAULT_AUTH_HANDLER
    ),
    response={204: None, **update_entity_error_responses},
)
def update_feature_of_interest(
    request: HttpRequest,
    entity_id: Path[app_settings.ID_TYPE],
    entity: FeatureOfInterestPatchBody,
) -> tuple[int, None]:
    """
    Update an existing `FeatureOfInterest` entity.
    """

    try:
        sensorthings_service.update_feature_of_interest(
            entity_id=entity_id, entity=entity, context=request
        )
    except Exception as e:
        raise http_error(e)

    return 204, None


@router.delete(
    f"{iot.FEATURES_OF_INTEREST}({app_settings.ID_DELIMITER}{{entity_id}}{app_settings.ID_DELIMITER})",
    auth=app_settings.AUTH_HANDLERS.get(
        "delete_feature_of_interest", app_settings.DEFAULT_AUTH_HANDLER
    ),
    response={204: None, **delete_entity_error_responses},
)
def delete_feature_of_interest(
    request: HttpRequest,
    entity_id: Path[app_settings.ID_TYPE],
) -> tuple[int, None]:
    """
    Delete a `FeatureOfInterest` entity by ID.
    """

    try:
        sensorthings_service.delete_feature_of_interest(
            entity_id=entity_id, context=request
        )
    except Exception as e:
        raise http_error(e)

    return 204, None
