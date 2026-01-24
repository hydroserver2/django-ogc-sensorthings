import re
import inspect
from django.http import HttpRequest
from asgiref.sync import sync_to_async
from pydantic import BaseModel
from pydantic.alias_generators import to_snake
from odata_query.ast import _Node  # noqa
from odata_query.grammar import ODataParser, ODataLexer
from odata_query.exceptions import ODataException
from sensorthings.types import Absent
from sensorthings.v1_1.conf import app_settings
from sensorthings.v1_1.backends import get_backend_adapter
from sensorthings.v1_1.protocol import sta, EntityType
from sensorthings.v1_1.dto import OrderByField, OrderByDirection
from sensorthings.v1_1.http import build_nav_link, build_next_link

lexer = ODataLexer()
parser = ODataParser()


class SensorThingsService:
    """SensorThings v1.1 service layer."""

    def __init__(self):
        self.backend_adapter = get_backend_adapter()

    async def get_collection(
        self,
        entity_type: EntityType,
        filters: str,
        count: bool,
        order_by: str,
        skip: int,
        top: int,
        select: str,
        expand: str,
        context: HttpRequest,
        group_by: str | None = None,
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

        validated_select = self.parse_select(entity_type, select)
        validated_expand = self.parse_expand(entity_type, expand)
        validated_filters = self.parse_filters(filters)
        validated_order_by = self.parse_order_by(entity_type, order_by)

        if top is Absent:
            top = 100

        if skip is Absent:
            skip = 0

        # ------------------------------------------------------------------
        # Resolve selected fields
        # ------------------------------------------------------------------

        if validated_select:
            selected_fields = validated_select
        else:
            selected_fields = (
                *entity_type.primitive_properties,
                *entity_type.complex_properties,
            )

        fields = [
            "iot_id" if field == "id" else to_snake(field)
            for field in selected_fields
        ]

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
        # Recursively resolve expanded related entities
        # ------------------------------------------------------------------

        related_entities: dict[str, dict] = {}

        for expand_entity_type, expand_params in validated_expand.items():
            related_entities[expand_entity_type] = await self.get_collection(
                entity_type=sta.get_entity_type(expand_entity_type),
                context=context,
                group_by=expand_entity_type,
                **expand_params,
            )

        # ------------------------------------------------------------------
        # Fetch data from backend
        # ------------------------------------------------------------------

        operation = self.backend_adapter.resolve_operation("get", entity_type)
        operation_kwargs = {
            "filters": validated_filters,
            "order_by": validated_order_by,
            "select": validated_select,
            "top": top,
            "skip": skip,
            "count": count,
            "context": context,
        }

        if inspect.iscoroutinefunction(operation):
            result_set = await operation(**operation_kwargs)
        else:
            result_set = await sync_to_async(
                operation,
                thread_sensitive=True,
            )(**operation_kwargs)

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
                        entity_type.name,
                        entity_id,
                        related_entity,
                    )
                    for related_entity, field in related_nav_links.items()
                }

                # Expanded related collections
                expanded_values = {}

                for field, expanded in related_entities.items():
                    entity_data = expanded.get(entity_id, {})

                    if "value" in entity_data:
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
                responses[collection_id][f"iot_next_link"] = build_next_link(
                    context.path.rsplit(f"{sta.VERSION}/", 1)[-1],
                    context.GET
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
        entity_id: app_settings.ID_TYPE,
        select: str,
        expand: str,
        context: HttpRequest
    ):
        """"""

    async def create_entity(
        self,
        entity_type: EntityType,
        payload: BaseModel,
        context: HttpRequest
    ):
        """"""

    async def update_entity(
        self,
        entity_type: EntityType,
        entity_id: app_settings.ID_TYPE,
        payload: BaseModel,
        context: HttpRequest
    ):
        """"""

    async def delete_entity(
        self,
        entity_type: EntityType,
        entity_id: app_settings.ID_TYPE,
        context: HttpRequest
    ):
        """"""

    @staticmethod
    def parse_select(
        entity_type: EntityType,
        select: str | None = None
    ) -> list[str] | None:
        """
        Parse and validate a $select clause for a given entity type.

        This method validates selected fields against the entity's allowed
        primitive, complex, and navigation properties, and normalizes field
        names to their internal representation.
        """

        if not select:
            return None

        # ------------------------------------------------------------------
        # Parse and deduplicate selected fields
        # ------------------------------------------------------------------

        selected_fields = list(
            dict.fromkeys(
                field.strip()
                for field in select.split(",")
                if field.strip()
            )
        )

        # ------------------------------------------------------------------
        # Determine allowed fields
        # ------------------------------------------------------------------

        allowed_fields = {
            *entity_type.primitive_properties,
            *entity_type.complex_properties,
            *entity_type.related_entity_type_names,
            *entity_type.related_entity_type_set_names,
        }

        # ------------------------------------------------------------------
        # Validate selection
        # ------------------------------------------------------------------

        invalid_fields = [
            field for field in selected_fields
            if field not in allowed_fields
        ]

        if invalid_fields:
            raise ValueError(
                f"Invalid fields in $select: {', '.join(invalid_fields)}"
            )

        # ------------------------------------------------------------------
        # Normalize field names
        # ------------------------------------------------------------------

        return [
            "iot_id" if field == "id" else to_snake(field)
            for field in selected_fields
        ]

    @staticmethod
    def parse_expand(
        entity_type: EntityType,
        expand: str | None = None,
    ) -> dict[str, dict]:
        """
        Parse and validate an $expand clause for a given entity type.

        This method validates expanded navigation properties against the entity's
        related entity types and entity sets, parses nested expansions and query
        options, and returns a normalized structure suitable for recursive
        expansion processing.
        """

        if not expand:
            return {}

        validated_expand: dict[str, dict] = {}
        parsed_entities: set[str] = set()

        allowed_entities = {
            *entity_type.related_entity_type_names,
            *entity_type.related_entity_type_set_names,
        }

        # ------------------------------------------------------------------
        # Split top-level expand components
        # ------------------------------------------------------------------

        expand_parts = re.findall(
            r"[^,()]+(?:\([^()]*\))?(?:/[^,()]+(?:\([^()]*\))?)*",
            expand,
        )

        for expand_part in expand_parts:

            # Split nested expansions (Thing/Datastreams/Observations)
            nested_parts = re.split(r"/(?![^(]*\))", expand_part)

            match = re.match(
                r"(?P<entity>[^(]+)(?:\((?P<params>.+)\))?",
                nested_parts[0],
            )

            if not match:
                raise ValueError(f"Invalid $expand syntax: {expand_part}")

            entity = match.group("entity").strip()
            params_str = match.group("params")

            # ------------------------------------------------------------------
            # Validate entity
            # ------------------------------------------------------------------

            if entity not in allowed_entities:
                raise ValueError(f"Invalid entity in $expand: {entity}")

            if entity in parsed_entities:
                raise ValueError(f"Duplicate entity in $expand: {entity}")

            parsed_entities.add(entity)

            # ------------------------------------------------------------------
            # Parse query parameters
            # ------------------------------------------------------------------

            raw_params = params_str.split(";") if params_str else []

            if not all(param.count("=") == 1 for param in raw_params):
                raise ValueError(
                    f"Invalid query parameters in $expand: {';'.join(raw_params)}"
                )

            query_params = dict(param.split("=", 1) for param in raw_params)

            # ------------------------------------------------------------------
            # Store normalized expansion definition
            # ------------------------------------------------------------------

            validated_expand[entity] = {
                "select": query_params.get("$select", Absent),
                "expand": "/".join(nested_parts[1:]) or Absent,
                "filters": query_params.get("$filter", Absent),
                "count": query_params.get("$count", Absent),
                "order_by": query_params.get("$orderby", Absent),
                "skip": query_params.get("$skip", Absent),
                "top": query_params.get("$top", Absent),
            }

        return validated_expand

    def parse_order_by(
        self,
        entity_type: EntityType,
        order_by: str | None = None,
    ) -> list[OrderByField] | None:
        """
        Parse and validate an $orderby clause for a given entity type.

        This method validates each order-by segment, resolves sort direction,
        verifies that the referenced property path is valid for the entity type,
        and returns a normalized list of OrderByField objects.
        """

        if not order_by:
            return None

        parsed_order_by: list[OrderByField] = []

        # ------------------------------------------------------------------
        # Split and parse order-by segments
        # ------------------------------------------------------------------

        for segment in (part.strip() for part in order_by.split(",")):
            if not segment:
                continue

            tokens = segment.split()

            if len(tokens) not in (1, 2):
                raise ValueError(f"Invalid $orderby segment: '{segment}'")

            # ------------------------------------------------------------------
            # Resolve sort direction
            # ------------------------------------------------------------------

            field_token = tokens[0]
            direction = OrderByDirection.ASC

            if len(tokens) == 2:
                try:
                    direction = OrderByDirection(tokens[1].lower())
                except ValueError:
                    raise ValueError(f"Invalid $orderby direction: '{segment}'")

            # ------------------------------------------------------------------
            # Validate field path
            # ------------------------------------------------------------------

            field_path = field_token.split("/")

            if not self.validate_field_path(entity_type, field_path):
                raise ValueError(f"Invalid $orderby field path: '{field_token}'")

            parsed_order_by.append(
                OrderByField(
                    path=field_path,
                    direction=direction,
                )
            )

        return parsed_order_by

    @staticmethod
    def parse_filters(filters: str | None = None) -> _Node | None:
        """
        Parse and validate an OData $filter string into an abstract syntax tree.

        Returns a parse tree representing the filter expression, suitable for
        downstream evaluation by the backend adapter. Returns None if no filter
        string is provided.
        """

        if not filters:
            return None

        try:
            return parser.parse(lexer.tokenize(filters.strip()))
        except ODataException as e:
            raise ValueError(f"Invalid $filter: {str(e)}")

    def validate_field_path(self, entity_type: EntityType, path: list[str]) -> bool:
        """
        Validate that a field path is valid for a given entity type.

        A path is valid if it references:
            1. A single primitive property, or
            2. A nested property of a complex type, or
            3. A navigation through related entity types where each step is valid.
        """

        if len(path) == 1 and path[0] in entity_type.primitive_properties:
            return True
        elif len(path) > 1 and path[0] in entity_type.complex_properties:
            return True
        elif (
            len(path) > 1
            and path[0] in entity_type.related_entity_type_names
            and self.validate_field_path(sta.get_entity_protocol(path[0]), path[1:])
        ):
            return True
        else:
            return False


sensorthings_service = SensorThingsService()
