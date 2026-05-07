from ninja import Router
from django.http import HttpRequest, HttpResponse, JsonResponse
from email import message_from_bytes
from email.policy import default as default_policy
from sensorthings.http import RouterDefinition, OperationDefinition
from sensorthings.versions.v1_1 import app_settings

router_definition = RouterDefinition(
    router=Router(),
    operations={}
)


def process_batch(
    request: HttpRequest
) -> HttpResponse:
    """
    Process a SensorThings API batch request.

    This view parses the incoming HTTP request body as a MIME batch message
    and serves as the entry point for handling multipart batch operations.
    The actual execution of batch parts is handled elsewhere.
    """

    batch_message = message_from_bytes(request.body, policy=default_policy)

    if batch_message.is_multipart():
        pass

    return JsonResponse({})


router_definition.operations["process_batch"] = OperationDefinition(
    path="$batch",
    methods=["POST"],
    view_func=process_batch,
    auth=app_settings.AUTH_HANDLERS.get(
        "process_batch", app_settings.DEFAULT_AUTH_HANDLER
    ),
    include_in_schema=False
)
