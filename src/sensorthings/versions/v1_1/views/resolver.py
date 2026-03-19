from ninja import Router, Query
from ninja.responses import Response
from django.http import HttpRequest, HttpResponse
from sensorthings.http import RouterDefinition, OperationDefinition, http_error
from sensorthings.versions.v1_1 import sensorthings_service
from sensorthings.versions.v1_1.schemas import (BaseSchema, CollectionQuery, ThingCollectionResponse, ThingResponse,
                                                LocationCollectionResponse, LocationResponse,
                                                HistoricalLocationCollectionResponse, HistoricalLocationResponse,
                                                DatastreamCollectionResponse, DatastreamResponse,
                                                SensorCollectionResponse, SensorResponse,
                                                ObservedPropertyCollectionResponse, ObservedPropertyResponse,
                                                FeatureOfInterestCollectionResponse, FeatureOfInterestResponse,
                                                ObservationCollectionResponse, ObservationResponse)


router_definition = RouterDefinition(
    router=Router(),
    operations={}
)

response_schemas = {
    "thing_collection": ThingCollectionResponse,
    "thing_entity": ThingResponse,
    "location_collection": LocationCollectionResponse,
    "location_entity": LocationResponse,
    "historical_location_collection": HistoricalLocationCollectionResponse,
    "historical_location_entity": HistoricalLocationResponse,
    "datastream_collection": DatastreamCollectionResponse,
    "datastream_entity": DatastreamResponse,
    "sensor_collection": SensorCollectionResponse,
    "sensor_entity": SensorResponse,
    "observed_property_collection": ObservedPropertyCollectionResponse,
    "observed_property_entity": ObservedPropertyResponse,
    "feature_of_interest_collection": FeatureOfInterestCollectionResponse,
    "feature_of_interest_entity": FeatureOfInterestResponse,
    "observation_collection": ObservationCollectionResponse,
    "observation_entity": ObservationResponse,
}


async def resolve_resource_path(
    request: HttpRequest,
    path: str,
    query: Query[CollectionQuery],
) -> Response | HttpResponse:
    """"""

    try:
        path_segments = [segment for segment in path.strip("/").split("/") if segment] if path else []
        result, result_type = await sensorthings_service.resolve_entity_path(
            path_segments=[segment for segment in path.strip("/").split("/") if segment] if path else [],
            context=request,
            **query.dict(exclude_unset=True)
        )
    except Exception as e:
        raise http_error(e)

    if path_segments[-1] == "$value":
        return HttpResponse(next(iter(result.values())), content_type="text/plain")
    else:
        return Response(
            status=200,
            data=response_schemas[result_type](**result).model_dump(
                exclude_unset=True, exclude_none=True, by_alias=True
            ),
        )

router_definition.operations["resolve_resource_path"] = OperationDefinition(
    path="/{path:path}",
    methods=["GET"],
    view_func=resolve_resource_path,
    include_in_schema=False
)
