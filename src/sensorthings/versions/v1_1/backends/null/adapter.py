from typing import Any
from django.http import HttpRequest
from sensorthings.versions.v1_1.conf import app_settings
from sensorthings.versions.v1_1.dto import (
    EntityResultSetDTO, ThingDTO, LocationDTO,
    HistoricalLocationDTO, SensorDTO, ObservedPropertyDTO,
    DatastreamDTO, ObservationDTO, FeatureOfInterestDTO,
)
from ..base import BaseBackendAdapter


class NullBackendAdapter(BaseBackendAdapter):

    @staticmethod
    async def _empty() -> EntityResultSetDTO:
        return EntityResultSetDTO(collections={}, entities={})

    # ------------------------------------------------------------------
    # Things
    # ------------------------------------------------------------------

    async def get_things(
        self,
        filters=None,
        orderby=None,
        group_by=None,
        select=None,
        top=100,
        skip=0,
        count=False,
        context=None
    ) -> EntityResultSetDTO[ThingDTO]:
        return await self._empty()

    async def create_things(
        self,
        payload: list[ThingDTO],
        context: HttpRequest | Any = None
    ) -> list[app_settings.ID_TYPE]:
        return []

    async def update_things(
        self,
        payload: dict[app_settings.ID_TYPE, ThingDTO],
        context: HttpRequest | Any = None
    ) -> None:
        pass

    async def delete_things(
        self,
        entity_ids: list[app_settings.ID_TYPE],
        context: HttpRequest | Any = None
    ) -> None:
        pass

    # ------------------------------------------------------------------
    # Locations
    # ------------------------------------------------------------------

    async def get_locations(
        self, filters=None,
        orderby=None,
        group_by=None,
        select=None,
        top=100,
        skip=0,
        count=False,
        context=None
    ) -> EntityResultSetDTO[LocationDTO]:
        return await self._empty()

    async def create_locations(
        self,
        payload: list[LocationDTO],
        context: HttpRequest | Any = None
    ) -> list[app_settings.ID_TYPE]:
        return []

    async def update_locations(
        self,
        payload: dict[app_settings.ID_TYPE, LocationDTO],
        context: HttpRequest | Any = None
    ) -> None:
        pass

    async def delete_locations(
        self,
        entity_ids: list[app_settings.ID_TYPE],
        context: HttpRequest | Any = None
    ) -> None:
        pass

    # ------------------------------------------------------------------
    # Historical Locations
    # ------------------------------------------------------------------

    async def get_historical_locations(
        self,
        filters=None,
        orderby=None,
        group_by=None,
        select=None,
        top=100,
        skip=0,
        count=False,
        context=None
    ) -> EntityResultSetDTO[HistoricalLocationDTO]:
        return await self._empty()

    async def create_historical_locations(
        self,
        payload: list[HistoricalLocationDTO],
        context: HttpRequest | Any = None
    ) -> list[app_settings.ID_TYPE]:
        return []

    async def update_historical_locations(
        self,
        payload: dict[app_settings.ID_TYPE, HistoricalLocationDTO],
        context: HttpRequest | Any = None
    ) -> None:
        pass

    async def delete_historical_locations(
        self, entity_ids: list[app_settings.ID_TYPE],
        context: HttpRequest | Any = None
    ) -> None:
        pass

    # ------------------------------------------------------------------
    # Sensors
    # ------------------------------------------------------------------

    async def get_sensors(
        self,
        filters=None,
        orderby=None,
        group_by=None,
        select=None,
        top=100,
        skip=0,
        count=False,
        context=None
    ) -> EntityResultSetDTO[SensorDTO]:
        return await self._empty()

    async def create_sensors(
        self,
        payload: list[SensorDTO],
        context: HttpRequest | Any = None
    ) -> list[app_settings.ID_TYPE]:
        return []

    async def update_sensors(
        self,
        payload: dict[app_settings.ID_TYPE, SensorDTO],
        context: HttpRequest | Any = None
    ) -> None:
        pass

    async def delete_sensors(
        self,
        entity_ids: list[app_settings.ID_TYPE],
        context: HttpRequest | Any = None
    ) -> None:
        pass

    # ------------------------------------------------------------------
    # Observed Properties
    # ------------------------------------------------------------------

    async def get_observed_properties(
        self,
        filters=None,
        orderby=None,
        group_by=None,
        select=None,
        top=100,
        skip=0,
        count=False,
        context=None
    ) -> EntityResultSetDTO[ObservedPropertyDTO]:
        return await self._empty()

    async def create_observed_properties(
        self,
        payload: list[ObservedPropertyDTO],
        context: HttpRequest | Any = None
    ) -> list[app_settings.ID_TYPE]:
        return []

    async def update_observed_properties(
        self,
        payload: dict[app_settings.ID_TYPE, ObservedPropertyDTO],
        context: HttpRequest | Any = None
    ) -> None:
        pass

    async def delete_observed_properties(
        self,
        entity_ids: list[app_settings.ID_TYPE],
        context: HttpRequest | Any = None
    ) -> None:
        pass

    # ------------------------------------------------------------------
    # Datastreams
    # ------------------------------------------------------------------

    async def get_datastreams(
        self,
        filters=None,
        orderby=None,
        group_by=None,
        select=None,
        top=100,
        skip=0,
        count=False,
        context=None
    ) -> EntityResultSetDTO[DatastreamDTO]:
        return await self._empty()

    async def create_datastreams(
        self,
        payload: list[DatastreamDTO],
        context: HttpRequest | Any = None
    ) -> list[app_settings.ID_TYPE]:
        return []

    async def update_datastreams(
        self, payload: dict[app_settings.ID_TYPE, DatastreamDTO],
        context: HttpRequest | Any = None
    ) -> None:
        pass

    async def delete_datastreams(
        self,
        entity_ids: list[app_settings.ID_TYPE],
        context: HttpRequest | Any = None
    ) -> None:
        pass

    # ------------------------------------------------------------------
    # Observations
    # ------------------------------------------------------------------

    async def get_observations(
        self,
        filters=None,
        orderby=None,
        group_by=None,
        select=None,
        top=100,
        skip=0,
        count=False,
        context=None
    ) -> EntityResultSetDTO[ObservationDTO]:
        return await self._empty()

    async def create_observations(
        self,
        payload: list[ObservationDTO],
        context: HttpRequest | Any = None
    ) -> list[app_settings.ID_TYPE]:
        return []

    async def update_observations(
        self,
        payload: dict[app_settings.ID_TYPE, ObservationDTO],
        context: HttpRequest | Any = None
    ) -> None:
        pass

    async def delete_observations(
        self,
        entity_ids: list[app_settings.ID_TYPE],
        context: HttpRequest | Any = None
    ) -> None:
        pass

    # ------------------------------------------------------------------
    # Features of Interest
    # ------------------------------------------------------------------

    async def get_features_of_interest(
        self,
        filters=None,
        orderby=None,
        group_by=None,
        select=None,
        top=100,
        skip=0,
        count=False,
        context=None
    ) -> EntityResultSetDTO[FeatureOfInterestDTO]:
        return await self._empty()

    async def create_features_of_interest(
        self,
        payload: list[FeatureOfInterestDTO],
        context: HttpRequest | Any = None
    ) -> list[app_settings.ID_TYPE]:
        return []

    async def update_features_of_interest(
        self,
        payload: dict[app_settings.ID_TYPE, FeatureOfInterestDTO],
        context: HttpRequest | Any = None
    ) -> None:
        pass

    async def delete_features_of_interest(
        self,
        entity_ids: list[app_settings.ID_TYPE],
        context: HttpRequest | Any = None
    ) -> None:
        pass
