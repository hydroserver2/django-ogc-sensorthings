from ninja import Router
from sensorthings.http import RouterDefinition, OperationDefinition
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

    return {"server_settings": {"conformance": []}, "value": []}


router_definition.operations["get_root"] = OperationDefinition(
    path="",
    methods=["GET"],
    view_func=get_root,
    response={
        200: ServiceRootSchema
    },
    include_in_schema=False
)
