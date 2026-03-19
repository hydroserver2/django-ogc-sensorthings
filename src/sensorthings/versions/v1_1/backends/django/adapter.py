from typing import Any
from itertools import groupby
from collections import defaultdict
from odata_query.ast import _Node  # noqa
from odata_query.django.django_q import AstToDjangoQVisitor
from django.http import HttpRequest
from django.db.models import QuerySet, Manager, Count, F, Window, Model
from django.db.models.functions import RowNumber
from django.db.models.expressions import OrderBy
from pydantic.alias_generators import to_snake
from sensorthings.types import Absent
from sensorthings.versions.v1_1.dto import (EntityResultSetDTO, CollectionDTO, OrderByField, OrderByDirection, ThingDTO,
                                            LocationDTO, HistoricalLocationDTO, SensorDTO, ObservedPropertyDTO,
                                            DatastreamDTO, ObservationDTO, FeatureOfInterestDTO)
from .models import (Thing, Location, HistoricalLocation, Sensor, ObservedProperty, Datastream, Observation,
                     FeatureOfInterest)
from ..base import BaseBackendAdapter


class DjangoBaseBackendAdapter:
    """"""

    @staticmethod
    def build_entity_filter_arg(
        model: type[Model],
        filters: _Node | None = None,
    ) -> dict:
        """"""

        query_filter = {}

        if filters is not None:
            visitor = AstToDjangoQVisitor(model)
            query_filter = visitor.visit(filters)

        return query_filter

    @staticmethod
    def build_orderby_arg(
        orderby: list[OrderByField] | None = None,
    ) -> list[OrderBy]:
        """"""

        if not orderby:
            orderby = []

        return [
            getattr(
                F("__".join(to_snake(path) for path in field.path)),
                "asc" if field.direction == OrderByDirection.ASC else "desc"
            )() for field in orderby
        ]

    @staticmethod
    def get_pagination_indices(
        top: int = 100,
        skip: int = 0,
    ) -> tuple[int, int]:
        """"""

        top = int(top) if int(top) >= 0 else 0
        skip = int(skip) if int(skip) >= 0 else 0

        return skip, skip + top

    def get_entities(
        self,
        manager: type[Manager],
        filters: _Node | None = None,
        orderby: list[OrderByField] | None = None,
        group_by: tuple[str, list] | None = None,
        select: list[str] | None = None,
        top: int = 100,
        skip: int = 0,
        count: bool = False,
    ) -> tuple[dict, QuerySet]:
        """"""

        manager = manager.filter(**self.build_entity_filter_arg(
            model=manager.model,
            filters=filters,
        ))

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
    """"""

    def get_things(
        self,
        filters: _Node | None = None,
        orderby: list[OrderByField] | None = None,
        group_by: str | None = None,
        select: list[str] | None = None,
        top: int = 100,
        skip: int = 0,
        count: bool = False,
        context: HttpRequest | Any = None,
    ) -> EntityResultSetDTO[ThingDTO]:
        """"""

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

    def get_locations(
        self,
        filters: _Node | None = None,
        orderby: list[OrderByField] | None = None,
        group_by: str | None = None,
        select: list[str] | None = None,
        top: int = 100,
        skip: int = 0,
        count: bool = False,
        context: HttpRequest | Any = None,
    ) -> EntityResultSetDTO[LocationDTO]:
        """"""

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

    def get_historical_locations(
        self,
        filters: _Node | None = None,
        orderby: list[OrderByField] | None = None,
        group_by: str | None = None,
        select: list[str] | None = None,
        top: int = 100,
        skip: int = 0,
        count: bool = False,
        context: HttpRequest | Any = None,
    ) -> EntityResultSetDTO[LocationDTO]:
        """"""

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

    def get_sensors(
        self,
        filters: _Node | None = None,
        orderby: list[OrderByField] | None = None,
        group_by: str | None = None,
        select: list[str] | None = None,
        top: int = 100,
        skip: int = 0,
        count: bool = False,
        context: HttpRequest | Any = None,
    ) -> EntityResultSetDTO[ThingDTO]:
        """"""

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

    def get_observed_properties(
        self,
        filters: _Node | None = None,
        orderby: list[OrderByField] | None = None,
        group_by: str | None = None,
        select: list[str] | None = None,
        top: int = 100,
        skip: int = 0,
        count: bool = False,
        context: HttpRequest | Any = None,
    ) -> EntityResultSetDTO[ThingDTO]:
        """"""

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

    def get_datastreams(
        self,
        filters: _Node | None = None,
        orderby: list[OrderByField] | None = None,
        group_by: str | None = None,
        select: list[str] | None = None,
        top: int = 100,
        skip: int = 0,
        count: bool = False,
        context: HttpRequest | Any = None,
    ) -> EntityResultSetDTO[DatastreamDTO]:
        """"""

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
                id=datastream.pk if select is None or "id" in select else Absent,
                name=datastream.name if select is None or "name" in select else Absent,
                description=datastream.description if select is None or "description" in select else Absent,
                unit_of_measurement=datastream.unit_of_measurement if select is None or "unit_of_measurement" in select else Absent,
                observation_type=datastream.observation_type if select is None or "observation_type" in select else Absent,
                observed_area=datastream.observed_area if select is None or "observed_area" in select else Absent,
                phenomenon_time=datastream.phenomenon_time_begin if select is None or "phenomenon_time_begin" in select else Absent,
                result_time=datastream.result_time_begin if select is None or "result_time_begin" in select else Absent,
                properties=datastream.properties if select is None or "properties" in select else Absent,
                thing_id=datastream.thing_id if select is None or "thing_id" in select else Absent,
                sensor_id=datastream.sensor_id if select is None or "sensor_id" in select else Absent,
                observed_property_id=datastream.observed_property_id if select is None or "observed_property_id" in select else Absent,
            ) for datastream in queryset
        }

        return EntityResultSetDTO(
            collections=collections,
            entities=entities
        )

    def get_observations(
        self,
        filters: _Node | None = None,
        orderby: list[OrderByField] | None = None,
        group_by: str | None = None,
        select: list[str] | None = None,
        top: int = 100,
        skip: int = 0,
        count: bool = False,
        context: HttpRequest | Any = None,
    ) -> EntityResultSetDTO[DatastreamDTO]:
        """"""

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
                id=observation.pk if select is None or "id" in select else Absent,
                phenomenon_time=str(observation.phenomenon_time_begin) if select is None or "phenomenon_time_begin" in select else Absent,
                result=observation.result if select is None or "result" in select else Absent,
                result_time=str(observation.result_time) if select is None or "result_time" in select else Absent,
                result_quality=observation.result_quality if select is None or "result_quality" in select else Absent,
                valid_time=observation.valid_time_begin if select is None or "valid_time" in select else Absent,
                parameters=observation.parameters if select is None or "parameters" in select else Absent,
                datastream_id=observation.datastream_id if select is None or "datastream_id" in select else Absent,
                feature_of_interest_id=observation.feature_of_interest_id if select is None or "feature_of_interest_id" in select else Absent,
            ) for observation in queryset
        }

        return EntityResultSetDTO(
            collections=collections,
            entities=entities
        )

    def get_features_of_interest(
        self,
        filters: _Node | None = None,
        orderby: list[OrderByField] | None = None,
        group_by: str | None = None,
        select: list[str] | None = None,
        top: int = 100,
        skip: int = 0,
        count: bool = False,
        context: HttpRequest | Any = None,
    ) -> EntityResultSetDTO[DatastreamDTO]:
        """"""

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
                encoding_type=feature_of_interest.encoding_type if select is None or "encoding_type" in select else Absent,
                feature=feature_of_interest.feature if select is None or "feature" in select else Absent,
                properties=feature_of_interest.properties if select is None or "properties" in select else Absent,
            ) for feature_of_interest in queryset
        }

        return EntityResultSetDTO(
            collections=collections,
            entities=entities
        )
