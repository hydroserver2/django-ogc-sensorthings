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
    FeatureOfInterestCollectionResponse,
    FeatureOfInterestResponse,
    FeatureOfInterestPostBody,
    FeatureOfInterestPatchBody,
)
from sensorthings.versions.v1_1 import app_settings

router_definition = RouterDefinition(
    router=Router(tags=[str(sta.FEATURES_OF_INTEREST)]),
    operations={}
)


async def get_feature_of_interest_collection(
    request: HttpRequest,
    query: Query[CollectionQuery],
) -> tuple[int, FeatureOfInterestCollectionResponse]:
    """
    Retrieve a collection of `FeatureOfInterest` entities.
    """

    try:
        collection = await sensorthings_service.get_collection(
            entity_type=sta.FEATURE_OF_INTEREST_ENTITY,
            context=request,
            **query.dict(exclude_unset=True)
        )
    except Exception as e:
        raise http_error(e)

    return 200, collection


router_definition.operations["get_feature_of_interest_collection"] = OperationDefinition(
    path=str(sta.FEATURES_OF_INTEREST),
    methods=["GET"],
    view_func=get_feature_of_interest_collection,
    auth=app_settings.AUTH_HANDLERS.get(
        "get_feature_of_interest_collection", app_settings.DEFAULT_AUTH_HANDLER
    ),
    response={
        200: FeatureOfInterestCollectionResponse, **get_collection_error_responses
    }
)


async def create_feature_of_interest_entity(
    request: HttpRequest, response: HttpResponse, payload: FeatureOfInterestPostBody
) -> tuple[int, None]:
    """
    Create a new `FeatureOfInterest` entity.
    """

    try:
        entity = await sensorthings_service.features_of_interest.create_entity(
            entity_type=sta.FEATURE_OF_INTEREST_ENTITY,
            payload=payload,
            context=request
        )
        response.headers["Location"] = entity.iot_self_link
    except Exception as e:
        raise http_error(e)

    return 201, None


router_definition.operations["create_feature_of_interest_entity"] = OperationDefinition(
    path=str(sta.FEATURES_OF_INTEREST),
    methods=["POST"],
    view_func=create_feature_of_interest_entity,
    auth=app_settings.AUTH_HANDLERS.get(
        "create_feature_of_interest_entity", app_settings.DEFAULT_AUTH_HANDLER
    ),
    response={
        201: None, **create_entity_error_responses
    }
)


async def get_feature_of_interest_entity(
    request: HttpRequest,
    query: Query[EntityQuery],
    entity_id: Path[app_settings.ID_TYPE],
) -> tuple[int, FeatureOfInterestResponse]:
    """
    Retrieve a single `FeatureOfInterest` entity by ID.
    """

    try:
        entity = await sensorthings_service.get_entity(
            entity_type=sta.FEATURE_OF_INTEREST_ENTITY,
            entity_id=entity_id,
            context=request,
            **query.dict(exclude_unset=True)
        )
    except Exception as e:
        raise http_error(e)

    return 200, entity


router_definition.operations["get_feature_of_interest_entity"] = OperationDefinition(
    path=f"{str(sta.FEATURES_OF_INTEREST)}({app_settings.ID_DELIMITER}{{entity_id}}{app_settings.ID_DELIMITER})",
    methods=["GET"],
    view_func=get_feature_of_interest_entity,
    auth=app_settings.AUTH_HANDLERS.get(
        "get_feature_of_interest_entity", app_settings.DEFAULT_AUTH_HANDLER
    ),
    response={
        200: FeatureOfInterestResponse, **get_entity_error_responses
    }
)


async def update_feature_of_interest_entity(
    request: HttpRequest,
    entity_id: Path[app_settings.ID_TYPE],
    payload: FeatureOfInterestPatchBody,
) -> tuple[int, None]:
    """
    Update an existing `FeatureOfInterest` entity.
    """

    try:
        await sensorthings_service.features_of_interest.update_entity(
            entity_type=sta.FEATURE_OF_INTEREST_ENTITY,
            entity_id=entity_id,
            payload=payload,
            context=request
        )
    except Exception as e:
        raise http_error(e)

    return 204, None


router_definition.operations["update_feature_of_interest_entity"] = OperationDefinition(
    path=f"{str(sta.FEATURES_OF_INTEREST)}({app_settings.ID_DELIMITER}{{entity_id}}{app_settings.ID_DELIMITER})",
    methods=["PATCH"],
    view_func=update_feature_of_interest_entity,
    auth=app_settings.AUTH_HANDLERS.get(
        "update_feature_of_interest_entity", app_settings.DEFAULT_AUTH_HANDLER
    ),
    response={
        204: None, **update_entity_error_responses
    }
)


async def delete_feature_of_interest_entity(
    request: HttpRequest,
    entity_id: Path[app_settings.ID_TYPE],
) -> tuple[int, None]:
    """
    Delete a `FeatureOfInterest` entity by ID.
    """

    try:
        await sensorthings_service.delete_entity(
            entity_id=entity_id, context=request
        )
    except Exception as e:
        raise http_error(e)

    return 204, None


router_definition.operations["delete_feature_of_interest_entity"] = OperationDefinition(
    path=f"{str(sta.FEATURES_OF_INTEREST)}({app_settings.ID_DELIMITER}{{entity_id}}{app_settings.ID_DELIMITER})",
    methods=["DELETE"],
    view_func=delete_feature_of_interest_entity,
    auth=app_settings.AUTH_HANDLERS.get(
        "delete_feature_of_interest_entity", app_settings.DEFAULT_AUTH_HANDLER
    ),
    response={
        204: None, **delete_entity_error_responses
    }
)
