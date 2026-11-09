from functools import reduce
from typing import Any, Callable
from collections import defaultdict
from contextlib import asynccontextmanager
from asgiref.sync import sync_to_async
from datetime import datetime, timezone
from odata_query import ast as odata_ast
from odata_query.ast import _Node  # noqa
from odata_query.django.django_q import AstToDjangoQVisitor
from odata_query.django.django_q_ext import NotEqual
from odata_query.exceptions import ODataException, TypeException
from ninja.errors import HttpError
from django.core.exceptions import EmptyResultSet, FieldDoesNotExist, FieldError
from django.http import HttpRequest
from django.db import transaction as django_transaction
from django.db.models import (QuerySet, Manager, Count, F, Window, Model, Q, Case, When, Value, FloatField, TextField,
                              JSONField, CharField, DateTimeField, ExpressionWrapper, IntegerField, DecimalField)
from django.db.models.fields.json import KeyTextTransform, KeyTransform
from django.db.models.functions import Cast, Concat, RowNumber
from django.db.models.expressions import OrderBy
from pydantic.alias_generators import to_snake
from sensorthings.http import InvalidQueryError
from sensorthings.types import Absent, OrderByField, OrderByDirection
from sensorthings.versions.v1_1.conf import app_settings
from sensorthings.versions.v1_1.dto import (EntityResultSetDTO, CollectionDTO, ThingDTO, LocationDTO,
                                            HistoricalLocationDTO, SensorDTO, ObservedPropertyDTO,
                                            DatastreamDTO, ObservationDTO, FeatureOfInterestDTO)
from .models import (Thing, Location, HistoricalLocation, Sensor, ObservedProperty, Datastream, Observation,
                     FeatureOfInterest)
from ..base import BaseBackendAdapter


JSON_NUMBER_PATTERN = r"^-?[0-9]+(\.[0-9]+)?([eE][-+]?[0-9]+)?$"
JSON_DATETIME_PATTERN = (
    r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}(:[0-9]{2}(\.[0-9]+)?)?(Z|[-+][0-9]{2}:[0-9]{2})?$"
)
JSON_FUNCTION_TYPES = {
    "round": "number", "floor": "number", "ceiling": "number",
    "year": "datetime", "month": "datetime", "day": "datetime", "hour": "datetime",
    "minute": "datetime", "second": "datetime", "date": "datetime", "time": "datetime",
}
JSON_COMPARE_NUMBER_FUNCTIONS = {
    "year", "month", "day", "hour", "minute", "second", "round", "floor", "ceiling", "length", "indexof",
}
JSON_FLIPPED_COMPARATORS = {
    odata_ast.Gt: odata_ast.Lt, odata_ast.GtE: odata_ast.LtE, odata_ast.Lt: odata_ast.Gt, odata_ast.LtE: odata_ast.GtE,
}


def _not_equal_as_sql(self, compiler, connection):
    lhs, lhs_params = self.process_lhs(compiler, connection)
    rhs, rhs_params = self.process_rhs(compiler, connection)
    return "%s <> %s" % (lhs, rhs), (*lhs_params, *rhs_params)


# TODO: Remove once odata-query supports Django 6.0, and require that version.
# odata-query's `ne` lookup concatenates params that Django 6.0 can return as a tuple and a list.
NotEqual.as_sql = _not_equal_as_sql


