from abc import ABC
from typing import ClassVar
from pydantic.alias_generators import to_snake
from sensorthings.types import EntityType


class BaseProtocol(ABC):
    """
    Base class for SensorThings API vocabularies and conceptual models.
    """

    VERSION: ClassVar[str]
    ID: ClassVar[str]
    SELF_LINK: ClassVar[str]
    COUNT: ClassVar[str]
    NEXT_LINK: ClassVar[str]
    NAVIGATION_LINK: ClassVar[str]

    entity_types: dict[str, EntityType] = {}

    @classmethod
    def register_entity(cls, entity_type: EntityType) -> None:
        cls.entity_types[entity_type.name] = entity_type
        cls.entity_types[entity_type.set_name] = entity_type

        setattr(cls, f"{to_snake(entity_type.name).upper()}_ENTITY", entity_type)
        setattr(cls, to_snake(entity_type.name).upper(), entity_type.name)
        setattr(cls, to_snake(entity_type.set_name).upper(), entity_type.set_name)

    @classmethod
    def get_entity_type(cls, name: str) -> EntityType | None:
        return cls.entity_types.get(name)

    @classmethod
    def extend_entity(
        cls,
        entity_name: str,
        *,
        related_entity_type_names: list[str] | None = None,
        related_entity_type_set_names: list[str] | None = None,
    ) -> None:
        base = cls.entity_types[entity_name]

        entity_type = EntityType(
            name=base.name,
            set_name=base.set_name,
            primitive_properties=base.primitive_properties,
            complex_properties=base.complex_properties,
            optional_properties=base.optional_properties,
            related_entity_type_names=sorted(
                set(base.related_entity_type_names)
                | set(related_entity_type_names or [])
            ),
            related_entity_type_set_names=sorted(
                set(base.related_entity_type_set_names)
                | set(related_entity_type_set_names or [])
            ),
            dto_class=base.dto_class,
        )

        cls.register_entity(entity_type)
