import copy
from typing import Generic, TypeVar
from ninja import Schema, Field
from pydantic import ConfigDict
from pydantic.alias_generators import to_camel
from sensorthings.types import Absent
from sensorthings.v1_1.protocol import sta
from sensorthings.v1_1.conf import app_settings

T = TypeVar("T", bound=Schema)


class BaseSchema(Schema):
    """Base schema for all SensorThings v1.1 entities and collections."""

    model_config: ConfigDict = ConfigDict(
        populate_by_name=True, str_strip_whitespace=True, alias_generator=to_camel
    )


class IdSchema(BaseSchema):
    """Schema that defines a generic SensorThings identifier."""

    iot_id: app_settings.ID_TYPE = Field(
        ...,
        alias=sta.ID,
        example=app_settings.ID_EXAMPLE
    )


class BaseEntitySchema(IdSchema, BaseSchema):
    """Base schema for all SensorThings entities."""

    iot_self_link: str = Field(Absent, alias=sta.SELF_LINK)


class BaseCollectionSchema(BaseSchema, Generic[T]):
    """Base schema for collections of SensorThings entities."""

    iot_count: int = Field(Absent, alias=sta.COUNT)
    value: list[T]
    iot_next_link: str = Field(Absent, alias=sta.NEXT_LINK)


class PartialMetaclass(type(Schema)):
    """
    Metaclass for creating "partial" schemas.

    Marks all fields as `Absent` by default, necessary for PATCH operations where only provided fields should
    be included, or responses where a subset of fields is selected by the client. Copies all inherited model fields and
    annotations to avoid mutating base classes.
    """

    def __new__(
        cls, name: str, bases: tuple[type, ...], attrs: dict, **kwargs
    ) -> "PartialMetaclass":
        new_cls = super().__new__(cls, name, bases, attrs, **kwargs)
        new_cls.model_fields = {
            k: copy.deepcopy(v) for k, v in new_cls.model_fields.items()
        }

        for field in new_cls.model_fields.values():
            field.default = Absent

        return new_cls