class ODataToDjangoQVisitor(AstToDjangoQVisitor):
    """Extends AstToDjangoQVisitor to translate OData camelCase field names to Django snake_case."""

    _json_mode = None

    def visit_Attribute(self, node: odata_ast.Attribute):
        return self._json_value(self._field_path(node), self._json_mode)

    visit_Identifier = visit_Attribute

    def visit_BinOp(self, node: odata_ast.BinOp):
        return self._with_json_mode("number", super().visit_BinOp, node)

    def visit_Call(self, node: odata_ast.Call):
        mode = JSON_FUNCTION_TYPES.get(node.func.full_name().lower(), "text")
        return self._with_json_mode(mode, super().visit_Call, node)

    def visit_Compare(self, node: odata_ast.Compare):
        left, right, comparator = node.left, node.right, node.comparator

        if self._is_json_path(right) and not self._is_json_path(left):
            left, right = right, left
            comparator = JSON_FLIPPED_COMPARATORS.get(type(comparator), type(comparator))()

        if not self._is_json_path(left) or self._is_json_path(right):
            return super().visit_Compare(node)

        path = self._field_path(left)
        if isinstance(right, odata_ast._Literal):  # noqa
            return self._compare_json(path, comparator, right)

        mode = self._value_type(right)
        expression = self.visit(right)

        return self.visit(comparator)(
            self._json_value(path, mode), Cast(expression, TextField()) if mode == "text" else expression
        )

    def visit_CollectionLambda(self, node: odata_ast.CollectionLambda):
        result = super().visit_CollectionLambda(node)

        return ~result if isinstance(node.operator, odata_ast.All) else result

    def djangofunc_concat(self, *args: odata_ast._Node) -> Concat:  # noqa
        return Concat(*[self.visit(arg) for arg in args], output_field=TextField())

    def _with_json_mode(self, mode: str, visit: Callable, node: odata_ast._Node):  # noqa
        """Visit a node with JSON values extracted according to the given mode."""

        previous, self._json_mode = self._json_mode, mode
        result = visit(node)
        self._json_mode = previous

        return result

    def _field_path(self, node: odata_ast._Node) -> str:  # noqa
        """Build a Django field path from an OData identifier or attribute."""

        if isinstance(node, odata_ast.Identifier):
            return self._column_name(None, node.name)

        owner = self._field_path(node.owner)
        if self._json_keys(owner) is not None:
            return owner + "__" + node.attr

        return owner + "__" + self._column_name(owner, node.attr)

    def _column_name(self, owner: str | None, name: str) -> str:
        """Return the column for an OData property, using the begin column of a time interval."""

        model = self.root_model
        for part in owner.split("__") if owner else []:
            model = model._meta.get_field(part).related_model if model else None  # noqa

        name = to_snake(name)

        return f"{name}_begin" if hasattr(model, f"{name}_begin") else name

    def _json_keys(self, path: str) -> list[str] | None:
        """Return the keys below a JSONField in a Django field path, or None if it doesn't reach one."""

        model = self.root_model
        parts = path.split("__")

        for index, part in enumerate(parts):
            field = model._meta.get_field(part)  # noqa
            if isinstance(field, JSONField):
                return parts[index + 1:]
            if not field.is_relation:
                return None
            model = field.related_model

        return None

    def _is_json_path(self, node: odata_ast._Node) -> bool:  # noqa
        """Return whether a node references a JSONField or a value inside one."""

        return isinstance(node, (odata_ast.Identifier, odata_ast.Attribute)) and (
            self._json_keys(self._field_path(node)) is not None
        )

    def _value_type(self, node: odata_ast._Node) -> str:  # noqa
        """Return the JSON extraction mode that matches the type of a non-JSON expression."""

        if isinstance(node, odata_ast.BinOp):
            return "number"
        if isinstance(node, odata_ast.Call):
            return "number" if node.func.full_name().lower() in JSON_COMPARE_NUMBER_FUNCTIONS else "text"
        if not isinstance(node, (odata_ast.Identifier, odata_ast.Attribute)):
            return "text"

        model = self.root_model
        *relations, column = self._field_path(node).split("__")
        for part in relations:
            model = model._meta.get_field(part).related_model  # noqa
        field = model._meta.get_field(column)  # noqa

        if isinstance(field, (IntegerField, FloatField, DecimalField)):
            return "number"

        return "datetime" if isinstance(field, DateTimeField) else "text"

    def _json_text(self, path: str):
        """Extract the text of a JSON value, supporting nested keys and related entities."""

        keys = self._json_keys(path)
        if not keys:
            return Cast(F(path), TextField())

        expression = F("__".join(path.split("__")[:-len(keys)]))
        for key in keys[:-1]:
            expression = KeyTransform(key, expression)

        return ExpressionWrapper(KeyTextTransform(keys[-1], expression), output_field=CharField())

    def _json_value(self, path: str, mode: str | None):
        """Return a field reference, extracting JSON values as text, numbers, or datetimes according to the mode."""

        if not mode or self._json_keys(path) is None:
            return F(path)
        if mode == "text":
            return self._json_text(path)

        pattern, output_field = (
            (JSON_NUMBER_PATTERN, FloatField()) if mode == "number" else (JSON_DATETIME_PATTERN, DateTimeField())
        )

        return Case(When(**{f"{path}__regex": pattern}, then=Cast(self._json_text(path), output_field)))

    def _compare_json(self, path: str, comparator: odata_ast._Node, literal: odata_ast._Node):  # noqa
        """Compare a value inside a JSONField with a literal."""

        if isinstance(comparator, odata_ast.In) and isinstance(literal, odata_ast.List):
            return reduce(Q.__or__, (self._compare_json(path, odata_ast.Eq(), item) for item in literal.val))
        if isinstance(literal, odata_ast.DateTime):
            return self.visit(comparator)(
                self._json_value(path, "datetime"),
                Cast(Value(literal.py_val, DateTimeField()), DateTimeField()),
            )
        if isinstance(literal, (odata_ast.Date, odata_ast.Time, odata_ast.GUID)):
            literal = odata_ast.String(literal.val)

        is_equality = isinstance(comparator, (odata_ast.Eq, odata_ast.NotEq))
        allowed = (odata_ast.String, odata_ast.Integer, odata_ast.Float)
        if not isinstance(literal, allowed + ((odata_ast.Boolean, odata_ast.Null) if is_equality else ())):
            raise TypeException(type(comparator).__name__, type(literal).__name__)

        value = literal.py_val
        has_key = Q(**{f"{path}__isnull": False})
        matches = Q(**{f"{path}__exact": value})

        if isinstance(comparator, odata_ast.NotEq):
            return has_key & ~matches
        if isinstance(comparator, odata_ast.Eq):
            return matches | ~has_key if value is None else matches

        if isinstance(literal, odata_ast.String):
            return self.visit(comparator)(Cast(self._json_text(path), TextField()), Value(value))

        return self.visit(comparator)(self._json_value(path, "number"), Value(value))


