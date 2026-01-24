from typing import Union
from ninja import Field
from sensorthings.types import (
    Absent,
    ISOTimeString,
    ISOIntervalString,
    example_iso_time_string,
    example_iso_interval_string,
)
from sensorthings.v1_1.protocol import sta
from sensorthings.v1_1.conf import app_settings
from .base import BaseSchema
from .factory import (
    build_sta_entity_response_schema,
    build_sta_collection_response_schema,
    build_sta_post_body_schema,
    build_sta_patch_body_schema
)


class ObservationFields(BaseSchema):
    """Base schema for `Observation` entity fields."""

    phenomenon_time: Union[ISOTimeString, ISOIntervalString] = Field(
        ..., examples=[example_iso_time_string, example_iso_interval_string]
    )
    result: app_settings.OBSERVATION_TYPE_SCHEMA
    result_time: ISOTimeString = Field(..., example=example_iso_time_string)
    result_quality: dict | None = None
    valid_time: ISOIntervalString | None = Field(
        None, example=example_iso_interval_string
    )
    parameters: dict = Absent


ObservationResponse = build_sta_entity_response_schema(sta.OBSERVATION_ENTITY, ObservationFields)
ObservationCollectionResponse = build_sta_collection_response_schema(sta.OBSERVATION_ENTITY, ObservationResponse)
ObservationPostBody = build_sta_post_body_schema(sta.OBSERVATION_ENTITY, ObservationFields)
ObservationPatchBody = build_sta_patch_body_schema(sta.OBSERVATION_ENTITY, ObservationFields)

ObservationPatchBody.model_rebuild(force=True)
