from abc import abstractmethod
from typing import Any
from odata_query.ast import _Node  # noqa
from django.http import HttpRequest
from sensorthings.core.backends.base import BaseBackendAdapter as _CoreBaseBackendAdapter
from sensorthings.versions.v1_1.conf import app_settings
from sensorthings.versions.v1_1.dto import (
    EntityResultSetDTO, OrderByField,
    ThingDTO, LocationDTO, HistoricalLocationDTO,
    SensorDTO, ObservedPropertyDTO, DatastreamDTO,
    ObservationDTO, FeatureOfInterestDTO,
)


BASE_CONFORMANCE_URI = "http://www.opengis.net/spec/iot_sensing/1.1/req"

conformance_registry: list[str] = []


class BaseBackendAdapter(_CoreBaseBackendAdapter):

    def get_server_settings(self) -> dict:
        return {"conformance": list(conformance_registry)}

    # ------------------------------------------------------------------
    # Things
    # ------------------------------------------------------------------

    @abstractmethod
    async def get_things(
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
        ...

    @abstractmethod
    async def create_things(
        self,
        payload: list[ThingDTO],
        context: HttpRequest | Any = None,
    ) -> list[app_settings.ID_TYPE]:
        ...

    @abstractmethod
    async def update_things(
        self,
        payload: dict[app_settings.ID_TYPE, ThingDTO],
        context: HttpRequest | Any = None,
    ) -> None:
        ...

    @abstractmethod
    async def delete_things(
        self,
        entity_ids: list[app_settings.ID_TYPE],
        context: HttpRequest | Any = None,
    ) -> None:
        ...

    # ------------------------------------------------------------------
    # Locations
    # ------------------------------------------------------------------

    @abstractmethod
    async def get_locations(
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
        ...

    @abstractmethod
    async def create_locations(
        self,
        payload: list[LocationDTO],
        context: HttpRequest | Any = None,
    ) -> list[app_settings.ID_TYPE]:
        ...

    @abstractmethod
    async def update_locations(
        self,
        payload: dict[app_settings.ID_TYPE, LocationDTO],
        context: HttpRequest | Any = None,
    ) -> None:
        ...

    @abstractmethod
    async def delete_locations(
        self,
        entity_ids: list[app_settings.ID_TYPE],
        context: HttpRequest | Any = None,
    ) -> None:
        ...

    # ------------------------------------------------------------------
    # Historical Locations
    # ------------------------------------------------------------------

    @abstractmethod
    async def get_historical_locations(
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
        ...

    @abstractmethod
    async def create_historical_locations(
        self,
        payload: list[HistoricalLocationDTO],
        context: HttpRequest | Any = None,
    ) -> list[app_settings.ID_TYPE]:
        ...

    @abstractmethod
    async def update_historical_locations(
        self,
        payload: dict[app_settings.ID_TYPE, HistoricalLocationDTO],
        context: HttpRequest | Any = None,
    ) -> None:
        ...

    @abstractmethod
    async def delete_historical_locations(
        self,
        entity_ids: list[app_settings.ID_TYPE],
        context: HttpRequest | Any = None,
    ) -> None:
        ...

    # ------------------------------------------------------------------
    # Sensors
    # ------------------------------------------------------------------

    @abstractmethod
    async def get_sensors(
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
        ...

    @abstractmethod
    async def create_sensors(
        self,
        payload: list[SensorDTO],
        context: HttpRequest | Any = None,
    ) -> list[app_settings.ID_TYPE]:
        ...

    @abstractmethod
    async def update_sensors(
        self,
        payload: dict[app_settings.ID_TYPE, SensorDTO],
        context: HttpRequest | Any = None,
    ) -> None:
        ...

    @abstractmethod
    async def delete_sensors(
        self,
        entity_ids: list[app_settings.ID_TYPE],
        context: HttpRequest | Any = None,
    ) -> None:
        ...

    # ------------------------------------------------------------------
    # Observed Properties
    # ------------------------------------------------------------------

    @abstractmethod
    async def get_observed_properties(
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
        ...

    @abstractmethod
    async def create_observed_properties(
        self,
        payload: list[ObservedPropertyDTO],
        context: HttpRequest | Any = None,
    ) -> list[app_settings.ID_TYPE]:
        ...

    @abstractmethod
    async def update_observed_properties(
        self,
        payload: dict[app_settings.ID_TYPE, ObservedPropertyDTO],
        context: HttpRequest | Any = None,
    ) -> None:
        ...

    @abstractmethod
    async def delete_observed_properties(
        self,
        entity_ids: list[app_settings.ID_TYPE],
        context: HttpRequest | Any = None,
    ) -> None:
        ...

    # ------------------------------------------------------------------
    # Datastreams
    # ------------------------------------------------------------------

    @abstractmethod
    async def get_datastreams(
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
        ...

    @abstractmethod
    async def create_datastreams(
        self,
        payload: list[DatastreamDTO],
        context: HttpRequest | Any = None,
    ) -> list[app_settings.ID_TYPE]:
        ...

    @abstractmethod
    async def update_datastreams(
        self,
        payload: dict[app_settings.ID_TYPE, DatastreamDTO],
        context: HttpRequest | Any = None,
    ) -> None:
        ...

    @abstractmethod
    async def delete_datastreams(
        self,
        entity_ids: list[app_settings.ID_TYPE],
        context: HttpRequest | Any = None,
    ) -> None:
        ...

    # ------------------------------------------------------------------
    # Observations
    # ------------------------------------------------------------------

    @abstractmethod
    async def get_observations(
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
        ...

    @abstractmethod
    async def create_observations(
        self,
        payload: list[ObservationDTO],
        context: HttpRequest | Any = None,
    ) -> list[app_settings.ID_TYPE]:
        ...

    @abstractmethod
    async def update_observations(
        self,
        payload: dict[app_settings.ID_TYPE, ObservationDTO],
        context: HttpRequest | Any = None,
    ) -> None:
        ...

    @abstractmethod
    async def delete_observations(
        self,
        entity_ids: list[app_settings.ID_TYPE],
        context: HttpRequest | Any = None,
    ) -> None:
        ...

    # ------------------------------------------------------------------
    # Features of Interest
    # ------------------------------------------------------------------

    @abstractmethod
    async def get_features_of_interest(
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
        ...

    @abstractmethod
    async def create_features_of_interest(
        self,
        payload: list[FeatureOfInterestDTO],
        context: HttpRequest | Any = None,
    ) -> list[app_settings.ID_TYPE]:
        ...

    @abstractmethod
    async def update_features_of_interest(
        self,
        payload: dict[app_settings.ID_TYPE, FeatureOfInterestDTO],
        context: HttpRequest | Any = None,
    ) -> None:
        ...

    @abstractmethod
    async def delete_features_of_interest(
        self,
        entity_ids: list[app_settings.ID_TYPE],
        context: HttpRequest | Any = None,
    ) -> None:
        ...
