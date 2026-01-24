from ninja import Field
from sensorthings.types import Absent, ISOIntervalString, example_iso_interval_string
from sensorthings.v1_1.protocol import sta
from sensorthings.v1_1.conf import app_settings
from sensorthings.v1_1.schemas.base import BaseSchema
from sensorthings.v1_1.schemas.factory import (
    build_sta_entity_response_schema,
    build_sta_collection_response_schema,
    build_sta_post_body_schema,
    build_sta_patch_body_schema
)
from sensorthings.v1_1.schemas.unit_of_measurement import UnitOfMeasurement


class MultiDatastreamFields(BaseSchema):
    """Base schema for `MultiDatastream` entity fields."""

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


MultiDatastreamResponse = build_sta_entity_response_schema(sta.DATASTREAM_ENTITY, MultiDatastreamFields)
MultiDatastreamCollectionResponse = build_sta_collection_response_schema(sta.DATASTREAM_ENTITY, MultiDatastreamResponse)
MultiDatastreamPostBody = build_sta_post_body_schema(sta.MULTI_DATASTREAM_ENTITY, MultiDatastreamFields)
MultiDatastreamPatchBody = build_sta_patch_body_schema(sta.MULTI_DATASTREAM_ENTITY, MultiDatastreamFields)

MultiDatastreamPatchBody.model_rebuild(force=True)
