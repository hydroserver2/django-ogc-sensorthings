from typing import Any, Callable
from itertools import groupby
from collections import defaultdict
from contextlib import asynccontextmanager
from asgiref.sync import sync_to_async
from odata_query.ast import _Node  # noqa
from odata_query.django.django_q import AstToDjangoQVisitor
from django.http import HttpRequest
from django.db import transaction as django_transaction
from django.db.models import QuerySet, Manager, Count, F, Window, Model
from django.db.models.functions import RowNumber
from django.db.models.expressions import OrderBy
from pydantic.alias_generators import to_snake
from sensorthings.types import Absent, OrderByField, OrderByDirection
from sensorthings.versions.v1_1.conf import app_settings
from sensorthings.versions.v1_1.dto import (EntityResultSetDTO, CollectionDTO, ThingDTO, LocationDTO,
                                            HistoricalLocationDTO, SensorDTO, ObservedPropertyDTO,
                                            DatastreamDTO, ObservationDTO, FeatureOfInterestDTO)
from .models import (Thing, Location, HistoricalLocation, Sensor, ObservedProperty, Datastream, Observation,
                     FeatureOfInterest)
from ..base import BaseBackendAdapter


class DjangoBaseBackendAdapter:

    @staticmethod
    def build_entity_filter_arg(
        model: type[Model],
        filters: _Node | None = None,
    ):
        if filters is not None:
            visitor = AstToDjangoQVisitor(model)
            return visitor.visit(filters)

        return None

    @staticmethod
    def build_orderby_arg(
        orderby: list[OrderByField] | None = None,
    ) -> list[OrderBy]:
        """Translate a list of OrderByField descriptors into Django OrderBy expressions."""

        if not orderby:
            orderby = []

        return [
            getattr(
                F("__".join(to_snake(path) for path in field.path)),
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

        q = self.build_entity_filter_arg(model=manager.model, filters=filters)
        if q is not None:
            manager = manager.filter(q)

        lower_page_index, upper_page_index = self.get_pagination_indices(top, skip)

        if group_by is None:
            entity_count = manager.count() if count else None

            manager = manager.order_by(*self.build_orderby_arg(orderby))
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
                row_number=Window(
                    expression=RowNumber(),
                    partition_by=[F(group_by[0])],
                    order_by=self.build_orderby_arg(orderby),
                )
            ).filter(row_number__gte=lower_page_index, row_number__lte=upper_page_index)

            queryset = manager.only(*select) if select is not None else manager.all()

            if queryset.model._meta.get_field(group_by[0]).many_to_many:  # noqa
                querysets = defaultdict(list)
                for obj in queryset:
                    for entity in getattr(obj, group_by[0]).all():
                        querysets[entity.pk].append(obj)
                querysets = dict(querysets)
            else:
                querysets = {
                    entity.pk: list(group)
                    for entity, group in groupby(
                        queryset, key=lambda o: getattr(o, group_by[0])
                    )
                }

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
            manager = manager.prefetch_related("locations").filter(locations__in=group_by[1])

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
            manager = manager.prefetch_related("things").filter(things__in=group_by[1])
        elif group_by and group_by[0] == "historical_location":
            group_by = ("historical_locations", group_by[1],)
            manager = manager.prefetch_related("historical_locations").filter(historical_locations__in=group_by[1])

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
        elif group_by and group_by[0] == "locations":
            group_by = ("locations", group_by[1],)
            manager = manager.prefetch_related("locations").filter(locations__in=group_by[1])

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
                    select, "phenomenon_time_begin", datastream.phenomenon_time_begin,
                    cast=lambda v: v and v.isoformat()
                ),
                result_time=self.select_field(
                    select, "result_time_begin", datastream.result_time_begin, cast=lambda v: v and v.isoformat()
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
                phenomenon_time_begin=dto.phenomenon_time if dto.phenomenon_time is not Absent else None,
                result_time_begin=dto.result_time if dto.result_time is not Absent else None,
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
            "observed_area", "phenomenon_time_begin", "result_time_begin",
            "thing_id", "sensor_id", "observed_property_id",
        }

        for entity_id, dto in payload.items():
            fields = {
                field: getattr(dto, field) for field in editable_fields
                if getattr(dto, field, Absent) is not Absent
            }

            if "thing_id" in fields and not Thing.objects.filter(pk=fields["thing_id"]).exists():
                raise ValueError(f"Thing with id {fields['thing_id']} does not exist.")
            if "sensor_id" in fields and not Sensor.objects.filter(pk=fields["sensor_id"]).exists():
                raise ValueError(f"Sensor with id {fields['sensor_id']} does not exist.")
            if "observed_property_id" in fields and not ObservedProperty.objects.filter(
                pk=fields["observed_property_id"]
            ).exists():
                raise ValueError(f"ObservedProperty with id {fields['observed_property_id']} does not exist.")

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
                    select, "phenomenon_time_begin", observation.phenomenon_time_begin,
                    cast=lambda v: v and v.isoformat()
                ),
                result=self.select_field(select, "result", observation.result),
                result_time=self.select_field(
                    select, "result_time", observation.result_time, cast=lambda v: v and v.isoformat()
                ),
                result_quality=self.select_field(select, "result_quality", observation.result_quality),
                valid_time=self.select_field(
                    select, "valid_time_begin", observation.valid_time_begin, cast=lambda v: v and v.isoformat()
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

    def create_observations(
        self,
        payload: list[ObservationDTO],
        context: HttpRequest | Any = None,
    ) -> list[app_settings.ID_TYPE]:
        """Persist new Observation instances and return their primary keys."""

        observations = [
            Observation(
                phenomenon_time_begin=dto.phenomenon_time,
                result=dto.result,
                result_time=dto.result_time,
                result_quality=dto.result_quality if dto.result_quality is not Absent else None,
                valid_time_begin=dto.valid_time if dto.valid_time is not Absent else None,
                parameters=dto.parameters if dto.parameters is not Absent else None,
                datastream_id=dto.datastream_id,
                feature_of_interest_id=dto.feature_of_interest_id,
            )
            for dto in payload
        ]

        Observation.objects.bulk_create(observations)

        return [
            observation.pk for observation in observations
        ]

    def update_observations(
        self,
        payload: dict[app_settings.ID_TYPE, ObservationDTO],
        context: HttpRequest | Any = None,
    ) -> None:
        """Apply partial updates to existing Observation instances."""

        editable_fields = {
            "phenomenon_time_begin", "result", "result_time", "result_quality", "valid_time_begin", "parameters",
            "datastream_id", "feature_of_interest_id"
        }

        for entity_id, dto in payload.items():
            fields = {
                field: getattr(dto, field) for field in editable_fields
                if getattr(dto, field, Absent) is not Absent
            }

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
