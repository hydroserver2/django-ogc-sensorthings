from typing import Union, Annotated, cast
from ninja import Schema, Field
from pydantic.alias_generators import to_snake
from sensorthings.types import Absent
from sensorthings.v1_1.protocol import sta, EntityType
from sensorthings.v1_1.conf import app_settings
from sensorthings.v1_1.http import build_self_link, build_nav_link, build_next_link
from .base import IdSchema, BaseSchema, BaseEntitySchema, PartialMetaclass, BaseCollectionSchema


def build_sta_entity_response_schema(
    entity_type: EntityType,
    entity_fields_schema: type[Schema]
) -> type[BaseEntitySchema]:
    """
    Build and return a Ninja schema class representing a single SensorThings
    entity response.

    The generated schema combines the entity’s core fields with standard
    SensorThings response elements, including navigation links, related entity
    references, and embedded collections where applicable. All related fields
    are optional and marked as absent by default to support partial responses
    and `$expand`/`$select` semantics.
    """

    namespace = {
        "__annotations__": {},
        "__doc__": f"GET response schema representing a `{entity_type.name}` entity."
    }

    for related_entity_type_name in entity_type.related_entity_type_names:
        property_name = to_snake(related_entity_type_name)
        nav_link = build_nav_link(
            entity_type_set_name=entity_type.set_name,
            iot_id=app_settings.ID_EXAMPLE,
            related_entity_type_name=related_entity_type_name
        )

        namespace["__annotations__"][f"{property_name}_link"] = str
        namespace[f"{property_name}_link"] = Field(
            Absent,
            alias=related_entity_type_name + sta.NAVIGATION_LINK,
            example=nav_link
        )

        # TODO: https://github.com/swagger-api/swagger-ui/issues/10583
        # WORKAROUND
        namespace["__annotations__"][property_name] = Union[f"{related_entity_type_name}Response", None]
        # CORRECT:
        # namespace["__annotations__"][property_name] = f"{related_entity_type_name}Response"
        namespace[property_name] = Field(default_factory=lambda: Absent, alias=related_entity_type_name)

    for related_entity_type_set_name in entity_type.related_entity_type_set_names:
        property_name = to_snake(related_entity_type_set_name)
        related_entity_type = sta.get_entity_type(related_entity_type_set_name)
        nav_link = build_nav_link(
            entity_type_set_name=entity_type.set_name,
            iot_id=app_settings.ID_EXAMPLE,
            related_entity_type_name=related_entity_type_set_name
        )

        namespace["__annotations__"][f"{property_name}_link"] = str
        namespace[f"{property_name}_link"] = Field(
            Absent,
            alias=related_entity_type_set_name + sta.NAVIGATION_LINK,
            example=nav_link
        )

        namespace["__annotations__"][f"{property_name}_count"] = int
        namespace[f"{property_name}_count"] = Field(Absent, alias=related_entity_type_set_name + sta.COUNT)

        namespace["__annotations__"][property_name] = list[f"{related_entity_type.name}Response"]
        namespace[property_name] = Field(Absent, alias=related_entity_type_set_name)

        namespace["__annotations__"][f"{property_name}_next_link"] = str
        namespace[f"{property_name}_next_link"] = Field(
            Absent,
            alias=related_entity_type_set_name + sta.NEXT_LINK,
            example=build_next_link(
                nav_link=nav_link,
                query_parameters={}
            )
        )

    entity_schema = cast(
        type[BaseEntitySchema],
        PartialMetaclass(
            f"{entity_type.name}Response",
            (entity_fields_schema, BaseEntitySchema,),
            namespace
        )
    )

    entity_schema.model_fields["iot_self_link"].json_schema_extra = {
        "example": build_self_link(
            entity_type.set_name,
            app_settings.ID_EXAMPLE
        )
    }

    return entity_schema


def build_sta_collection_response_schema(
    entity_type: EntityType,
    entity_response_schema: type[BaseEntitySchema]
) -> type[BaseCollectionSchema]:
    """
    Build and return a Ninja schema class representing a collection
    response for a SensorThings entity.

    The generated schema wraps a list of entity response schemas in the standard
    SensorThings collection envelope, including count and pagination fields, and
    is parameterized by the provided entity response schema type.
    """

    namespace = {
        "__annotations__": {},
        "__doc__": f"GET response schema representing a collection of `{entity_type.name}` entities."
    }

    collection_schema = cast(
        type[BaseCollectionSchema],
        type(
            f"{entity_type.name}CollectionResponse",
            (BaseCollectionSchema[entity_response_schema],),
            namespace
        )
    )

    self_link = build_self_link(
        entity_type.set_name,
        app_settings.ID_EXAMPLE
    )

    collection_schema.model_fields["iot_next_link"].json_schema_extra = {
        "example": build_next_link(
            nav_link=self_link,
            query_parameters={}
        )
    }

    return collection_schema


def build_sta_post_body_schema(
    entity_type: EntityType,
    entity_fields_schema: type[Schema]
) -> type[BaseSchema]:
    """
    Build and return a Ninja schema class for POST requests that create a
    SensorThings entity.

    The generated schema subclasses the provided entity fields schema and defines
    required relationship fields for single-related entities and optional fields
    for related entity collections. Related entities may be referenced either by
    identifier or by an embedded POST body schema.
    """

    namespace = {
        "__annotations__": {},
        "__doc__": f"POST body schema for creating a new `{entity_type.name}` entity."
    }

    for related_entity_type_name in entity_type.related_entity_type_names:
        property_name = to_snake(related_entity_type_name)

        namespace["__annotations__"][property_name] = Union[IdSchema, f"{related_entity_type_name}PostBody"]
        namespace[property_name] = Field(..., alias=related_entity_type_name)

    for related_entity_type_set_name in entity_type.related_entity_type_set_names:
        property_name = to_snake(related_entity_type_set_name)
        related_entity_type = sta.get_entity_type(related_entity_type_set_name)

        namespace["__annotations__"][property_name] = list[
            Union[IdSchema, f"{related_entity_type.name}PostBody"]
        ]
        namespace[property_name] = Field(Absent, alias=related_entity_type.set_name)

    return cast(
        type[BaseSchema],
        type(
            f"{entity_type.name}PostBody",
            (entity_fields_schema,),
            namespace
        )
    )


def build_sta_patch_body_schema(
    entity_type: EntityType,
    entity_fields_schema: type[Schema]
) -> type[BaseSchema]:
    """
    Build and return a Ninja schema class for PATCH requests on a SensorThings entity.

    The generated schema subclasses the provided entity fields schema and defines
    optional relationship fields for all related entity types. All fields default
    to `Absent`, allowing clients to supply only the fields they intend to update.
    """

    namespace = {
        "__annotations__": {},
        "__doc__": f"PATCH body schema for partially updating `{entity_type.name}` entities."
    }

    for related_entity_type_name in entity_type.related_entity_type_names:
        property_name = to_snake(related_entity_type_name)

        namespace["__annotations__"][property_name] = IdSchema
        namespace[property_name] = Field(Absent, alias=related_entity_type_name)

    return cast(
        type[BaseSchema],
        PartialMetaclass(
            f"{entity_type.name}PatchBody",
            (entity_fields_schema,),
            namespace
        )
    )
