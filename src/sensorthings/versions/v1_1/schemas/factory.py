from typing import Union, cast
from ninja import Field
from pydantic.alias_generators import to_snake
from sensorthings.types import Absent, EntityType
from sensorthings.http import build_self_link, build_nav_link, build_next_link
from sensorthings.versions.v1_1 import STA, app_settings
from .base import IdSchema, BaseSchema, BaseEntitySchema, PartialMetaclass, BaseCollectionSchema


class SchemaFactory:
    """
    Builds and caches SensorThings v1.1 Ninja schema classes.

    Holds a `fields_registry` mapping entity names to their base field schemas and
    internal caches to ensure each generated schema class is created exactly once.
    Extensions register new entity field schemas via `register` before building.
    """

    def __init__(self, fields_registry: dict[str, type]):
        self.fields_registry = fields_registry
        self._response_cache: dict[str, type[BaseEntitySchema]] = {}
        self._collection_cache: dict[str, type[BaseCollectionSchema]] = {}
        self._post_body_cache: dict[tuple, type[BaseSchema]] = {}
        self._patch_body_cache: dict[str, type[BaseSchema]] = {}

    def register(self, entity_name: str, fields_class: type) -> None:
        """Add or replace an entity's fields class in the registry."""

        self.fields_registry[entity_name] = fields_class

    def all_schemas(self) -> dict[str, type[BaseSchema]]:
        """
        Return all response and POST body schemas keyed by class name, for use with `model_rebuild`.

        Patch body schemas are excluded: they have no forward references and are rebuilt immediately
        inside `build_patch_body` with `force=True`, so including them here would re-read the
        original class body and undo the Absent defaults.
        """

        return {
            **{s.__name__: s for s in self._response_cache.values()},
            **{s.__name__: s for s in self._post_body_cache.values()},
        }

    def build_entity_response(self, entity_type: EntityType) -> type[BaseEntitySchema]:
        """
        Build and return a Ninja schema class representing a single SensorThings
        entity response.

        The generated schema combines the entity's core fields with standard
        SensorThings response elements, including navigation links, related entity
        references, and embedded collections where applicable. All related fields
        are optional and marked as absent by default to support partial responses
        and `$expand`/`$select` semantics. Results are cached by entity name.
        """

        if entity_type.name in self._response_cache:
            return self._response_cache[entity_type.name]

        entity_fields_schema = self.fields_registry[entity_type.name]
        namespace = {
            "__annotations__": {},
            "__doc__": f"GET response schema representing a `{entity_type.name}` entity."
        }

        for related_entity_type_name in entity_type.related_entity_type_names:
            property_name = to_snake(related_entity_type_name)
            nav_link = build_nav_link(
                entity_type_set_name=entity_type.set_name,
                iot_id=app_settings.ID_EXAMPLE,
                related_entity_type_name=related_entity_type_name,
                protocol=STA,
                settings=app_settings
            )
            namespace["__annotations__"][f"{property_name}_link"] = str
            namespace[f"{property_name}_link"] = Field(
                Absent,
                alias=related_entity_type_name + STA.NAVIGATION_LINK,
                examples=[nav_link]
            )
            # TODO: https://github.com/swagger-api/swagger-ui/issues/10583
            # WORKAROUND
            namespace["__annotations__"][property_name] = Union[f"{related_entity_type_name}Response", None]
            # CORRECT:
            # namespace["__annotations__"][property_name] = f"{related_entity_type_name}Response"
            namespace[property_name] = Field(default_factory=lambda: Absent, alias=related_entity_type_name)

        for related_entity_type_set_name in entity_type.related_entity_type_set_names:
            property_name = to_snake(related_entity_type_set_name)
            related_entity_type = STA.get_entity_type(related_entity_type_set_name)
            nav_link = build_nav_link(
                entity_type_set_name=entity_type.set_name,
                iot_id=app_settings.ID_EXAMPLE,
                related_entity_type_name=related_entity_type_set_name,
                protocol=STA,
                settings=app_settings
            )
            namespace["__annotations__"][f"{property_name}_link"] = str
            namespace[f"{property_name}_link"] = Field(
                Absent,
                alias=related_entity_type_set_name + STA.NAVIGATION_LINK,
                examples=[nav_link]
            )
            namespace["__annotations__"][f"{property_name}_count"] = int
            namespace[f"{property_name}_count"] = Field(Absent, alias=related_entity_type_set_name + STA.COUNT)
            namespace["__annotations__"][property_name] = list[f"{related_entity_type.name}Response"]
            namespace[property_name] = Field(Absent, alias=related_entity_type_set_name)
            namespace["__annotations__"][f"{property_name}_next_link"] = str
            namespace[f"{property_name}_next_link"] = Field(
                Absent,
                alias=related_entity_type_set_name + STA.NEXT_LINK,
                examples=[build_next_link(nav_link=nav_link, query_params={})]
            )

        entity_schema: type[BaseEntitySchema] = PartialMetaclass(  # type: ignore[assignment]
            f"{entity_type.name}Response",
            (entity_fields_schema, BaseEntitySchema,),
            namespace
        )
        entity_schema.model_fields["iot_self_link"].json_schema_extra = {
            "example": build_self_link(
                entity_type_set_name=entity_type.set_name,
                iot_id=app_settings.ID_EXAMPLE,
                protocol=STA,
                settings=app_settings
            )
        }

        self._response_cache[entity_type.name] = entity_schema

        return entity_schema

    def build_collection_response(self, entity_type: EntityType) -> type[BaseCollectionSchema]:
        """
        Build and return a Ninja schema class representing a collection
        response for a SensorThings entity.

        The generated schema wraps a list of entity response schemas in the standard
        SensorThings collection envelope, including count and pagination fields.
        The entity response schema is retrieved or built via `build_entity_response`.
        """

        if entity_type.name in self._collection_cache:
            return self._collection_cache[entity_type.name]

        entity_response = self.build_entity_response(entity_type)

        namespace = {
            "__annotations__": {},
            "__doc__": f"GET response schema representing a collection of `{entity_type.name}` entities."
        }

        collection_schema = cast(
            type[BaseCollectionSchema],
            type(
                f"{entity_type.name}CollectionResponse",
                (BaseCollectionSchema[entity_response],),
                namespace
            )
        )

        self_link = build_self_link(
            entity_type_set_name=entity_type.set_name,
            iot_id=app_settings.ID_EXAMPLE,
            protocol=STA,
            settings=app_settings
        )
        collection_schema.model_fields["iot_next_link"].json_schema_extra = {
            "example": build_next_link(nav_link=self_link, query_params={})
        }

        self._collection_cache[entity_type.name] = collection_schema

        return collection_schema

    def build_post_body(
        self,
        entity_type: EntityType,
        exclude: set[str] | None = None,
        parent_name: str | None = None,
    ) -> type[BaseSchema]:
        """
        Build and return a Ninja schema class for POST requests that create a
        SensorThings entity.

        Required FK-parent relationships are added as `Union[IdSchema, ParentPostBody]`
        fields; any names in `exclude` are omitted, which prevents redundant back-references
        when building deep-insert variants. Optional collection relationships use string
        forward references of the form `"{Entity}{Related}PostBody"` (one level of parent
        exclusion), resolved via `model_rebuild` after all schemas are built.

        Pass `parent_name` when building an exclusion variant — the generated class will be
        named `"{parent_name}{entity_type.name}PostBody"` and keyed in the cache under
        `(entity_type.name, frozenset(exclude))`.
        """

        cache_key = (entity_type.name, frozenset(exclude or []))
        if cache_key in self._post_body_cache:
            return self._post_body_cache[cache_key]

        entity_fields_schema = self.fields_registry[entity_type.name]
        schema_name = (
            f"{parent_name}{entity_type.name}PostBody" if parent_name
            else f"{entity_type.name}PostBody"
        )

        namespace = {
            "__annotations__": {},
            "__doc__": f"POST body schema for creating a new `{entity_type.name}` entity."
        }

        for related_entity_type_name in entity_type.related_entity_type_names:
            if exclude and related_entity_type_name in exclude:
                continue
            property_name = to_snake(related_entity_type_name)
            related_entity_type = STA.get_entity_type(related_entity_type_name)
            nested_post_body = self.build_post_body(related_entity_type)
            if related_entity_type_name in entity_type.optional_related_entity_type_names:
                namespace["__annotations__"][property_name] = Union[IdSchema, nested_post_body, None]
                namespace[property_name] = Field(None, alias=related_entity_type_name)
            else:
                namespace["__annotations__"][property_name] = Union[IdSchema, nested_post_body]
                namespace[property_name] = Field(..., alias=related_entity_type_name)

        for related_entity_type_set_name in entity_type.related_entity_type_set_names:
            property_name = to_snake(related_entity_type_set_name)
            related_entity_type = STA.get_entity_type(related_entity_type_set_name)
            nested_ref = f"{entity_type.name}{related_entity_type.name}PostBody"
            namespace["__annotations__"][property_name] = list[Union[IdSchema, nested_ref]]
            namespace[property_name] = Field(Absent, alias=related_entity_type.set_name)

        schema = cast(
            type[BaseSchema],
            type(schema_name, (entity_fields_schema,), namespace)
        )

        self._post_body_cache[cache_key] = schema

        return schema

    def build_patch_body(self, entity_type: EntityType) -> type[BaseSchema]:
        """
        Build and return a Ninja schema class for PATCH requests on a SensorThings entity.

        The generated schema subclasses the entity's fields schema and defines optional
        relationship fields for all FK-parent entity types. All fields default to `Absent`,
        allowing clients to supply only the fields they intend to update. Results are cached
        by entity name.
        """

        if entity_type.name in self._patch_body_cache:
            return self._patch_body_cache[entity_type.name]

        entity_fields_schema = self.fields_registry[entity_type.name]
        namespace = {
            "__annotations__": {},
            "__doc__": f"PATCH body schema for partially updating `{entity_type.name}` entities."
        }

        for related_entity_type_name in entity_type.related_entity_type_names:
            property_name = to_snake(related_entity_type_name)
            namespace["__annotations__"][property_name] = IdSchema
            namespace[property_name] = Field(Absent, alias=related_entity_type_name)

        schema: type[BaseSchema] = PartialMetaclass(  # type: ignore[assignment]
            f"{entity_type.name}PatchBody",
            (entity_fields_schema,),
            namespace
        )

        # model_rebuild re-reads model_fields (which PartialMetaclass set to Absent defaults),
        # compiling a core schema where all primitive fields are optional.
        # force=True is required because Pydantic marks the class complete at creation.
        schema.model_rebuild(force=True)

        self._patch_body_cache[entity_type.name] = schema

        return schema
