from __future__ import annotations
import re
from abc import ABC
from typing import Any, TYPE_CHECKING
from pydantic.alias_generators import to_snake
from odata_query.ast import _Node  # noqa
from odata_query.grammar import ODataParser, ODataLexer
from odata_query.exceptions import ODataException
from django.http import HttpRequest
from sensorthings.types import Absent
from sensorthings.v1_1.conf import app_settings
from sensorthings.v1_1.core import iot
from sensorthings.v1_1.core.dto import (
    BaseEntityDTO,
    OrderByField,
    OrderByDirection,
)

if TYPE_CHECKING:
    from . import SensorThingsService

lexer = ODataLexer()
parser = ODataParser()


class BaseHandler(ABC):
    service: SensorThingsService

    entity_name: str
    primitive_properties: list[str]
    complex_properties: list[str]
    related_entities: list[str]
    related_collections: list[str]

    def __init__(self, service: SensorThingsService):
        self.service = service

    async def get_collection(
        self,
        select: str | None = None,
        expand: str | None = None,
        filters: str | None = None,
        order_by: str | None = None,
        count: bool = False,
        skip: int = 0,
        top: int = 100,
        group_by: str | None = None,
        context: HttpRequest | Any = None,
    ) -> dict:
        """"""

        validated_select = self.parse_select(select) if select else None
        validated_expand = self.parse_expand(expand) if expand else None
        validated_filters = self.parse_filters(filters) if filters else None
        validated_order_by = self.parse_order_by(order_by) if order_by else None

        fields = validated_select or (*self.primitive_properties, *self.complex_properties)
        fields = ["iot_id" if field == "id" else field for field in fields]

        related_nav_links = {
            field: f"{to_snake(field)}_link"
            for field in self.related_collections + self.related_entities
            if not validated_expand or field not in validated_expand.keys()
        } if not validated_select else {}

        related_entities = {
            expand_entity: await self.service.get_entity_handler(expand_entity).get_collection(
                context=context,
                group_by=expand_entity,
                **expand_params,
            ) for expand_entity, expand_params in validated_expand.items()
        }

        collection_group = await self.service.backend.get_things(
            select=validated_select,
            filters=validated_filters,
            order_by=validated_order_by,
            count=True,
            skip=skip,
            top=top,
            group_by=group_by,
            context=context,
        )

        if not group_by:
            collection_group = {self.entity_name: collection_group}

        responses = {}

        for entity, collection in collection_group.items():
            response = {"value": [
                {
                    field: value
                    for field in fields
                    if (value := getattr(entity, field, None)) is not (None or Absent)
                }
                | {
                    field: iot.build_nav_link(
                        self.entity_name, entity.iot_id, related_entity
                    )
                    for related_entity, field in related_nav_links.items()
                }
                | {
                    to_snake(k): v
                    for field, data in ((f, v.get(entity.iot_id, {})) for f, v in related_entities.items())
                    for k, v in (
                            [(field, data.get("value", []))] +
                            ([(f"{field}_count", data["iot_count"])] if "iot_count" in data else []) +
                            ([(f"{field}_next_link", data["iot_next_link"])] if "iot_next_link" in data else [])
                    )
                }
                for entity in collection.value
            ]}

            if count:
                response["iot_count"] = collection.iot_count or len(response["value"])

            if collection.iot_count and skip + top < collection.iot_count:
                response["iot_next_link"] = iot.build_next_link(
                    relative_path=next(iter(context.path.split("v1.1/", 1)[1:]), ""),
                    query_parameters=context.GET.dict()
                )

            responses[entity] = response

        return responses if group_by else next(iter(responses.values()))

    async def get_entity(
        self,
        entity_id: app_settings.ID_TYPE,
        select: str | None = None,
        expand: str | None = None,
        context: HttpRequest | Any = None,
    ) -> dict:
        """"""

        validated_select = self.parse_select(select)
        validated_expand = self.parse_expand(expand)

        return {}

    async def create_entity(
        self, entity_payload: type(BaseEntityDTO), context: HttpRequest | Any = None
    ):
        """"""

    async def update_entity(
        self,
        entity_id: app_settings.ID_TYPE,
        entity_payload: type(BaseEntityDTO),
        context: HttpRequest | Any = None,
    ):
        """"""

    async def delete_entity(
        self, entity_id: app_settings.ID_TYPE, context: HttpRequest | Any = None
    ):
        """"""

    def parse_select(self, select: str) -> list[str]:
        """"""

        selected_fields = list(
            dict.fromkeys(
                [field.strip() for field in select.split(",") if field.strip()]
            )
        )

        allowed_fields = set(
            self.primitive_properties
            + self.complex_properties
            + self.related_entities
            + self.related_collections
        )

        invalid_fields = [f for f in selected_fields if f not in allowed_fields]

        if invalid_fields:
            raise ValueError(f"Invalid fields in $select: {', '.join(invalid_fields)}")

        return [
            "iot_id" if field == "id" else to_snake(field) for field in selected_fields
        ]

    def parse_expand(self, expand: str) -> dict[str, dict]:
        """"""

        validated_expand = {}

        parsed_entities = set()
        allowed_entities = set(
            self.related_entities + self.related_collections
        )

        for expand_part in re.findall(r'[^,()]+(?:\([^()]*\))?(?:/[^,()]+(?:\([^()]*\))?)*', expand):
            nested_parts = re.split(r'/(?![^(]*\))', expand_part)
            match = re.match(r"(?P<entity>[^(]+)(?:\((?P<params>.+)\))?", nested_parts[0])

            entity = match.group("entity").strip()
            raw_query_parameters_str = params.split(";") if (params := match.group("params")) else []

            if not all(param.count("=") == 1 for param in raw_query_parameters_str):
                raise ValueError(f"Invalid query parameters in $expand: {';'.join(raw_query_parameters_str)}")

            raw_query_parameters = dict(param.split("=", 1) for param in raw_query_parameters_str)

            if entity not in allowed_entities:
                raise ValueError(f"Invalid entity in $expand: {entity}")

            if entity in parsed_entities:
                raise ValueError(f"Duplicate entity in $expand: {entity}")
            else:
                parsed_entities.add(str(entity))

            validated_expand[str(entity)] = {
                "select": raw_query_parameters.get("$select", Absent),
                "expand": "/".join(nested_parts[1:]) or Absent,
                "filters": raw_query_parameters.get("$filter", Absent),
                "count": raw_query_parameters.get("$count", Absent),
                "order_by": raw_query_parameters.get("$orderby", Absent),
                "skip": raw_query_parameters.get("$skip", Absent),
                "top": raw_query_parameters.get("$top", Absent),
            }

        return validated_expand

    @staticmethod
    def parse_filters(filters: str) -> _Node:
        """"""

        try:
            return parser.parse(lexer.tokenize(filters.strip()))
        except ODataException as e:
            raise ValueError(f"Invalid $filter: {str(e)}")

    def parse_order_by(self, order_by: str) -> list[OrderByField]:
        """"""

        parsed_order_by: list[OrderByField] = []

        for part in map(str.strip, order_by.split(",")):
            if not part:
                continue

            tokens = part.split()
            if len(tokens) not in (1, 2):
                raise ValueError(f"Invalid $orderby segment: '{part}'")

            direction = OrderByDirection.ASC
            if len(tokens) == 2:
                try:
                    direction = OrderByDirection(tokens[1].lower())
                except ValueError:
                    raise ValueError(f"Invalid $orderby direction: '{part}'")

            order_by_path = tokens[0].split("/")

            if not self.validate_field_path(order_by_path):
                raise ValueError(f"Invalid $orderby: '{order_by_path}'")

            parsed_order_by.append(
                OrderByField(path=order_by_path, direction=direction)
            )

        return parsed_order_by

    def validate_field_path(self, path: list[str]):
        """"""

        if len(path) == 1 and path[0] in self.primitive_properties:
            return True
        elif len(path) > 1 and path[0] in self.complex_properties:
            return True
        elif (
            len(path) > 1
            and path[0] in self.related_entities
            and self.service.get_entity_handler(path[0]).validate_field_path(path[1:])
        ):
            return True
        else:
            return False

    # def build_response(
    #     self,
    #     select: Optional[List[str]] = None,
    #     expand: Optional[Dict[str, Union["CollectionDTO", "BaseEntityDTO"]]] = None,
    # ):
    #     select_set = set(select or [])
    #     expand_keys = set(expand or {})
    #
    #     for related_entity in self._related_entities:
    #         related_entity_ref = to_snake(related_entity)
    #         related_entity_link_ref = f"{related_entity_ref}_link"
    #         related_nav_link = iot.build_nav_link(
    #             self._entity, self.iot_id, related_entity
    #         )
    #
    #         if (
    #             not select_set or related_entity_link_ref in select_set
    #         ) and related_entity_ref not in expand_keys:
    #             setattr(self, related_entity_link_ref, related_nav_link)
    #
    #         if related_entity_ref in expand_keys:  # TODO
    #             setattr(
    #                 self,
    #                 f"{related_entity_ref}_count",
    #                 expand[related_entity_ref]["count"],
    #             )
    #             setattr(self, related_entity_ref, expand[related_entity_ref]["value"])
    #             setattr(
    #                 self,
    #                 f"{related_entity_ref}_next_link",
    #                 f"{related_nav_link}?$skip=100&$top=100",
    #             )
    #
    #     if select_set:
    #         for f in fields(self):
    #             if f.name not in select_set:
    #                 setattr(self, f.name, Absent)

    # def build_response(self):  # TODO
    #     setattr(
    #         self, "iot_next_link", "http://www.example.com/replace?$top=100&$skip=100"
    #     )
    #
    #     for entity in self.value:
    #         entity.build_response()
