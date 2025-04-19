from ninja import Query
from django.http import HttpResponse
from sensorthings import settings
from sensorthings.router import SensorThingsRouter
from sensorthings.http import SensorThingsHttpRequest
from sensorthings.schemas import ListQueryParams, GetQueryParams
from sensorthings.factories import SensorThingsRouterFactory, SensorThingsEndpointFactory
from .schemas import (FeatureOfInterest, FeatureOfInterestPostBody, FeatureOfInterestPatchBody,
                      FeatureOfInterestListResponse, FeatureOfInterestGetResponse)


id_qualifier = settings.ST_API_ID_QUALIFIER
id_type = settings.ST_API_ID_TYPE


def list_features_of_interest(
        request: SensorThingsHttpRequest,
        params: ListQueryParams = Query(...)
):
    """
    Get a collection of Feature of Interest entities.

    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/feature-of-interest/properties" target="_blank">\
      Feature of Interest Properties</a> -
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/feature-of-interest/relations" target="_blank">\
      Feature of Interest Relations</a>
    """

    return request.engine.list_entities(
        component=FeatureOfInterest,
        query_params=params.dict()
    )


list_features_of_interest_endpoint = SensorThingsEndpointFactory(
    router_name='feature_of_interest',
    endpoint_route='/FeaturesOfInterest',
    view_function=list_features_of_interest,
    view_method=SensorThingsRouter.st_list,
    view_response_schema=FeatureOfInterestListResponse
)


def get_feature_of_interest(
        request: SensorThingsHttpRequest,
        feature_of_interest_id: id_type,
        params: GetQueryParams = Query(...)
):
    """
    Get a Feature of Interest entity.

    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/feature-of-interest/properties" target="_blank">\
      Feature of Interest Properties</a> -
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/feature-of-interest/relations" target="_blank">\
      Feature of Interest Relations</a>
    """

    return request.engine.get_entity(
        component=FeatureOfInterest,
        entity_id=feature_of_interest_id,
        query_params=params.dict()
    )


get_feature_of_interest_endpoint = SensorThingsEndpointFactory(
    router_name='feature_of_interest',
    endpoint_route=f'/FeaturesOfInterest({id_qualifier}{{feature_of_interest_id}}{id_qualifier})',
    view_function=get_feature_of_interest,
    view_method=SensorThingsRouter.st_get,
    view_response_schema=FeatureOfInterestGetResponse
)


def create_feature_of_interest(
        request: SensorThingsHttpRequest,
        response: HttpResponse,
        feature_of_interest: FeatureOfInterestPostBody
):
    """
    Create a new Feature of Interest entity.

    Links:
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/feature-of-interest/properties" target="_blank">\
      Feature of Interest Properties</a> -
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/feature-of-interest/relations" target="_blank">\
      Feature of Interest Relations</a> -
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/create-update-delete/create-entity" target="_blank">\
      Create Entity</a>
    """

    request.engine.create_entity(
        component=FeatureOfInterest,
        entity_body=feature_of_interest,
        response=response
    )

    return 201, None


create_feature_of_interest_endpoint = SensorThingsEndpointFactory(
    router_name='feature_of_interest',
    endpoint_route='/FeaturesOfInterest',
    view_function=create_feature_of_interest,
    view_method=SensorThingsRouter.st_post,
)


def update_feature_of_interest(
        request: SensorThingsHttpRequest,
        feature_of_interest_id: id_type,
        feature_of_interest: FeatureOfInterestPatchBody
):
    """
    Update an existing Feature of Interest entity.

    Links:
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/feature-of-interest/properties" target="_blank">\
      Feature of Interest Properties</a> -
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/feature-of-interest/relations" target="_blank">\
      Feature of Interest Relations</a> -
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/create-update-delete/update-entity" target="_blank">\
      Update Entity</a>
    """

    request.engine.update_entity(
        component=FeatureOfInterest,
        entity_id=feature_of_interest_id,
        entity_body=feature_of_interest
    )

    return 204, None


update_feature_of_interest_endpoint = SensorThingsEndpointFactory(
    router_name='feature_of_interest',
    endpoint_route=f'/FeaturesOfInterest({id_qualifier}{{feature_of_interest_id}}{id_qualifier})',
    view_function=update_feature_of_interest,
    view_method=SensorThingsRouter.st_patch,
)


def delete_feature_of_interest(
        request: SensorThingsHttpRequest,
        feature_of_interest_id: id_type
):
    """
    Delete a Feature of Interest entity.

    Links:
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/create-update-delete/delete-entity" target="_blank">\
      Delete Entity</a>
    """

    request.engine.delete_entity(
        component=FeatureOfInterest,
        entity_id=feature_of_interest_id
    )

    return 204, None


delete_feature_of_interest_endpoint = SensorThingsEndpointFactory(
    router_name='feature_of_interest',
    endpoint_route=f'/FeaturesOfInterest({id_qualifier}{{feature_of_interest_id}}{id_qualifier})',
    view_function=delete_feature_of_interest,
    view_method=SensorThingsRouter.st_delete,
)


feature_of_interest_router_factory = SensorThingsRouterFactory(
    name='feature_of_interest',
    tags=['Features Of Interest'],
    endpoints=[
        list_features_of_interest_endpoint,
        get_feature_of_interest_endpoint,
        create_feature_of_interest_endpoint,
        update_feature_of_interest_endpoint,
        delete_feature_of_interest_endpoint
    ]
)
