from pydantic.alias_generators import to_snake
from sensorthings.v1_1.protocol.entity import EntityType


class STA:
    """
    Defines the SensorThings API v1.1 controlled vocabulary and conceptual entity model.

    This class provides protocol-level constants and immutable entity definitions that
    describe the SensorThings v1.1 conceptual model, including entity names, properties,
    and relationships. It serves as a central, implementation-independent reference for
    SensorThings semantics and structure, and is intended to be consumed by routing,
    serialization, and link-construction logic rather than representing runtime data
    or persistence models.
    """

    VERSION = "v1.1"
    ID = "@iot.id"
    SELF_LINK = "@iot.selfLink"
    COUNT = "@iot.count"
    NEXT_LINK = "@iot.nextLink"
    NAVIGATION_LINK = "@iot.navigationLink"

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
            related_entity_type_names=sorted(
                set(base.related_entity_type_names)
                | set(related_entity_type_names or [])
            ),
            related_entity_type_set_names=sorted(
                set(base.related_entity_type_set_names)
                | set(related_entity_type_set_names or [])
            ),
        )

        cls.register_entity(entity_type)
