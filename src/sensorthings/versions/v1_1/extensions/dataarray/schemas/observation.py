from typing import Literal
from ninja import Field
from pydantic import model_validator
from sensorthings.types import Absent
from sensorthings.versions.v1_1 import STA
from sensorthings.versions.v1_1.schemas import CollectionQuery, BaseSchema, BaseCollectionSchema, IdSchema


class ObservationDataArrayCollectionQuery(CollectionQuery):
    """Query schema for data array collections."""

    result_format: Literal["dataArray"] = Field(Absent, alias="$resultFormat")


class ObservationDataArrayResponse(BaseSchema):
    """GET response schema representing `Observation` entities in a data array format."""

    datastream_link: str = Field(
        alias="Datastream" + STA.NAVIGATION_LINK,
    )
    components: list[str]
    data_array: list[list]


class ObservationDataArrayCollectionResponse(BaseCollectionSchema):
    """GET response schema representing a collection of `Observation` entities in a data array format."""

    value: list[ObservationDataArrayResponse]


class DataArrayPostGroup(BaseSchema):
    """A single datastream group in a CreateObservations request body."""

    datastream: IdSchema = Field(..., alias="Datastream")
    components: list[str]
    data_array: list[list] = Field(..., alias="dataArray")

    @model_validator(mode="after")
    def validate_row_lengths(self):
        n = len(self.components)
        for i, row in enumerate(self.data_array):
            if len(row) != n:
                raise ValueError(
                    f"dataArray[{i}] has {len(row)} values but components has {n}"
                )
        return self
