from ninja import Field
from sensorthings.types import Absent, ISOIntervalString, example_iso_interval_string
from sensorthings.v1_1.protocol import sta
from sensorthings.v1_1.conf import app_settings
from .base import BaseSchema
from .factory import (
    build_sta_entity_response_schema,
    build_sta_collection_response_schema,
    build_sta_post_body_schema,
    build_sta_patch_body_schema
)
from .unit_of_measurement import UnitOfMeasurement


class DatastreamFields(BaseSchema):
    """Base schema for `Datastream` entity fields."""

    name: str
    description: str
    unit_of_measurement: UnitOfMeasurement
    observation_type: app_settings.OBSERVATION_TYPE_VALUE_LITERAL
    properties: app_settings.PROPERTIES_SCHEMAS.get(str(sta.DATASTREAMS), dict) = Absent
    observed_area: dict | None = None
    phenomenon_time: ISOIntervalString | None = Field(
        None, example=example_iso_interval_string
    )
    result_time: ISOIntervalString | None = Field(
        None, example=example_iso_interval_string
    )


DatastreamResponse = build_sta_entity_response_schema(sta.DATASTREAM_ENTITY, DatastreamFields)
DatastreamCollectionResponse = build_sta_collection_response_schema(sta.DATASTREAM_ENTITY, DatastreamResponse)
DatastreamPostBody = build_sta_post_body_schema(sta.DATASTREAM_ENTITY, DatastreamFields)
DatastreamPatchBody = build_sta_patch_body_schema(sta.DATASTREAM_ENTITY, DatastreamFields)

DatastreamPatchBody.model_rebuild(force=True)
