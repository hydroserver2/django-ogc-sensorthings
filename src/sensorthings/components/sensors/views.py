from ninja import Query
from django.http import HttpResponse
from sensorthings import settings
from sensorthings.router import SensorThingsRouter
from sensorthings.http import SensorThingsHttpRequest
from sensorthings.schemas import ListQueryParams, GetQueryParams
from sensorthings.factories import SensorThingsRouterFactory, SensorThingsEndpointFactory
from .schemas import Sensor, SensorPostBody, SensorPatchBody, SensorListResponse, SensorGetResponse


id_qualifier = settings.ST_API_ID_QUALIFIER
id_type = settings.ST_API_ID_TYPE


def list_sensors(
        request,
        params: ListQueryParams = Query(...)
):
    """
    Get a collection of Sensor entities.

    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/sensor/properties" target="_blank">\
      Sensor Properties</a> -
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/sensor/relations" target="_blank">\
      Sensor Relations</a>
    """

    return request.engine.list_entities(
        component=Sensor,
        query_params=params.dict()
    )


list_sensors_endpoint = SensorThingsEndpointFactory(
    router_name='sensor',
    endpoint_route='/Sensors',
    view_function=list_sensors,
    view_method=SensorThingsRouter.st_list,
    view_response_schema=SensorListResponse,
)


def get_sensor(
        request: SensorThingsHttpRequest,
        sensor_id: id_type,
        params: GetQueryParams = Query(...)
):
    """
    Get a Sensor entity.

    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/sensor/properties" target="_blank">\
      Sensor Properties</a> -
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/sensor/relations" target="_blank">\
      Sensor Relations</a>
    """

    return request.engine.get_entity(
        component=Sensor,
        entity_id=sensor_id,
        query_params=params.dict()
    )


get_sensor_endpoint = SensorThingsEndpointFactory(
    router_name='sensor',
    endpoint_route=f'/Sensors({id_qualifier}{{sensor_id}}{id_qualifier})',
    view_function=get_sensor,
    view_method=SensorThingsRouter.st_get,
    view_response_schema=SensorGetResponse,
)


def create_sensor(
        request: SensorThingsHttpRequest,
        response: HttpResponse,
        sensor: SensorPostBody
):
    """
    Create a new Sensor entity.

    Links:
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/sensor/properties" target="_blank">\
      Sensor Properties</a> -
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/sensor/relations" target="_blank">\
      Sensor Relations</a> -
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/create-update-delete/create-entity" target="_blank">\
      Create Entity</a>
    """

    request.engine.create_entity(
        component=Sensor,
        entity_body=sensor,
        response=response
    )

    return 201, None


create_sensor_endpoint = SensorThingsEndpointFactory(
    router_name='sensor',
    endpoint_route='/Sensors',
    view_function=create_sensor,
    view_method=SensorThingsRouter.st_post,
)


def update_sensor(
        request: SensorThingsHttpRequest,
        sensor_id: id_type,
        sensor: SensorPatchBody
):
    """
    Update an existing Sensor entity.

    Links:
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/sensor/properties" target="_blank">\
      Sensor Properties</a> -
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/sensor/relations" target="_blank">\
      Sensor Relations</a> -
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/create-update-delete/update-entity" target="_blank">\
      Update Entity</a>
    """

    request.engine.update_entity(
        component=Sensor,
        entity_id=sensor_id,
        entity_body=sensor
    )

    return 204, None


update_sensor_endpoint = SensorThingsEndpointFactory(
    router_name='sensor',
    endpoint_route=f'/Sensors({id_qualifier}{{sensor_id}}{id_qualifier})',
    view_function=update_sensor,
    view_method=SensorThingsRouter.st_patch,
)


def delete_sensor(
        request: SensorThingsHttpRequest,
        sensor_id: id_type
):
    """
    Delete a Sensor entity.

    Links:
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/create-update-delete/delete-entity" target="_blank">\
      Delete Entity</a>
    """

    request.engine.delete_entity(
        component=Sensor,
        entity_id=sensor_id
    )

    return 204, None


delete_sensor_endpoint = SensorThingsEndpointFactory(
    router_name='sensor',
    endpoint_route=f'/Sensors({id_qualifier}{{sensor_id}}{id_qualifier})',
    view_function=delete_sensor,
    view_method=SensorThingsRouter.st_delete,
)


sensor_router_factory = SensorThingsRouterFactory(
    name='sensor',
    tags=['Sensors'],
    endpoints=[
        list_sensors_endpoint,
        get_sensor_endpoint,
        create_sensor_endpoint,
        update_sensor_endpoint,
        delete_sensor_endpoint
    ]
)
