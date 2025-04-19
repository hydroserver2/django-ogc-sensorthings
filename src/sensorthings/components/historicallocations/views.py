from ninja import Query
from django.http import HttpResponse
from sensorthings import settings
from sensorthings.router import SensorThingsRouter
from sensorthings.http import SensorThingsHttpRequest
from sensorthings.schemas import ListQueryParams, GetQueryParams
from sensorthings.factories import SensorThingsRouterFactory, SensorThingsEndpointFactory
from .schemas import (HistoricalLocation, HistoricalLocationPostBody, HistoricalLocationPatchBody,
                      HistoricalLocationListResponse, HistoricalLocationGetResponse)


id_qualifier = settings.ST_API_ID_QUALIFIER
id_type = settings.ST_API_ID_TYPE


def list_historical_locations(
        request: SensorThingsHttpRequest,
        params: ListQueryParams = Query(...)
):
    """
    Get a collection of Historical Location entities.

    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/historical-location/properties" target="_blank">\
      Historical Location Properties</a> -
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/historical-location/relations" target="_blank">\
      Historical Location Relations</a>
    """

    return request.engine.list_entities(
        component=HistoricalLocation,
        query_params=params.dict()
    )


list_historical_locations_endpoint = SensorThingsEndpointFactory(
    router_name='historical_location',
    endpoint_route='/HistoricalLocations',
    view_function=list_historical_locations,
    view_method=SensorThingsRouter.st_list,
    view_response_schema=HistoricalLocationListResponse,
)


def get_historical_location(
        request: SensorThingsHttpRequest,
        historical_location_id: id_type,
        params: GetQueryParams = Query(...)
):
    """
    Get a Historical Location entity.

    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/historical-location/properties" target="_blank">\
      Historical Location Properties</a> -
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/historical-location/relations" target="_blank">\
      Historical Location Relations</a>
    """

    return request.engine.get_entity(
        component=HistoricalLocation,
        entity_id=historical_location_id,
        query_params=params.dict()
    )


get_historical_location_endpoint = SensorThingsEndpointFactory(
    router_name='historical_location',
    endpoint_route=f'/HistoricalLocations({id_qualifier}{{historical_location_id}}{id_qualifier})',
    view_function=get_historical_location,
    view_method=SensorThingsRouter.st_get,
    view_response_schema=HistoricalLocationGetResponse,
)


def create_historical_location(
        request: SensorThingsHttpRequest,
        response: HttpResponse,
        historical_location: HistoricalLocationPostBody
):
    """
    Create a new Historical Location entity.

    Links:
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/historical-location/properties" target="_blank">\
      Historical Location Properties</a> -
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/historical-location/relations" target="_blank">\
      Historical Location Relations</a> -
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/create-update-delete/create-entity" target="_blank">\
      Create Entity</a>
    """

    request.engine.create_entity(
        component=HistoricalLocation,
        entity_body=historical_location,
        response=response
    )

    return 201, None


create_historical_location_endpoint = SensorThingsEndpointFactory(
    router_name='historical_location',
    endpoint_route='/HistoricalLocations',
    view_function=create_historical_location,
    view_method=SensorThingsRouter.st_post,
)


def update_historical_location(
        request: SensorThingsHttpRequest,
        historical_location_id: id_type,
        historical_location: HistoricalLocationPatchBody
):
    """
    Update an existing Historical Location entity.

    Links:
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/historical-location/properties" target="_blank">\
      Historical Location Properties</a> -
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/historical-location/relations" target="_blank">\
      Historical Location Relations</a> -
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/create-update-delete/update-entity" target="_blank">\
      Update Entity</a>
    """

    request.engine.update_entity(
        component=HistoricalLocation,
        entity_id=historical_location_id,
        entity_body=historical_location
    )

    return 204, None


update_historical_location_endpoint = SensorThingsEndpointFactory(
    router_name='historical_location',
    endpoint_route=f'/HistoricalLocations({id_qualifier}{{historical_location_id}}{id_qualifier})',
    view_function=update_historical_location,
    view_method=SensorThingsRouter.st_patch,
)


def delete_historical_location(request: SensorThingsHttpRequest, historical_location_id: id_type):
    """
    Delete a Historical Location entity.

    Links:
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/create-update-delete/delete-entity" target="_blank">\
      Delete Entity</a>
    """

    request.engine.delete_entity(
        component=HistoricalLocation,
        entity_id=historical_location_id
    )

    return 204, None


delete_historical_location_endpoint = SensorThingsEndpointFactory(
    router_name='historical_location',
    endpoint_route=f'/HistoricalLocations({id_qualifier}{{historical_location_id}}{id_qualifier})',
    view_function=delete_historical_location,
    view_method=SensorThingsRouter.st_delete,
)


historical_location_router_factory = SensorThingsRouterFactory(
    name='historical_location',
    tags=['Historical Locations'],
    endpoints=[
        list_historical_locations_endpoint,
        get_historical_location_endpoint,
        create_historical_location_endpoint,
        update_historical_location_endpoint,
        delete_historical_location_endpoint
    ]
)
