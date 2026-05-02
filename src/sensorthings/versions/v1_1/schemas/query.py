from ninja import Schema, Field
from sensorthings.types import Absent
from sensorthings.versions.v1_1 import app_settings


class EntityQuery(Schema):
    """Query schema for entities."""

    select: str = Field(Absent, alias="$select")
    expand: str = Field(Absent, alias="$expand")


class CollectionQuery(EntityQuery):
    """Query schema for collections."""

    filters: str = Field(Absent, alias="$filter")
    count: bool = Field(False, alias="$count")
    orderby: str = Field(Absent, alias="$orderby")
    skip: int = Field(0, ge=0, alias="$skip")
    top: int = Field(100, ge=0, le=app_settings.MAX_TOP, alias="$top")
