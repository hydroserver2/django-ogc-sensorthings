from ninja import Router
from sensorthings.v1_1.core.schemas import ServiceRootSchema

router = Router()


@router.get(
    "",
    include_in_schema=False,
    response=ServiceRootSchema,
    exclude_unset=True,
)
def get_root(request):

    return {
        "server_settings": {
            "conformance": []
        },
        "value": []
    }
