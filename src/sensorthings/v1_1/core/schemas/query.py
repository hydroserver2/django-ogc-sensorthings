from ninja import Schema, Field
from sensorthings.v1_1.conf import app_settings


class EntityQuery(Schema):
    select: str = Field("", alias="$select")
    expand: str = Field("", alias="$expand")


class CollectionQuery(EntityQuery):
    filter: str = Field("", alias="$filter")
    count: bool = Field(False, alias="$count")
    orderby: str = Field("", alias="$orderby")
    skip: int = Field(0, ge=0, alias="$skip")
    top: int = Field(100, ge=0, le=app_settings.MAX_TOP, alias="$top")