class DjangoBaseBackendAdapter:

    @staticmethod
    def build_entity_filter_arg(
        model: type[Model],
        filters: _Node | None = None,
    ):
        if filters is not None:
            visitor = ODataToDjangoQVisitor(model)
            return visitor.visit(filters)

        return None

    @staticmethod
    def build_orderby_arg(
        model: type[Model],
        orderby: list[OrderByField] | None = None,
    ) -> list[OrderBy]:
        """Translate a list of OrderByField descriptors into Django OrderBy expressions."""

        if not orderby:
            orderby = []

        visitor = ODataToDjangoQVisitor(model)

        return [
            getattr(
                F(visitor._field_path(  # noqa
                    reduce(odata_ast.Attribute, field.path[1:], odata_ast.Identifier(field.path[0]))
                )),
                "asc" if field.direction == OrderByDirection.ASC else "desc"
            )() for field in orderby
        ]

    @staticmethod
    def select_field(
        select: list[str] | None = None,
        field: str | None = None,
        value: Any | None = None,
        cast: Callable | None = None,
    ):
        """Return value when a field is selected, Absent otherwise."""

        if select is not None and field not in select:
            return Absent

        return cast(value) if cast else value

    @staticmethod
    def time_value(begin: datetime | None, end: datetime | None, interval: bool = True) -> str | None:
        """Format stored begin and end times as an ISO instant or interval."""

        if begin is None or (end is None and not interval):
            return begin and begin.isoformat()

        return f"{begin.isoformat()}/{(end or begin).isoformat()}"

    @staticmethod
    def time_fields(name: str, value: str | None) -> dict[str, str | None]:
        """Split an ISO instant or interval into begin and end model fields."""

        begin, _, end = (value or "").partition("/")

        return {f"{name}_begin": begin or None, f"{name}_end": end or None}

    @staticmethod
    def get_pagination_indices(
        top: int = 100,
        skip: int = 0,
    ) -> tuple[int, int]:
        """Compute queryset slice indices from OData $top and $skip values."""

        top = int(top) if int(top) >= 0 else 0
        skip = int(skip) if int(skip) >= 0 else 0

        return skip, skip + top

    def get_entities(
        self,
        manager: Manager,
        filters: _Node | None = None,
        orderby: list[OrderByField] | None = None,
        group_by: tuple[str, list] | None = None,
        select: list[str] | None = None,
        top: int = 100,
        skip: int = 0,
        count: bool = False,
    ) -> tuple[dict, QuerySet]:
        """
        Execute a filtered, ordered, paginated queryset and return grouped collections.

        Supports three modes: ungrouped (standard collection), pk-filtered (direct entity lookup
        by primary key), and field-grouped (window-function-based per-group pagination). For
        grouped queries, M2M fields are traversed by iterating related objects, while FK fields
        use a standard groupby on the field value.
        """

        try:
            q = self.build_entity_filter_arg(model=manager.model, filters=filters)
            if q is not None:
                if group_by is not None and group_by[0] != "pk" and (
                    manager.model._meta.get_field(group_by[0]).many_to_many  # noqa
                ):
                    # A filter on the grouping relation must not share its join.
                    q = Q(pk__in=manager.model._default_manager.filter(q).values("pk"))  # noqa
                manager = manager.filter(q)
                manager.query.get_compiler(manager.db).as_sql()  # Surfaces errors Django raises at compile time.
        except EmptyResultSet:
            pass
        except ODataException as e:
            raise InvalidQueryError(f"Invalid $filter: {e}") from e
        except (FieldError, FieldDoesNotExist) as e:
            raise InvalidQueryError("Invalid $filter: unknown property or incompatible types") from e
        except TypeError as e:
            raise InvalidQueryError("Invalid $filter: expression must be a boolean condition") from e
        except ValueError as e:
            raise InvalidQueryError("Invalid $filter: invalid function argument") from e

        lower_page_index, upper_page_index = self.get_pagination_indices(top, skip)

        if group_by is None:
            entity_count = manager.count() if count else None

            manager = manager.order_by(*self.build_orderby_arg(manager.model, orderby))
            queryset = manager.only(*select) if select is not None else manager.all()
            queryset = queryset[lower_page_index:upper_page_index]

            collections = {
                "__UNGROUPED__": CollectionDTO(
                    entity_count=entity_count,
                    entity_ids=[entity.pk for entity in queryset],
                )
            }

        elif group_by[0] == "pk":
            queryset = manager.only(*select) if select is not None else manager.all()

            collections = {
                "__UNGROUPED__": CollectionDTO(
                    entity_ids=[entity.pk for entity in queryset],
                )
            }

        else:
            if not orderby:
                orderby = [OrderByField(["id"], OrderByDirection.DESC)]

            entity_counts = dict(
                manager
                .values(group_by[0])
                .annotate(total=Count("id"))
                .values_list(group_by[0], "total")
            )

            manager = manager.annotate(
                group_id=F(group_by[0]),
                row_number=Window(
                    expression=RowNumber(),
                    partition_by=[F(group_by[0])],
                    order_by=self.build_orderby_arg(manager.model, orderby),
                )
            ).filter(row_number__gt=lower_page_index, row_number__lte=upper_page_index)

            queryset = manager.only(*select) if select is not None else manager.all()

            querysets = defaultdict(list)
            for obj in queryset:
                querysets[obj.group_id].append(obj)

            collections = {
                entity_id: CollectionDTO(
                    entity_count=int(entity_counts.get(entity_id, 0)),
                    entity_ids=[entity.pk for entity in querysets.get(entity_id, [])],
                )
                for entity_id in group_by[1]
            }

            queryset = [obj for group in querysets.values() for obj in group]

        return collections, queryset


