from ninja import Query
from ninja.responses import Response
from django.http import HttpRequest, HttpResponse
from sensorthings.http import OperationDefinition, http_error
from sensorthings.versions.v1_1 import sensorthings_service
from sensorthings.versions.v1_1.views.resolver import response_schemas
from sensorthings.versions.v1_1.extensions.dataarray.schemas import (
    ObservationDataArrayCollectionQuery,
    ObservationDataArrayCollectionResponse,
)


async def resolve_resource_path(
    request: HttpRequest,
    path: str,
    query: Query[ObservationDataArrayCollectionQuery],
) -> Response | HttpResponse:
    try:
        path_segments = [segment for segment in path.strip("/").split("/") if segment] if path else []
        result, result_type = await sensorthings_service.resolve_entity_path(
            path_segments=path_segments,
            context=request,
            **query.dict(exclude_unset=True)
        )
    except Exception as e:
        raise http_error(e)

    if path_segments[-1] == "$value":
        return HttpResponse(next(iter(result.values())), content_type="text/plain")

    if result_type == "observation_collection" and query.result_format:
        schema_class = ObservationDataArrayCollectionResponse
    else:
        schema_class = response_schemas[result_type]

    return Response(
        status=200,
        data=schema_class(**result).model_dump(
            exclude_unset=True, exclude_none=True, by_alias=True
        ),
    )


resolve_resource_path_operation = OperationDefinition(
    path="/{path:path}",
    methods=["GET"],
    view_func=resolve_resource_path,
    include_in_schema=False
)
