from typing import Literal
from ninja import Field
from sensorthings.types import Absent
from sensorthings.versions.v1_1 import sta
from sensorthings.versions.v1_1.schemas import CollectionQuery, BaseSchema, BaseCollectionSchema


class ObservationDataArrayCollectionQuery(CollectionQuery):
    """Query schema for data array collections."""

    result_format: Literal["dataArray"] = Field(Absent, alias="$resultFormat")


class ObservationDataArrayResponse(BaseSchema):
    """GET response schema representing `Observation` entities in a data array format."""

    datastream_link: str = Field(
        alias="Datastream" + sta.NAVIGATION_LINK,
    )
    components: list[str]
    data_array: list[list]


class ObservationDataArrayCollectionResponse(BaseCollectionSchema):
    """GET response schema representing a collection of `Observation` entities in a data array format."""

    value: list[ObservationDataArrayResponse]


class ObservationDataArrayPostBody(BaseSchema):
    """POST body schema for creating new `Observation` entities from a data array format."""

    components: list[str]
    data_array: list[list]
