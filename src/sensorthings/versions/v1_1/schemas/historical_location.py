from ninja import Field
from sensorthings.types import ISOTimeString, example_iso_time_string
from sensorthings.versions.v1_1 import sta
from .base import BaseSchema
from .factory import (
    build_sta_entity_response_schema,
    build_sta_collection_response_schema,
    build_sta_post_body_schema,
    build_sta_patch_body_schema
)


class HistoricalLocationFields(BaseSchema):
    """Base schema for `HistoricalLocation` entity fields."""

    time: ISOTimeString = Field(..., example=example_iso_time_string)


HistoricalLocationResponse = build_sta_entity_response_schema(sta.HISTORICAL_LOCATION_ENTITY, HistoricalLocationFields)
HistoricalLocationCollectionResponse = build_sta_collection_response_schema(
    sta.HISTORICAL_LOCATION_ENTITY, HistoricalLocationResponse
)
HistoricalLocationPostBody = build_sta_post_body_schema(sta.HISTORICAL_LOCATION_ENTITY, HistoricalLocationFields)
HistoricalLocationPatchBody = build_sta_patch_body_schema(sta.HISTORICAL_LOCATION_ENTITY, HistoricalLocationFields)

HistoricalLocationPatchBody.model_rebuild(force=True)
