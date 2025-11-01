from ninja import Router
from sensorthings.v1_1.core.schemas import ServiceRootSchema

router = Router()


@router.get(
    "",
    include_in_schema=False,
    response=ServiceRootSchema,
    exclude_unset=True,
)
def get_root(request) -> dict:
    """
    Return the SensorThings API service root document.

    This endpoint provides the base structure of the service, including
    conformance information and an empty collection of entities. It is not
    included in the API schema.
    """

    return {"server_settings": {"conformance": []}, "value": []}
