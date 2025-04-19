from ninja import Router
from django.http import HttpResponse
from django.urls import reverse
from .schemas import ServerRootResponse
from sensorthings import settings


router = Router()


@router.get(
    '',
    include_in_schema=False,
    by_alias=True,
    response=ServerRootResponse
)
def get_root(request):
    """
    Get SensorThings server capabilities.
    """

    host_url = getattr(settings, 'PROXY_BASE_URL', request.get_host())
    response = {
        'server_settings': {
            'conformance': settings.ST_CONFORMANCE
        },
        'server_capabilities': [
            {
                'name': capability['NAME'],
                'url': host_url + reverse(f"sensorthings-v{settings.ST_VERSION}-api:{capability['VIEW']}")
            } for capability in settings.ST_CAPABILITIES
        ]
    }

    return response


def handle_advanced_path(request):  # noqa
    return HttpResponse(status=404)
