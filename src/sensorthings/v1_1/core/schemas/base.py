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
    model_config = ConfigDict(
        populate_by_name=True, str_strip_whitespace=True, alias_generator=to_camel
    )


class IdSchema(BaseSchema):
    iot_id: app_settings.ID_TYPE = Field(..., alias=iot.ID)


class BaseEntitySchema(IdSchema, BaseSchema):
    iot_self_link: str = Field(None, alias=iot.SELF_LINK)

    _entity: ClassVar[str]
    _related_entities: ClassVar[list[str]]

    @classmethod
    def add_examples(cls):
        id_examples = {
            int: "1", str: "string", UUID: "3fa85f64-5717-4562-b3fc-2c963f66afa6"
        }

        iot_id = (
            app_settings.ID_EXAMPLE
            if getattr(app_settings, "ID_EXAMPLE", None) is not None
            else id_examples.get(app_settings.ID_TYPE, "1")
        )

        iot_self_link = iot.build_self_link(cls._entity, iot_id)

        cls.model_fields["iot_self_link"].json_schema_extra = {
            "example": iot_self_link
        }

        for related_entity in cls._related_entities:
            related_entity_ref = to_snake(related_entity)

            cls.model_fields[f"{related_entity_ref}_link"].json_schema_extra = {
                "example": iot.build_nav_link(cls._entity, iot_id, related_entity)
            }

            if f"{related_entity_ref}_next_link" in cls.model_fields:
                cls.model_fields[f"{related_entity_ref}_next_link"].json_schema_extra = {
                    "example": f"{iot.build_nav_link(cls._entity, iot_id, related_entity)}?$skip=100&$top=100"
                }


class BaseCollectionSchema(BaseSchema, Generic[T]):
    iot_count: int = Field(None, alias=iot.COUNT)
    value: list[T] = Field(default_factory=list)
    iot_next_link: str = Field(None, alias=iot.NEXT_LINK)

    _entity: ClassVar[str]

    @classmethod
    def add_examples(cls):
        cls.model_fields["iot_next_link"].json_schema_extra = {
            "example": f"{iot.build_entity_link(cls._entity)}?$skip=100&$top=100"
        }


class PartialMetaclass(type(Schema)):
    def __new__(cls, name, bases, attrs, **kwargs):
        for base in bases:
            if issubclass(base, Schema):
                for field_name, field_value in base.model_fields.items():
                    field_value.default = Absent

        return super().__new__(cls, name, bases, attrs, **kwargs)
