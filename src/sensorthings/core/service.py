import inspect
import re
from typing import Any, Callable
from django.http import HttpRequest
from asgiref.sync import sync_to_async
from pydantic.alias_generators import to_snake
from sensorthings.core.protocol import BaseProtocol
from sensorthings.types import Absent, EntityType
from sensorthings.http import (build_self_link, build_nav_link, build_next_link, validate_select, validate_expand,
                               validate_orderby, validate_filters)


class SensorThingsService:

    def __init__(self, protocol: type[BaseProtocol], settings, get_backend_adapter: Callable):
        self._backend_adapter = None
        self._get_backend_adapter = get_backend_adapter
        self._post_create_hooks: list[tuple[Callable, list | None]] = []
        self._post_update_hooks: list[tuple[Callable, list | None]] = []
        self._post_delete_hooks: list[tuple[Callable, list | None]] = []

        self.protocol = protocol
        self.settings = settings

        delimiter = settings.ID_DELIMITER or ""
        delimiter_re = re.escape(delimiter)

        if delimiter:
            id_re = rf"{delimiter_re}(?P<id>[^{delimiter_re}()]+){delimiter_re}"
        else:
            id_re = rf"(?P<id>[^()]+)"

        self._segment_re = re.compile(
            rf"^(?P<entity_type>[A-Za-z][A-Za-z0-9]*)"
            rf"(?:\({id_re}\))?$"
        )

    def register_post_create_hook(self, hook: Callable, entity_types: list | None = None) -> None:
        """Register a hook to be called after an entity is created. Pass `entity_types` to limit to specific types."""
        self._post_create_hooks.append((hook, entity_types))

    def register_post_update_hook(self, hook: Callable, entity_types: list | None = None) -> None:
        """Register a hook to be called after an entity is updated. Pass `entity_types` to limit to specific types."""
        self._post_update_hooks.append((hook, entity_types))

    def register_post_delete_hook(self, hook: Callable, entity_types: list | None = None) -> None:
        """Register a hook to be called after an entity is deleted. Pass `entity_types` to limit to specific types."""
        self._post_delete_hooks.append((hook, entity_types))

    @property
    def backend_adapter(self):
        """Lazily instantiate and return the configured backend adapter."""
        if self._backend_adapter is None:
            self._backend_adapter = self._get_backend_adapter()

        return self._backend_adapter

    async def run_adapter_operation(self, method: str, entity_type: EntityType, **kwargs):
        """Resolve and invoke a backend adapter operation, supporting both sync and async implementations."""

        operation = self.backend_adapter.resolve_operation(method, entity_type)

        if inspect.iscoroutinefunction(operation):
            result_set = await operation(**kwargs)
        else:
            result_set = await sync_to_async(
                operation,
                thread_sensitive=True,
            )(**kwargs)

        return result_set

    async def resolve_nested_entity(
        self,
        entity_type: EntityType,
        nested_payload: dict,
        context: HttpRequest,
    ) -> Any:
        """Resolve a nested entity payload to an ID, creating the entity first if a full payload is provided."""

        if set(nested_payload.keys()) == {"id"}:
            return nested_payload["id"]

        entity_results = await self.create_entity(entity_type, nested_payload, context)

        return entity_results["iot_id"]

    async def resolve_nested_entities(
        self,
        entity_type: EntityType,
        nested_list: list,
        context: HttpRequest,
    ) -> list:
        """Resolve a list of nested entity payloads to IDs via `resolve_nested_entity`."""
        return [
            await self.resolve_nested_entity(entity_type, item, context)
            for item in nested_list
        ]

    async def get_collection(
        self,
        entity_type: EntityType,
        context: HttpRequest,
        filters: str | None = None,
        count: bool | None = None,
        orderby: str | None = None,
        skip: int | None = None,
        top: int | None = None,
        select: str | None = None,
        select_extra: list[str] | None = None,
        expand: str | None = None,
        group_by: tuple[str, list] | None = None,
        next_link_target: list[str] | None = None
    ) -> dict:
        """
        Retrieve a SensorThings entity collection and construct a protocol-compliant response.

        This method validates and applies query options, delegates data retrieval to the
        configured backend adapter, and assembles a SensorThings collection response. When
        `group_by` is not provided, a single collection response is returned. When `group_by`
        is provided, the result is grouped and a mapping of group keys to collection responses
        is returned.
        """

        # ------------------------------------------------------------------
        # Validate and normalize query parameters
        # ------------------------------------------------------------------

        validated_select = validate_select(entity_type, select)
        validated_expand = validate_expand(entity_type, expand)
        validated_filters = validate_filters(filters)
        validated_orderby = validate_orderby(entity_type, self.protocol, orderby)

        top = int(top) if top is not None else 100
        skip = int(skip) if skip is not None else 0

        if next_link_target is None:
            next_link_target = []

        # ------------------------------------------------------------------
        # Resolve selected fields
        # ------------------------------------------------------------------

        if validated_select:
            selected_fields = validated_select
        else:
            selected_fields = [
                *entity_type.primitive_properties,
                *entity_type.complex_properties,
            ]

        fields = [
            to_snake(field) for field in selected_fields
        ]

        if select_extra:
            fields.extend(select_extra)

        for expand_field in validated_expand:
            expand_field_type = self.protocol.get_entity_type(expand_field)
            if expand_field_type and expand_field_type.name in entity_type.related_entity_type_names:
                if (fk_field := f"{to_snake(expand_field_type.name)}_id") not in fields:
                    fields.append(fk_field)

        # ------------------------------------------------------------------
        # Resolve navigation links
        # ------------------------------------------------------------------

        related_nav_links: dict[str, str] = {}

        if not validated_select:
            for related_entity_set in (
                entity_type.related_entity_type_set_names
                + entity_type.related_entity_type_names
            ):
                if not validated_expand or related_entity_set not in validated_expand:
                    related_nav_links[related_entity_set] = f"{to_snake(related_entity_set)}_link"

        # ------------------------------------------------------------------
        # Fetch data from backend
        # ------------------------------------------------------------------

        result_set = await self.run_adapter_operation(
            "get", entity_type, **{
                "filters": validated_filters,
                "orderby": validated_orderby,
                "select": fields,
                "group_by": group_by,
                "top": top,
                "skip": skip,
                "count": count,
                "context": context,
            }
        )

        # ------------------------------------------------------------------
        # Recursively resolve expanded related entities
        # ------------------------------------------------------------------

        related_entities: dict[str, dict] = {}

        for expand_entity_type, expand_params in validated_expand.items():
            related_entity_type = self.protocol.get_entity_type(expand_entity_type)

            if expand_entity_type in [entity_type.name for entity_type in self.protocol.entity_types.values()]:
                group_by_entity_name = to_snake(expand_entity_type)
                group_by_entity_ids = list({
                    getattr(entity, f"{group_by_entity_name}_id")
                    for entity in result_set.entities.values()
                })
            else:
                group_by_entity_name = to_snake(entity_type.name)
                group_by_entity_ids = list({
                    entity_id for collection in result_set.collections.values()
                    for entity_id in collection.entity_ids
                })

            related_entities[expand_entity_type] = await self.get_collection(
                entity_type=related_entity_type,
                context=context,
                group_by=(group_by_entity_name, group_by_entity_ids,),
                next_link_target=next_link_target + [expand_entity_type],
                **expand_params,
            )

        # ------------------------------------------------------------------
        # Build collection responses
        # ------------------------------------------------------------------

        responses: dict = {}

        for collection_id, collection in result_set.collections.items():
            collection_values = []

            for entity_id in collection.entity_ids:
                entity = result_set.entities[entity_id]

                # Primitive and complex fields
                field_values = {
                    field: value
                    for field in fields
                    if (value := getattr(entity, field, None)) not in (None, Absent)
                }

                # Navigation links
                nav_links = {
                    field: build_nav_link(
                        entity_type_set_name=entity_type.set_name,
                        iot_id=entity_id,
                        related_entity_type_name=related_entity,
                        protocol=self.protocol,
                        settings=self.settings
                    )
                    for related_entity, field in related_nav_links.items()
                }

                if not select:
                    nav_links["iot_self_link"] = build_self_link(
                        entity_type_set_name=entity_type.set_name,
                        iot_id=entity_id,
                        protocol=self.protocol,
                        settings=self.settings
                    )

                # Expanded related collections
                expanded_values = {}

                for field, expanded in related_entities.items():
                    if "__UNGROUPED__" in expanded:
                        entity_data = expanded.get("__UNGROUPED__", {})
                    else:
                        entity_data = expanded.get(entity_id, {})

                    if "__UNGROUPED__" in expanded and "value" in entity_data:
                        expanded_values[to_snake(field)] = entity_data["value"][0] if entity_data["value"] else None
                    elif "value" in entity_data:
                        expanded_values[to_snake(field)] = entity_data["value"]

                    if "iot_count" in entity_data:
                        expanded_values[f"{to_snake(field)}_count"] = entity_data["iot_count"]

                    if "iot_next_link" in entity_data:
                        expanded_values[f"{to_snake(field)}_next_link"] = entity_data["iot_next_link"]

                collection_values.append(
                    field_values | nav_links | expanded_values
                )

            responses[collection_id] = {"value": collection_values[:top]}

            if count:
                responses[collection_id]["iot_count"] = collection.entity_count

            if len(responses[collection_id]["value"]) == top:
                base_path = context.path.rsplit(f"{self.protocol.VERSION}/", 1)[-1]
                resource_url = f"{self.settings.SERVICE_URL}/{self.protocol.VERSION}/{base_path}"
                responses[collection_id][f"iot_next_link"] = build_next_link(
                    resource_url,
                    dict(context.GET),
                    next_link_target
                )

        # ------------------------------------------------------------------
        # Return grouped or ungrouped response
        # ------------------------------------------------------------------

        if group_by is None:
            return next(iter(responses.values()), {"value": []})

        return responses

    async def get_entity(
        self,
        entity_type: EntityType,
        entity_id: Any,
        context: HttpRequest,
        select: str | None = None,
        expand: str | None = None,
    ):
        """Retrieve a single entity by ID, raising `LookupError` if not found."""

        result_set = await self.get_collection(
            entity_type=entity_type,
            filters="",
            count=False,
            orderby="",
            skip=0,
            top=1,
            select=select,
            expand=expand,
            context=context,
            group_by=(to_snake(entity_type.name), [entity_id],)
        )

        if len(result_set["__UNGROUPED__"]["value"]) == 0:
            raise LookupError
        else:
            return result_set["__UNGROUPED__"]["value"][0]

    async def create_entity(
        self,
        entity_type: EntityType,
        payload: dict,
        context: HttpRequest,
    ) -> dict[str, Any]:
        """
        Create an entity from a payload dict, handling deep inserts recursively.

        FK parents are resolved first (created inline or referenced by ID). FK children that
        carry a back-reference to the new entity are deferred until after it is persisted.
        M2M relationships are resolved before the entity is created. Post-create hooks are
        called after all nested entities are written. Returns a dict with `iot_id` and
        `iot_self_link` for the created entity.
        """

        async with self.backend_adapter.transaction():

            related_entity_ids = {}
            deferred_payloads = []

            # Resolve required single related entities — FK lives on the current entity
            for related_name in entity_type.related_entity_type_names:
                if (related_dto_name := to_snake(related_name)) in payload:
                    related_type = self.protocol.get_entity_type(related_name)
                    related_entity_ids[f"{related_dto_name}_id"] = await self.resolve_nested_entity(
                        related_type, payload.pop(related_dto_name), context
                    )

            # Resolve collection related entities
            for related_set_name in entity_type.related_entity_type_set_names:
                if (related_set_dto_name := to_snake(related_set_name)) in payload:
                    related_type = self.protocol.get_entity_type(related_set_name)
                    snake_entity = to_snake(related_type.name)

                    if entity_type.name in related_type.related_entity_type_names:
                        # FK-child: the related entity carries a FK back to the current entity.
                        # Defer creation until after the current entity exists.
                        deferred_payloads.append((related_type, payload.pop(related_set_dto_name)))
                    else:
                        # M2M: resolve all items first, collect IDs, pass to DTO.
                        related_entity_ids[f"{snake_entity}_ids"] = await self.resolve_nested_entities(
                            related_type, payload.pop(related_set_dto_name), context
                        )

            dto = entity_type.build_dto(
                **{
                    to_snake(prop): value
                    for prop, value in payload.items()
                },
                **related_entity_ids
            )

            entity_ids = await self.run_adapter_operation("create", entity_type, payload=[dto], context=context)
            entity_id = entity_ids[0]

            # Create FK-child entities, injecting the newly created parent ID
            parent_ref_key = to_snake(entity_type.name)
            for related_type, nested_payloads in deferred_payloads:
                for nested_payload in nested_payloads:
                    child_payload = nested_payload if parent_ref_key in nested_payload else {
                        **nested_payload, parent_ref_key: {"id": entity_id}
                    }
                    await self.create_entity(related_type, child_payload, context)

            for hook, entity_types in self._post_create_hooks:
                if entity_types is None or entity_type in entity_types:
                    await hook(entity_type=entity_type, entity_id=entity_id, context=context)

            return {
                "iot_id": entity_id,
                "iot_self_link": build_self_link(
                    entity_type_set_name=entity_type.set_name,
                    iot_id=entity_id,
                    protocol=self.protocol,
                    settings=self.settings
                )
            }

    async def update_entity(
        self,
        entity_type: EntityType,
        entity_id: Any,
        payload: dict,
        context: HttpRequest,
    ) -> None:
        """Apply a partial update to an existing entity, resolving any FK reassignments by ID."""

        async with self.backend_adapter.transaction():

            related_entity_ids = {}

            for related_name in entity_type.related_entity_type_names:
                if (related_dto_name := to_snake(related_name)) in payload:
                    related_type = self.protocol.get_entity_type(related_name)
                    related_entity_ids[f"{related_dto_name}_id"] = await self.resolve_nested_entity(
                        related_type, payload.pop(related_dto_name), context
                    )

            dto = entity_type.build_dto(
                **{
                    to_snake(prop): value
                    for prop, value in payload.items()
                },
                **related_entity_ids
            )

            await self.run_adapter_operation(
                "update", entity_type, **{
                    "payload": {entity_id: dto},
                    "context": context,
                }
            )

    async def delete_entity(
        self,
        entity_type: EntityType,
        entity_id: Any,
        context: HttpRequest,
    ) -> None:
        """Delete an entity by ID, raising `LookupError` if it does not exist."""

        async with self.backend_adapter.transaction():
            await self.run_adapter_operation(
                "delete", entity_type,
                entity_ids=[entity_id],
                context=context,
            )

    async def resolve_entity_path(
        self,
        path_segments: list[str],
        context: HttpRequest,
        filters: str | None = None,
        count: bool | None = None,
        orderby: str | None = None,
        skip: int | None = None,
        top: int | None = None,
        select: str | None = None,
        expand: str | None = None,
        **kwargs,
    ):
        """
        Parse an OData path segment list and dispatch to `get_entity` or `get_collection`.

        Walks each segment to resolve the target entity type, ID, and operation mode. Supports
        direct collection and entity access, related entity and collection navigation, FK parent
        inference, property selection, `$value`, and `$ref`. Raises `LookupError` for invalid
        or unresolvable paths. Returns a `(result, result_type)` tuple where `result_type` is a
        string like `"thing_entity"` or `"observation_collection"`.
        """

        operation_entity_type = None
        operation_entity_id = None
        operation_group_by = None

        path_parent_entity_type = None
        path_parent_identifier = None

        selected_property = None
        value_only = False
        ref_allowed = False
        ref_only = False

        for i, segment in enumerate(path_segments):
            segment_match = self._segment_re.match(segment)

            segment_value = segment_match.group("entity_type") if segment_match else segment
            segment_identifier = segment_match.group("id") if segment_match else None
            segment_entity_type = self.protocol.get_entity_type(segment_value)

            if segment_entity_type:
                operation_entity_type = segment_entity_type

            # ------------------------------------------------------------------
            # Coerce identifier to correct type
            # ------------------------------------------------------------------

            if segment_identifier:
                try:
                    segment_identifier = self.settings.ID_TYPE(segment_identifier)
                except (TypeError, ValueError):
                    raise LookupError

            # ------------------------------------------------------------------
            # Handle first path segment
            # ------------------------------------------------------------------

            if i == 0:
                if segment_entity_type and segment_value in self.protocol.entity_types:
                    path_parent_entity_type = segment_entity_type
                    path_parent_identifier = segment_identifier
                    if segment_identifier:
                        operation_entity_id = segment_identifier
                    else:
                        ref_allowed = True
                    continue
                else:
                    raise LookupError

            # ------------------------------------------------------------------
            # Handle subsequent entity type path segments
            # ------------------------------------------------------------------

            if segment_entity_type:

                # Entity segments cannot follow non-entity or collection segments.
                if not path_parent_entity_type or not path_parent_identifier:
                    raise LookupError

                # Points to a specific entity in a related collection of the parent entities.
                if segment_identifier and segment_value in path_parent_entity_type.related_entity_type_set_names:
                    path_check_group_by = (to_snake(segment_entity_type.name), [segment_identifier],)
                    result = await self.run_adapter_operation(
                        "get",
                        segment_entity_type,
                        group_by=path_check_group_by,
                        context=context
                    )
                    if not result.entities.get(segment_identifier) or getattr(
                        result.entities[segment_identifier],
                        f"{to_snake(path_parent_entity_type.name)}_id",
                    ) != path_parent_identifier:
                        raise LookupError
                    operation_entity_id = segment_identifier
                    path_parent_identifier = segment_identifier

                # Points to a specific related entity of the parent entity by ID.
                elif segment_identifier and (
                    segment_entity_type.name in path_parent_entity_type.related_entity_type_names
                ):
                    path_check_group_by = (to_snake(path_parent_entity_type.name), [path_parent_identifier],)
                    result = await self.run_adapter_operation(
                        "get",
                        path_parent_entity_type,
                        group_by=path_check_group_by,
                        context=context
                    )
                    if not result.entities.get(path_parent_identifier) or getattr(
                        result.entities[path_parent_identifier],
                        f"{to_snake(segment_entity_type.name)}_id",
                    ) != segment_identifier:
                        raise LookupError
                    operation_entity_id = segment_identifier
                    path_parent_identifier = segment_identifier

                # Points to a collection of the parent entities.
                elif not segment_identifier and segment_value in path_parent_entity_type.related_entity_type_set_names:
                    path_check_group_by = (to_snake(path_parent_entity_type.name), [path_parent_identifier],)
                    result = await self.run_adapter_operation(
                        "get",
                        path_parent_entity_type,
                        group_by=path_check_group_by,
                        context=context
                    )
                    if not result.entities.get(path_parent_identifier):
                        raise LookupError
                    operation_entity_id = None
                    if path_parent_entity_type.set_name in segment_entity_type.related_entity_type_set_names:
                        operation_group_by = (to_snake(path_parent_entity_type.set_name), [path_parent_identifier],)
                    else:
                        operation_group_by = path_check_group_by
                    path_parent_identifier = None
                    ref_allowed = True

                # Points to a specific related entity of the parent entity (inferred).
                elif not segment_identifier and segment_value in path_parent_entity_type.related_entity_type_names:
                    related_entity_id_field = f"{to_snake(segment_entity_type.name)}_id"
                    result = await self.run_adapter_operation(
                        "get",
                        path_parent_entity_type,
                        select=[related_entity_id_field],
                        group_by=(to_snake(path_parent_entity_type.name), [path_parent_identifier],),
                        context=context
                    )
                    if not result.entities.get(path_parent_identifier):
                        raise LookupError
                    segment_identifier = getattr(
                        result.entities[path_parent_identifier],
                        related_entity_id_field,
                    )
                    operation_entity_id = segment_identifier
                    path_parent_identifier = segment_identifier
                    ref_allowed = True

                else:
                    raise LookupError

                path_parent_entity_type = segment_entity_type
                continue

            # ------------------------------------------------------------------
            # Handle property navigation
            # ------------------------------------------------------------------

            elif value_only or ref_only:
                raise LookupError

            elif to_snake(segment_value) in path_parent_entity_type.properties:
                if selected_property or not operation_entity_id:
                    raise LookupError
                else:
                    selected_property = segment_value
                    continue

            elif selected_property and segment_value == "$value":
                value_only = True
                continue

            elif ref_allowed and segment_value == "$ref":
                ref_only = True
                continue

            else:
                raise LookupError

        # ------------------------------------------------------------------
        # Run resolved operation
        # ------------------------------------------------------------------

        if selected_property or ref_only or value_only:
            if any({filters, count, orderby, skip, top, select, expand}):
                raise ValueError

            if selected_property:
                select = selected_property

        if operation_entity_id:
            result = await self.get_entity(
                entity_type=operation_entity_type,
                entity_id=operation_entity_id,
                select=select,
                expand=expand,
                context=context,
            )
        else:
            result = await self.get_collection(
                entity_type=operation_entity_type,
                filters=filters,
                count=count,
                orderby=orderby,
                skip=skip,
                top=top,
                select=select,
                expand=expand,
                group_by=operation_group_by,
                context=context,
                **kwargs
            )

            if operation_group_by:
                result = next(iter(result.values()), {"value": []})

        if ref_only:
            result["value"] = [{"iot_self_link": entity["iot_self_link"]} for entity in result["value"]]

        response_type = "collection" if not operation_entity_id else "entity"

        return result, f"{to_snake(operation_entity_type.name)}_{response_type}"
