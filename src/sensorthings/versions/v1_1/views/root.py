from ninja import Router
from sensorthings.http import RouterDefinition, OperationDefinition
from sensorthings.versions.v1_1 import sta, app_settings, sensorthings_service
from sensorthings.versions.v1_1.schemas import ServiceRootSchema

router_definition = RouterDefinition(
    router=Router(),
    operations={}
)


async def get_root(request) -> dict:
    """
    Return the SensorThings API service root document.

    This endpoint provides the base structure of the service, including
    conformance information and an empty collection of entities. It is not
    included in the API schema.
    """
    
    server_settings = sensorthings_service.backend_adapter.get_server_settings()
    value = [
        {
            "name": entity_type.set_name,
            "url": f"{app_settings.SERVICE_URL}/{sta.VERSION}/{entity_type.set_name}",
        }
        for entity_type in {
            entity_type.set_name: entity_type for entity_type in sta.entity_types.values()
        }.values()
    ]

    return {
        "server_settings": server_settings, 
        "value": value
    }


router_definition.operations["get_root"] = OperationDefinition(
    path="",
    methods=["GET"],
    view_func=get_root,
    response={
        200: ServiceRootSchema
    },
    include_in_schema=False
)
