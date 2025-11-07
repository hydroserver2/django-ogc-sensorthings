from __future__ import annotations
from abc import ABC
from typing import Any, TYPE_CHECKING
from pydantic.alias_generators import to_snake
from odata_query.ast import _Node  # noqa
from odata_query.grammar import ODataParser, ODataLexer
from odata_query.exceptions import ODataException
from django.http import HttpRequest
from sensorthings.v1_1.conf import app_settings
from sensorthings.v1_1.core.dto import BaseEntityDTO, QueryDTO, OrderByField, OrderByDirection

if TYPE_CHECKING:
    from . import SensorThingsService

lexer = ODataLexer()
parser = ODataParser()


class BaseHandler(ABC):
    service: SensorThingsService

    primitive_fields: list[str]
    complex_fields: list[str]
    related_entities: list[str]
    related_collections: list[str]

    def __init__(self, service: SensorThingsService):
        self.service = service

    async def get_collection(
        self,
        select_query: str | None = None,
        expand_query: str | None = None,
        filter_query: str | None = None,
        count_query: bool = False,
        orderby_query: str | None = None,
        skip_query: int = 0,
        top_query: int = 100,
        context: HttpRequest | Any = None
    ):
        """"""

        query_dto = self.parse_query_parameters(
            select_query=select_query,
            expand_query=expand_query,
            filter_query=filter_query,
            count_query=count_query,
            orderby_query=orderby_query,
            skip_query=skip_query,
            top_query=top_query,
        )

        return {"value": []}

    async def get_entity(
        self,
        iot_id: app_settings.ID_TYPE,
        select_query: str | None = None,
        expand_query: str | None = None,
    ):
        """"""

        query_dto = self.parse_query_parameters(
            select_query=select_query,
            expand_query=expand_query,
        )

        return {}

    async def create_entity(
        self,
        entity_payload: type(BaseEntityDTO)
    ):
        """"""

    async def update_entity(
        self,
        iot_id: app_settings.ID_TYPE,
        entity_payload: type(BaseEntityDTO)
    ):
        """"""

    async def delete_entity(
        self,
        iot_id: app_settings.ID_TYPE,
    ):
        """"""

    def parse_query_parameters(
        self,
        select_query: str | None = None,
        expand_query: str | None = None,
        filter_query: str | None = None,
        count_query: bool | None = None,
        orderby_query: str | None = None,
        skip_query: int | None = None,
        top_query: int | None = None,
    ) -> QueryDTO:
        """"""

        query_map = {
            "select": (select_query, self.parse_select_query),
            "expand": (expand_query, self.parse_expand_query),
            "filter": (filter_query, self.parse_filter_query),
            "count": (count_query, None),
            "order_by": (orderby_query, self.parse_orderby_query),
            "skip": (skip_query, None),
            "top": (top_query, None),
        }

        return QueryDTO(**{
            key: parse_fn(value) if parse_fn else value
            for key, (value, parse_fn) in query_map.items()
            if value
        })

    def parse_select_query(self, select_query: str) -> list[str]:
        """"""

        select_fields = list(dict.fromkeys([
            field.strip() for field in select_query.split(",") if field.strip()
        ]))

        allowed_fields = set(
            self.primitive_fields +
            self.complex_fields +
            self.related_entities +
            self.related_collections
        )

        invalid_fields = [f for f in select_fields if f not in allowed_fields]

        if invalid_fields:
            raise ValueError(f"Invalid fields in $select: {', '.join(invalid_fields)}")

        return [
            "iot_id" if field == "id" else to_snake(field) for field in select_fields
        ]

    def parse_expand_query(self, expand_query: str) -> dict[str, QueryDTO]:
        """"""

    def parse_filter_query(self, filter_query: str) -> _Node:
        """"""

        try:
            return parser.parse(lexer.tokenize(filter_query.strip()))
        except ODataException as e:
            raise ValueError(f"Invalid $filter: {str(e)}")

    def parse_orderby_query(self, orderby_query: str) -> list[OrderByField]:
        """"""

        parsed_orderby: list[OrderByField] = []

        for part in map(str.strip, orderby_query.split(",")):
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

            orderby_path = tokens[0].split("/")

            if not self.validate_field_path(orderby_path):
                raise ValueError(f"Invalid $orderby: '{orderby_path}'")

            parsed_orderby.append(OrderByField(path=orderby_path, direction=direction))

        return parsed_orderby

    def validate_field_path(self, path: list[str]):
        """"""

        if len(path) == 1 and path[0] in self.primitive_fields:
            return True
        elif len(path) > 1 and path[0] in self.complex_fields:
            return True
        elif (len(path) > 1 and path[0] in self.related_entities and
              self.get_entity_handler(path[0]).validate_field_path(path[1:])):
            return True
        else:
            return False

    def get_entity_handler(self, entity_name: str):
        """"""

        entity_handler_map = {
            "Things": self.service.things, "Thing": self.service.things,
            "Locations": self.service.locations, "Location": self.service.locations,
            "HistoricalLocations": self.service.historical_locations,
            "HistoricalLocation": self.service.historical_locations,
            "Datastreams": self.service.datastreams, "Datastream": self.service.datastreams,
            "Sensors": self.service.sensors, "Sensor": self.service.sensors,
            "ObservedProperties": self.service.observed_properties,
            "ObservedProperty": self.service.observed_properties,
            "Observations": self.service.observations, "Observation": self.service.observations,
            "FeaturesOfInterest": self.service.features_of_interest,
            "FeatureOfInterest": self.service.features_of_interest,
        }

        return entity_handler_map.get(entity_name)

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