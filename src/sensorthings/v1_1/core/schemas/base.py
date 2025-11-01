import copy
from uuid import UUID
from typing import Generic, TypeVar, ClassVar
from ninja import Schema, Field
from pydantic import ConfigDict
from pydantic.alias_generators import to_camel, to_snake
from sensorthings.types import Absent
from sensorthings.v1_1 import iot
from sensorthings.v1_1.conf import app_settings

T = TypeVar("T", bound=Schema)


class BaseSchema(Schema):
    """Base schema for all SensorThings v1.1 entities and collections."""

    model_config: ConfigDict = ConfigDict(
        populate_by_name=True, str_strip_whitespace=True, alias_generator=to_camel
    )


class IdSchema(BaseSchema):
    """Schema that defines a generic SensorThings identifier."""

    iot_id: app_settings.ID_TYPE = Field(..., alias=iot.ID)


class BaseEntitySchema(IdSchema, BaseSchema):
    """Base schema for all SensorThings entities."""

    iot_self_link: str = Field(Absent, alias=iot.SELF_LINK)

    _entity: ClassVar[str]
    _related_entities: ClassVar[list[str]]

    @classmethod
    def add_examples(cls) -> None:
        """Add example values to the schema for JSON Schema generation."""

        id_examples: dict[type, str] = {
            int: "1",
            str: "string",
            UUID: "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        }

        iot_id = (
            app_settings.ID_EXAMPLE
            if getattr(app_settings, "ID_EXAMPLE", None) is not None
            else id_examples.get(app_settings.ID_TYPE, 1)
        )

        iot_self_link: str = iot.build_self_link(cls._entity, iot_id)
        cls.model_fields["iot_self_link"].json_schema_extra = {"example": iot_self_link}

        for related_entity in cls._related_entities:
            related_entity_ref: str = to_snake(related_entity)

            cls.model_fields[f"{related_entity_ref}_link"].json_schema_extra = {
                "example": iot.build_nav_link(cls._entity, iot_id, related_entity)
            }

            if f"{related_entity_ref}_next_link" in cls.model_fields:
                cls.model_fields[
                    f"{related_entity_ref}_next_link"
                ].json_schema_extra = {
                    "example": f"{iot.build_nav_link(cls._entity, iot_id, related_entity)}?$skip=100&$top=100"
                }


class BaseCollectionSchema(BaseSchema, Generic[T]):
    """Base schema for collections of SensorThings entities."""

    iot_count: int = Field(Absent, alias=iot.COUNT)
    value: list[T]
    iot_next_link: str = Field(Absent, alias=iot.NEXT_LINK)

    _entity: ClassVar[str]

    @classmethod
    def add_examples(cls) -> None:
        """Add example values to the collection schema."""

        cls.model_fields["iot_next_link"].json_schema_extra = {
            "example": f"{iot.build_entity_link(cls._entity)}?$skip=100&$top=100"
        }


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
