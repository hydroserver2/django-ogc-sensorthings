import copy
from typing import Generic, TypeVar
from ninja import Schema, Field
from pydantic import ConfigDict
from pydantic.alias_generators import to_camel
from pydantic.fields import FieldInfo
from sensorthings.types import Absent
from sensorthings.versions.v1_1 import sta
from sensorthings.versions.v1_1 import app_settings

T = TypeVar("T", bound=Schema)


class BaseSchema(Schema):
    """Base schema for all SensorThings v1.1 entities and collections."""

    model_config: ConfigDict = ConfigDict(
        populate_by_name=True, str_strip_whitespace=True, alias_generator=to_camel
    )


class IdSchema(BaseSchema):
    """Schema that defines a generic SensorThings identifier."""

    id: app_settings.ID_TYPE = Field(
        ...,
        alias=sta.ID,
        examples=[app_settings.ID_EXAMPLE]
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

    Marks all fields as `Absent` by default by re-declaring inherited fields directly in the
    class body before Pydantic processes them. This avoids assigning to the `model_fields`
    property and ensures Absent defaults survive `model_rebuild(force=True)`.
    """

    def __new__(
        cls, name: str, bases: tuple[type, ...], attrs: dict, **kwargs
    ) -> "PartialMetaclass":
        annotations = attrs.setdefault("__annotations__", {})

        # Re-declare inherited fields with Absent defaults before Pydantic compiles the class,
        # so they live in the class __dict__ and survive model_rebuild(force=True).
        # Process bases in MRO order so the first (most-derived) base wins on conflicts.
        for base in bases:
            if not hasattr(base, "model_fields"):
                continue
            for field_name, field_info in base.model_fields.items():
                if field_name in annotations:
                    continue
                new_field = copy.deepcopy(field_info)
                new_field.default = Absent
                new_field.default_factory = None
                annotations[field_name] = field_info.annotation
                attrs[field_name] = new_field

        # Apply to fields declared directly in this class body (e.g. from the namespace dict).
        for field_name in list(annotations.keys()):
            val = attrs.get(field_name)
            if isinstance(val, FieldInfo):
                new_field = copy.deepcopy(val)
                new_field.default = Absent
                new_field.default_factory = None
                attrs[field_name] = new_field

        return super().__new__(cls, name, bases, attrs, **kwargs)
