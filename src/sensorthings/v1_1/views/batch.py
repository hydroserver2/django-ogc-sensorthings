from ninja import Router
from django.http import HttpRequest, HttpResponse, JsonResponse
from email import message_from_bytes
from email.policy import default as default_policy
from sensorthings.v1_1.http import RouterDefinition, OperationDefinition

router_definition = RouterDefinition(
    router=Router(),
    operations={}
)


def process_batch(
    request: HttpRequest
) -> HttpResponse:
    """"""

    batch_message = message_from_bytes(request.body, policy=default_policy)

    if batch_message.is_multipart():
        pass

    return JsonResponse({})


router_definition.operations["process_batch"] = OperationDefinition(
    path="$batch",
    methods=["POST"],
    view_func=process_batch,
    include_in_schema=False
)
