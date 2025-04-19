from typing import Optional
from pydantic import Field, ConfigDict
from ninja import Schema
from sensorthings.schemas import EntityId
from sensorthings.types import ISOIntervalString


class DeleteObservationsPostBody(Schema):
    """
    Schema for deleting batches of observations from a datastream.

    Attributes
    ----------
    datastream : EntityId
        ID of the Datastream associated whose observations will be deleted.
    phenomenon_time : Optional[ISOIntervalString]
        The range of phenomenon times over which observations will be deleted.
    """

    model_config = ConfigDict(populate_by_name=True)

    datastream: EntityId = Field(..., alias='Datastream')
    phenomenon_time: Optional[ISOIntervalString] = Field(None, alias='phenomenonTime')