class DjangoBackendAdapter(
    BaseBackendAdapter,
    DjangoBaseBackendAdapter
):

    @asynccontextmanager
    async def transaction(self):
        ctx = django_transaction.atomic()
        await sync_to_async(ctx.__enter__, thread_sensitive=True)()
        try:
            yield
        except Exception as exc:
            suppress = await sync_to_async(ctx.__exit__, thread_sensitive=True)(
                type(exc), exc, exc.__traceback__
            )
            if not suppress:
                raise
        else:
            await sync_to_async(ctx.__exit__, thread_sensitive=True)(None, None, None)

    # ------------------------------------------------------------------
    # Things
    # ------------------------------------------------------------------

    def get_things(
        self,
        filters: _Node | None = None,
        orderby: list[OrderByField] | None = None,
        group_by: tuple[str, list] | None = None,
        select: list[str] | None = None,
        top: int = 100,
        skip: int = 0,
        count: bool = False,
        context: HttpRequest | Any = None,
    ) -> EntityResultSetDTO[ThingDTO]:
        """Retrieve Thing entities from the database."""

        manager = Thing.objects

        if group_by and group_by[0] == "thing":
            group_by = ("pk", group_by[1],)
            manager = manager.filter(pk__in=group_by[1])
        elif group_by and group_by[0] == "location":
            group_by = ("locations", group_by[1],)
            manager = manager.filter(locations__in=group_by[1])

        if not select:
            select = []

        collections, queryset = self.get_entities(
            manager, filters, orderby, group_by, select, top, skip, count
        )

        entities = {
            thing.pk: ThingDTO(
                id=thing.pk if select is None or "id" in select else Absent,
                name=thing.name if select is None or "name" in select else Absent,
                description=thing.description if select is None or "description" in select else Absent,
                properties=thing.properties if select is None or "properties" in select else Absent,
            ) for thing in queryset
        }

        return EntityResultSetDTO(
            collections=collections,
            entities=entities
        )

    def create_things(
        self,
        payload: list[ThingDTO],
        context: HttpRequest | Any = None,
    ) -> list[app_settings.ID_TYPE]:
        """Persist new Thing instances and return their primary keys."""

        things = [
            Thing(
                name=dto.name,
                description=dto.description,
                properties=dto.properties if dto.properties is not Absent else None,
            )
            for dto in payload
        ]

        Thing.objects.bulk_create(things)

        for thing, dto in zip(things, payload):
            if dto.location_ids is not Absent:
                thing.locations.set(dto.location_ids)  # noqa

        return [thing.pk for thing in things]

    def update_things(
        self,
        payload: dict[app_settings.ID_TYPE, ThingDTO],
        context: HttpRequest | Any = None,
    ) -> None:
        """Apply partial updates to existing Thing instances."""

        editable_fields = {"name", "description", "properties"}

        for entity_id, dto in payload.items():
            fields = {
                field: getattr(dto, field) for field in editable_fields
                if getattr(dto, field, Absent) is not Absent
            }

            if fields:
                if not Thing.objects.filter(pk=entity_id).update(**fields):
                    raise LookupError
            elif not Thing.objects.filter(pk=entity_id).exists():
                raise LookupError

            if getattr(dto, "location_ids", Absent) is not Absent:
                Thing.objects.get(pk=entity_id).locations.set(dto.location_ids)

    def delete_things(
        self,
        entity_ids: list[app_settings.ID_TYPE],
        context: HttpRequest | Any = None,
    ) -> None:
        """Delete Thing instances using a single bulk DELETE query."""

        deleted, _ = Thing.objects.filter(pk__in=entity_ids).delete()
        if not deleted:
            raise LookupError

    # ------------------------------------------------------------------
    # Locations
    # ------------------------------------------------------------------

    def get_locations(
        self,
        filters: _Node | None = None,
        orderby: list[OrderByField] | None = None,
        group_by: tuple[str, list] | None = None,
        select: list[str] | None = None,
        top: int = 100,
        skip: int = 0,
        count: bool = False,
        context: HttpRequest | Any = None,
    ) -> EntityResultSetDTO[LocationDTO]:
        """Retrieve Location entities from the database."""

        manager = Location.objects

        if group_by and group_by[0] == "location":
            group_by = ("pk", group_by[1],)
            manager = manager.filter(pk__in=group_by[1])
        elif group_by and group_by[0] == "thing":
            group_by = ("things", group_by[1],)
            manager = manager.filter(things__in=group_by[1])
        elif group_by and group_by[0] == "historical_location":
            group_by = ("historical_locations", group_by[1],)
            manager = manager.filter(historical_locations__in=group_by[1])

        if not select:
            select = []

        collections, queryset = self.get_entities(
            manager, filters, orderby, group_by, select, top, skip, count
        )

        entities = {
            location.pk: LocationDTO(
                id=location.pk if select is None or "id" in select else Absent,
                name=location.name if select is None or "name" in select else Absent,
                description=location.description if select is None or "description" in select else Absent,
                encoding_type=location.encoding_type if select is None or "encoding_type" in select else Absent,
                location=location.location if select is None or "location" in select else Absent,
                properties=location.properties if select is None or "properties" in select else Absent,
            ) for location in queryset
        }

        return EntityResultSetDTO(
            collections=collections,
            entities=entities
        )

    def create_locations(
        self,
        payload: list[LocationDTO],
        context: HttpRequest | Any = None,
    ) -> list[app_settings.ID_TYPE]:
        """Persist new Location instances and return their primary keys."""

        locations = [
            Location(
                name=dto.name,
                description=dto.description,
                encoding_type=dto.encoding_type if dto.encoding_type is not Absent else Location.GEOJSON,
                location=dto.location,
                properties=dto.properties if dto.properties is not Absent else None,
            )
            for dto in payload
        ]

        Location.objects.bulk_create(locations)

        for location, dto in zip(locations, payload):
            if dto.thing_ids is not Absent:
                location.things.set(dto.thing_ids)

        return [location.pk for location in locations]

    def update_locations(
        self,
        payload: dict[app_settings.ID_TYPE, LocationDTO],
        context: HttpRequest | Any = None,
    ) -> None:
        """Apply partial updates to existing Location instances."""

        editable_fields = {"name", "description", "encoding_type", "location", "properties"}

        for entity_id, dto in payload.items():
            fields = {
                field: getattr(dto, field) for field in editable_fields
                if getattr(dto, field, Absent) is not Absent
            }

            if fields:
                if not Location.objects.filter(pk=entity_id).update(**fields):
                    raise LookupError
            elif not Location.objects.filter(pk=entity_id).exists():
                raise LookupError

            if getattr(dto, "thing_ids", Absent) is not Absent:
                Location.objects.get(pk=entity_id).things.set(dto.thing_ids)

    def delete_locations(
        self,
        entity_ids: list[app_settings.ID_TYPE],
        context: HttpRequest | Any = None,
    ) -> None:
        """Delete Location instances using a single bulk DELETE query."""

        deleted, _ = Location.objects.filter(pk__in=entity_ids).delete()
        if not deleted:
            raise LookupError

    # ------------------------------------------------------------------
    # Historical Locations
    # ------------------------------------------------------------------

    def get_historical_locations(
        self,
        filters: _Node | None = None,
        orderby: list[OrderByField] | None = None,
        group_by: tuple[str, list] | None = None,
        select: list[str] | None = None,
        top: int = 100,
        skip: int = 0,
        count: bool = False,
        context: HttpRequest | Any = None,
    ) -> EntityResultSetDTO[HistoricalLocationDTO]:
        """Retrieve HistoricalLocation entities from the database."""

        manager = HistoricalLocation.objects

        if group_by and group_by[0] == "historical_location":
            group_by = ("pk", group_by[1],)
            manager = manager.filter(pk__in=group_by[1])
        elif group_by and group_by[0] == "thing":
            group_by = ("thing", group_by[1],)
            manager = manager.filter(thing__in=group_by[1])
        elif group_by and group_by[0] in ("location", "locations"):
            group_by = ("locations", group_by[1],)
            manager = manager.filter(locations__in=group_by[1])

        if not select:
            select = []

        collections, queryset = self.get_entities(
            manager, filters, orderby, group_by, select, top, skip, count
        )

        entities = {
            historical_location.pk: HistoricalLocationDTO(
                id=historical_location.pk if select is None or "id" in select else Absent,
                time=str(historical_location.time) if select is None or "time" in select else Absent,
                thing_id=historical_location.thing_id
            ) for historical_location in queryset
        }

        return EntityResultSetDTO(
            collections=collections,
            entities=entities
        )

    def create_historical_locations(
        self,
        payload: list[HistoricalLocationDTO],
        context: HttpRequest | Any = None,
    ) -> list[app_settings.ID_TYPE]:
        """Persist new HistoricalLocation instances and return their primary keys."""

        historical_locations = [
            HistoricalLocation(
                time=dto.time, 
                thing_id=dto.thing_id
            )
            for dto in payload
        ]

        HistoricalLocation.objects.bulk_create(historical_locations)

        for historical_location, dto in zip(historical_locations, payload):
            if dto.location_ids is not Absent:
                historical_location.locations.set(dto.location_ids)

        return [historical_location.pk for historical_location in historical_locations]

    def update_historical_locations(
        self,
        payload: dict[app_settings.ID_TYPE, HistoricalLocationDTO],
        context: HttpRequest | Any = None,
    ) -> None:
        """Apply partial updates to existing HistoricalLocation instances."""

        editable_fields = {"time", "thing_id"}

        for entity_id, dto in payload.items():
            fields = {
                field: getattr(dto, field) for field in editable_fields
                if getattr(dto, field, Absent) is not Absent
            }

            if fields:
                if not HistoricalLocation.objects.filter(pk=entity_id).update(**fields):
                    raise LookupError
            elif not HistoricalLocation.objects.filter(pk=entity_id).exists():
                raise LookupError

            if getattr(dto, "location_ids", Absent) is not Absent:
                HistoricalLocation.objects.get(pk=entity_id).locations.set(dto.location_ids)

    def delete_historical_locations(
        self,
        entity_ids: list[app_settings.ID_TYPE],
        context: HttpRequest | Any = None,
    ) -> None:
        """Delete HistoricalLocation instances using a single bulk DELETE query."""

        deleted, _ = HistoricalLocation.objects.filter(pk__in=entity_ids).delete()
        if not deleted:
            raise LookupError

    # ------------------------------------------------------------------
    # Sensors
    # ------------------------------------------------------------------

    def get_sensors(
        self,
        filters: _Node | None = None,
        orderby: list[OrderByField] | None = None,
        group_by: tuple[str, list] | None = None,
        select: list[str] | None = None,
        top: int = 100,
        skip: int = 0,
        count: bool = False,
        context: HttpRequest | Any = None,
    ) -> EntityResultSetDTO[SensorDTO]:
        """Retrieve Sensor entities from the database."""

        manager = Sensor.objects

        if group_by and group_by[0] == "sensor":
            group_by = ("pk", group_by[1],)
            manager = manager.filter(pk__in=group_by[1])

        if not select:
            select = []

        collections, queryset = self.get_entities(
            manager, filters, orderby, group_by, select, top, skip, count
        )

        entities = {
            sensor.pk: SensorDTO(
                id=sensor.pk if select is None or "id" in select else Absent,
                name=sensor.name if select is None or "name" in select else Absent,
                description=sensor.description if select is None or "description" in select else Absent,
                encoding_type=sensor.encoding_type if select is None or "encoding_type" in select else Absent,
                metadata=sensor.metadata if select is None or "metadata" in select else Absent,
                properties=sensor.properties if select is None or "properties" in select else Absent,
            ) for sensor in queryset
        }

        return EntityResultSetDTO(
            collections=collections,
            entities=entities
        )

    def create_sensors(
        self,
        payload: list[SensorDTO],
        context: HttpRequest | Any = None,
    ) -> list[app_settings.ID_TYPE]:
        """Persist new Sensor instances and return their primary keys."""

        sensors = [
            Sensor(
                name=dto.name,
                description=dto.description,
                encoding_type=dto.encoding_type,
                metadata=dto.metadata,
                properties=dto.properties if dto.properties is not Absent else None,
            )
            for dto in payload
        ]

        Sensor.objects.bulk_create(sensors)

        return [sensor.pk for sensor in sensors]

    def update_sensors(
        self,
        payload: dict[app_settings.ID_TYPE, SensorDTO],
        context: HttpRequest | Any = None,
    ) -> None:
        """Apply partial updates to existing Sensor instances."""

        editable_fields = {"name", "description", "encoding_type", "metadata", "properties"}

        for entity_id, dto in payload.items():
            fields = {
                field: getattr(dto, field) for field in editable_fields
                if getattr(dto, field, Absent) is not Absent
            }

            if fields:
                if not Sensor.objects.filter(pk=entity_id).update(**fields):
                    raise LookupError
            elif not Sensor.objects.filter(pk=entity_id).exists():
                raise LookupError

    def delete_sensors(
        self,
        entity_ids: list[app_settings.ID_TYPE],
        context: HttpRequest | Any = None,
    ) -> None:
        """Delete Sensor instances using a single bulk DELETE query."""

        deleted, _ = Sensor.objects.filter(pk__in=entity_ids).delete()
        if not deleted:
            raise LookupError

    # ------------------------------------------------------------------
    # Observed Properties
    # ------------------------------------------------------------------

    def get_observed_properties(
        self,
        filters: _Node | None = None,
        orderby: list[OrderByField] | None = None,
        group_by: tuple[str, list] | None = None,
        select: list[str] | None = None,
        top: int = 100,
        skip: int = 0,
        count: bool = False,
        context: HttpRequest | Any = None,
    ) -> EntityResultSetDTO[ObservedPropertyDTO]:
        """Retrieve ObservedProperty entities from the database."""

        manager = ObservedProperty.objects

        if group_by and group_by[0] == "observed_property":
            group_by = ("pk", group_by[1],)
            manager = manager.filter(pk__in=group_by[1])

        if not select:
            select = []

        collections, queryset = self.get_entities(
            manager, filters, orderby, group_by, select, top, skip, count
        )

        entities = {
            observed_property.pk: ObservedPropertyDTO(
                id=observed_property.pk if select is None or "id" in select else Absent,
                name=observed_property.name if select is None or "name" in select else Absent,
                description=observed_property.description if select is None or "description" in select else Absent,
                definition=observed_property.definition if select is None or "definition" in select else Absent,
                properties=observed_property.properties if select is None or "properties" in select else Absent,
            ) for observed_property in queryset
        }

        return EntityResultSetDTO(
            collections=collections,
            entities=entities
        )

    def create_observed_properties(
        self,
        payload: list[ObservedPropertyDTO],
        context: HttpRequest | Any = None,
    ) -> list[app_settings.ID_TYPE]:
        """Persist new ObservedProperty instances and return their primary keys."""

        observed_properties = [
            ObservedProperty(
                name=dto.name,
                definition=dto.definition,
                description=dto.description,
                properties=dto.properties if dto.properties is not Absent else None,
            )
            for dto in payload
        ]

        ObservedProperty.objects.bulk_create(observed_properties)

        return [observed_property.pk for observed_property in observed_properties]

    def update_observed_properties(
        self,
        payload: dict[app_settings.ID_TYPE, ObservedPropertyDTO],
        context: HttpRequest | Any = None,
    ) -> None:
        """Apply partial updates to existing ObservedProperty instances."""

        editable_fields = {"name", "definition", "description", "properties"}

        for entity_id, dto in payload.items():
            fields = {
                field: getattr(dto, field) for field in editable_fields
                if getattr(dto, field, Absent) is not Absent
            }

            if fields:
                if not ObservedProperty.objects.filter(pk=entity_id).update(**fields):
                    raise LookupError
            elif not ObservedProperty.objects.filter(pk=entity_id).exists():
                raise LookupError

    def delete_observed_properties(
        self,
        entity_ids: list[app_settings.ID_TYPE],
        context: HttpRequest | Any = None,
    ) -> None:
        """Delete ObservedProperty instances using a single bulk DELETE query."""

        deleted, _ = ObservedProperty.objects.filter(pk__in=entity_ids).delete()
        if not deleted:
            raise LookupError

    # ------------------------------------------------------------------
    # Datastreams
    # ------------------------------------------------------------------

    def get_datastreams(
        self,
        filters: _Node | None = None,
        orderby: list[OrderByField] | None = None,
        group_by: tuple[str, list] | None = None,
        select: list[str] | None = None,
        top: int = 100,
        skip: int = 0,
        count: bool = False,
        context: HttpRequest | Any = None,
    ) -> EntityResultSetDTO[DatastreamDTO]:
        """Retrieve Datastream entities from the database."""

        manager = Datastream.objects

        if group_by and group_by[0] == "datastream":
            group_by = ("pk", group_by[1],)
            manager = manager.filter(pk__in=group_by[1])
        elif group_by and group_by[0] == "thing":
            manager = manager.filter(thing__in=group_by[1])
        elif group_by and group_by[0] == "sensor":
            manager = manager.filter(sensor__in=group_by[1])
        elif group_by and group_by[0] == "observed_property":
            manager = manager.filter(observed_property__in=group_by[1])

        if not select:
            select = []

        if "phenomenon_time" in select:
            select = [
                "phenomenon_time_begin" if field == "phenomenon_time" else field
                for field in select
            ] + ["phenomenon_time_end"]

        if "result_time" in select:
            select = [
                "result_time_begin" if field == "result_time" else field
                for field in select
            ] + ["result_time_end"]

        collections, queryset = self.get_entities(
            manager, filters, orderby, group_by, select, top, skip, count
        )

        entities = {
            datastream.pk: DatastreamDTO(
                id=self.select_field(select, "id", datastream.pk),
                name=self.select_field(select, "name", datastream.name),
                description=self.select_field(select, "description", datastream.description),
                unit_of_measurement=self.select_field(select, "unit_of_measurement", datastream.unit_of_measurement),
                observation_type=self.select_field(select, "observation_type", datastream.observation_type),
                observed_area=self.select_field(select, "observed_area", datastream.observed_area),
                phenomenon_time=self.select_field(
                    select, "phenomenon_time_begin", datastream,
                    cast=lambda d: self.time_value(d.phenomenon_time_begin, d.phenomenon_time_end)
                ),
                result_time=self.select_field(
                    select, "result_time_begin", datastream,
                    cast=lambda d: self.time_value(d.result_time_begin, d.result_time_end)
                ),
                properties=self.select_field(select, "properties", datastream.properties),
                thing_id=self.select_field(select, "thing_id", datastream.thing_id),
                sensor_id=self.select_field(select, "sensor_id", datastream.sensor_id),
                observed_property_id=self.select_field(select, "observed_property_id", datastream.observed_property_id),
            ) for datastream in queryset
        }

        return EntityResultSetDTO(
            collections=collections,
            entities=entities
        )

    def create_datastreams(
        self,
        payload: list[DatastreamDTO],
        context: HttpRequest | Any = None,
    ) -> list[app_settings.ID_TYPE]:
        """Persist new Datastream instances and return their primary keys."""

        datastreams = [
            Datastream(
                name=dto.name,
                description=dto.description,
                unit_of_measurement=dto.unit_of_measurement,
                observation_type=dto.observation_type,
                properties=dto.properties if dto.properties is not Absent else None,
                observed_area=dto.observed_area if dto.observed_area is not Absent else None,
                **self.time_fields("phenomenon_time", dto.phenomenon_time),
                **self.time_fields("result_time", dto.result_time),
                thing_id=dto.thing_id,
                sensor_id=dto.sensor_id,
                observed_property_id=dto.observed_property_id,
            )
            for dto in payload
        ]

        Datastream.objects.bulk_create(datastreams)

        return [datastream.pk for datastream in datastreams]

    def update_datastreams(
        self,
        payload: dict[app_settings.ID_TYPE, DatastreamDTO],
        context: HttpRequest | Any = None,
    ) -> None:
        """Apply partial updates to existing Datastream instances."""

        editable_fields = {
            "name", "description", "unit_of_measurement", "observation_type", "properties",
            "observed_area", "thing_id", "sensor_id", "observed_property_id",
        }

        for entity_id, dto in payload.items():
            fields = {
                field: getattr(dto, field) for field in editable_fields
                if getattr(dto, field, Absent) is not Absent
            }

            for name in ("phenomenon_time", "result_time"):
                if (value := getattr(dto, name)) is not Absent:
                    fields.update(self.time_fields(name, value))

            if "thing_id" in fields and not Thing.objects.filter(pk=fields["thing_id"]).exists():
                raise HttpError(400, f"Thing with id {fields['thing_id']} does not exist.")
            if "sensor_id" in fields and not Sensor.objects.filter(pk=fields["sensor_id"]).exists():
                raise HttpError(400, f"Sensor with id {fields['sensor_id']} does not exist.")
            if "observed_property_id" in fields and not ObservedProperty.objects.filter(
                pk=fields["observed_property_id"]
            ).exists():
                raise HttpError(400, f"ObservedProperty with id {fields['observed_property_id']} does not exist.")

            if fields:
                if not Datastream.objects.filter(pk=entity_id).update(**fields):
                    raise LookupError
            elif not Datastream.objects.filter(pk=entity_id).exists():
                raise LookupError

    def delete_datastreams(
        self,
        entity_ids: list[app_settings.ID_TYPE],
        context: HttpRequest | Any = None,
    ) -> None:
        """Delete Datastream instances using a single bulk DELETE query."""

        deleted, _ = Datastream.objects.filter(pk__in=entity_ids).delete()
        if not deleted:
            raise LookupError

    # ------------------------------------------------------------------
    # Observations
    # ------------------------------------------------------------------

    def get_observations(
        self,
        filters: _Node | None = None,
        orderby: list[OrderByField] | None = None,
        group_by: tuple[str, list] | None = None,
        select: list[str] | None = None,
        top: int = 100,
        skip: int = 0,
        count: bool = False,
        context: HttpRequest | Any = None,
    ) -> EntityResultSetDTO[ObservationDTO]:
        """Retrieve Observation entities from the database."""

        manager = Observation.objects

        if group_by and group_by[0] == "observation":
            group_by = ("pk", group_by[1],)
            manager = manager.filter(pk__in=group_by[1])
        elif group_by and group_by[0] == "datastream":
            manager = manager.filter(datastream__in=group_by[1])
        elif group_by and group_by[0] == "feature_of_interest":
            manager = manager.filter(feature_of_interest__in=group_by[1])

        if not select:
            select = []

        if "phenomenon_time" in select:
            select = [
                "phenomenon_time_begin" if field == "phenomenon_time" else field
                for field in select
            ] + ["phenomenon_time_end"]

        if "valid_time" in select:
            select = [
                "valid_time_begin" if field == "valid_time" else field
                for field in select
            ] + ["valid_time_end"]

        collections, queryset = self.get_entities(
            manager, filters, orderby, group_by, select, top, skip, count
        )

        entities = {
            observation.pk: ObservationDTO(
                id=self.select_field(select, "id", observation.pk),
                phenomenon_time=self.select_field(
                    select, "phenomenon_time_begin", observation,
                    cast=lambda o: self.time_value(o.phenomenon_time_begin, o.phenomenon_time_end, interval=False)
                ),
                result=self.select_field(select, "result", observation.result),
                result_time=self.select_field(
                    select, "result_time", observation.result_time, cast=lambda v: v and v.isoformat()
                ),
                result_quality=self.select_field(select, "result_quality", observation.result_quality),
                valid_time=self.select_field(
                    select, "valid_time_begin", observation,
                    cast=lambda o: self.time_value(o.valid_time_begin, o.valid_time_end)
                ),
                parameters=self.select_field(select, "parameters", observation.parameters),
                datastream_id=self.select_field(select, "datastream_id", observation.datastream_id),
                feature_of_interest_id=self.select_field(
                    select, "feature_of_interest_id", observation.feature_of_interest_id
                ),
            ) for observation in queryset
        }

        return EntityResultSetDTO(
            collections=collections,
            entities=entities
        )

    @staticmethod
    def resolve_feature_of_interest_for_datastream(datastream_id) -> app_settings.ID_TYPE | None:
        """Get or create a FeatureOfInterest from the Thing's current GeoJSON Location."""

        location = (
            Location.objects
            .filter(things__datastreams__id=datastream_id, encoding_type=FeatureOfInterest.GEOJSON)
            .first()
        )

        if location is None:
            return None

        feature_of_interest, _ = FeatureOfInterest.objects.get_or_create(
            feature=location.location,
            defaults={
                "name": location.name,
                "description": location.description,
                "encoding_type": location.encoding_type,
            }
        )

        return feature_of_interest.pk

    def create_observations(
        self,
        payload: list[ObservationDTO],
        context: HttpRequest | Any = None,
    ) -> list[app_settings.ID_TYPE]:
        """Persist new Observation instances and return their primary keys."""

        now = datetime.now(timezone.utc)

        feature_of_interest_cache: dict = {}
        for dto in payload:
            if dto.feature_of_interest_id is Absent and dto.datastream_id not in feature_of_interest_cache:
                feature_of_interest_cache[dto.datastream_id] = self.resolve_feature_of_interest_for_datastream(
                    dto.datastream_id
                )

        observations = []

        for dto in payload:
            phenomenon_time = dto.phenomenon_time or now.isoformat()
            observations.append(Observation(
                **self.time_fields("phenomenon_time", phenomenon_time),
                result=dto.result,
                result_time=dto.result_time if dto.result_time is not Absent else phenomenon_time.split("/")[0],
                result_quality=dto.result_quality if dto.result_quality is not Absent else None,
                **self.time_fields("valid_time", dto.valid_time),
                parameters=dto.parameters if dto.parameters is not Absent else None,
                datastream_id=dto.datastream_id,
                feature_of_interest_id=(
                    dto.feature_of_interest_id if dto.feature_of_interest_id is not Absent
                    else feature_of_interest_cache.get(dto.datastream_id)
                ),
            ))

        Observation.objects.bulk_create(observations)

        return [observation.pk for observation in observations]

    def update_observations(
        self,
        payload: dict[app_settings.ID_TYPE, ObservationDTO],
        context: HttpRequest | Any = None,
    ) -> None:
        """Apply partial updates to existing Observation instances."""

        editable_fields = {
            "result", "result_time", "result_quality", "parameters", "datastream_id", "feature_of_interest_id"
        }

        for entity_id, dto in payload.items():
            if dto.phenomenon_time is None:
                raise HttpError(400, "phenomenonTime cannot be null.")

            fields = {
                field: getattr(dto, field) for field in editable_fields
                if getattr(dto, field, Absent) is not Absent
            }

            for name in ("phenomenon_time", "valid_time"):
                if (value := getattr(dto, name)) is not Absent:
                    fields.update(self.time_fields(name, value))

            if fields:
                if not Observation.objects.filter(pk=entity_id).update(**fields):
                    raise LookupError
            elif not Observation.objects.filter(pk=entity_id).exists():
                raise LookupError

    def delete_observations(
        self,
        entity_ids: list[app_settings.ID_TYPE],
        context: HttpRequest | Any = None,
    ) -> None:
        """Delete Observation instances using a single bulk DELETE query."""

        deleted, _ = Observation.objects.filter(pk__in=entity_ids).delete()
        if not deleted:
            raise LookupError

    # ------------------------------------------------------------------
    # Features of Interest
    # ------------------------------------------------------------------

    def get_features_of_interest(
        self,
        filters: _Node | None = None,
        orderby: list[OrderByField] | None = None,
        group_by: tuple[str, list] | None = None,
        select: list[str] | None = None,
        top: int = 100,
        skip: int = 0,
        count: bool = False,
        context: HttpRequest | Any = None,
    ) -> EntityResultSetDTO[FeatureOfInterestDTO]:
        """Retrieve FeatureOfInterest entities from the database."""

        manager = FeatureOfInterest.objects

        if group_by and group_by[0] == "feature_of_interest":
            group_by = ("pk", group_by[1],)
            manager = manager.filter(pk__in=group_by[1])

        if not select:
            select = []

        collections, queryset = self.get_entities(
            manager, filters, orderby, group_by, select, top, skip, count
        )

        entities = {
            feature_of_interest.pk: FeatureOfInterestDTO(
                id=feature_of_interest.pk if select is None or "id" in select else Absent,
                name=feature_of_interest.name if select is None or "name" in select else Absent,
                description=feature_of_interest.description if select is None or "description" in select else Absent,
                encoding_type=(
                    feature_of_interest.encoding_type if select is None or "encoding_type" in select else Absent
                ),
                feature=feature_of_interest.feature if select is None or "feature" in select else Absent,
                properties=feature_of_interest.properties if select is None or "properties" in select else Absent,
            ) for feature_of_interest in queryset
        }

        return EntityResultSetDTO(
            collections=collections,
            entities=entities
        )

    def create_features_of_interest(
        self,
        payload: list[FeatureOfInterestDTO],
        context: HttpRequest | Any = None,
    ) -> list[app_settings.ID_TYPE]:
        """Persist new FeatureOfInterest instances and return their primary keys."""

        features_of_interest = [
            FeatureOfInterest(
                name=dto.name,
                description=dto.description,
                encoding_type=dto.encoding_type,
                feature=dto.feature,
                properties=dto.properties if dto.properties is not Absent else None,
            )
            for dto in payload
        ]

        FeatureOfInterest.objects.bulk_create(features_of_interest)

        return [feature_of_interest.pk for feature_of_interest in features_of_interest]

    def update_features_of_interest(
        self,
        payload: dict[app_settings.ID_TYPE, FeatureOfInterestDTO],
        context: HttpRequest | Any = None,
    ) -> None:
        """Apply partial updates to existing FeatureOfInterest instances."""

        editable_fields = {"name", "description", "encoding_type", "feature", "properties"}

        for entity_id, dto in payload.items():
            fields = {
                field: getattr(dto, field) for field in editable_fields
                if getattr(dto, field, Absent) is not Absent
            }

            if fields:
                if not FeatureOfInterest.objects.filter(pk=entity_id).update(**fields):
                    raise LookupError
            elif not FeatureOfInterest.objects.filter(pk=entity_id).exists():
                raise LookupError

    def delete_features_of_interest(
        self,
        entity_ids: list[app_settings.ID_TYPE],
        context: HttpRequest | Any = None,
    ) -> None:
        """Delete FeatureOfInterest instances using a single bulk DELETE query."""

        deleted, _ = FeatureOfInterest.objects.filter(pk__in=entity_ids).delete()
        if not deleted:
            raise LookupError
