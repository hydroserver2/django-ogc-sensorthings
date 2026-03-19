from typing import Any
from odata_query.ast import _Node  # noqa
from django.http import HttpRequest
from sensorthings.versions.v1_1.dto import EntityResultSetDTO, OrderByField
from ..base import BaseBackendAdapter


class NullBackendAdapter(
    BaseBackendAdapter,
):
    """"""

    @staticmethod
    async def get_collection() -> EntityResultSetDTO[EntityResultSetDTO]:
        """"""

        return EntityResultSetDTO(
            collections={},
            entities={}
        )

    async def get_things(
        self,
        filters: _Node | None = None,
        orderby: list[OrderByField] | None = None,
        group_by: str | None = None,
        select: list[str] | None = None,
        top: int = 100,
        skip: int = 0,
        count: bool = False,
        context: HttpRequest | Any = None,
    ) -> EntityResultSetDTO[EntityResultSetDTO]:
        """"""

        return await self.get_collection()

    async def get_locations(
        self,
        filters: _Node | None = None,
        orderby: list[OrderByField] | None = None,
        group_by: str | None = None,
        select: list[str] | None = None,
        top: int = 100,
        skip: int = 0,
        count: bool = False,
        context: HttpRequest | Any = None,
    ) -> EntityResultSetDTO[EntityResultSetDTO]:
        """"""

        return await self.get_collection()

    async def get_historical_locations(
        self,
        filters: _Node | None = None,
        orderby: list[OrderByField] | None = None,
        group_by: str | None = None,
        select: list[str] | None = None,
        top: int = 100,
        skip: int = 0,
        count: bool = False,
        context: HttpRequest | Any = None,
    ) -> EntityResultSetDTO[EntityResultSetDTO]:
        """"""

        return await self.get_collection()

    async def get_sensors(
        self,
        filters: _Node | None = None,
        orderby: list[OrderByField] | None = None,
        group_by: str | None = None,
        select: list[str] | None = None,
        top: int = 100,
        skip: int = 0,
        count: bool = False,
        context: HttpRequest | Any = None,
    ) -> EntityResultSetDTO[EntityResultSetDTO]:
        """"""

        return await self.get_collection()

    async def get_observed_properties(
        self,
        filters: _Node | None = None,
        orderby: list[OrderByField] | None = None,
        group_by: str | None = None,
        select: list[str] | None = None,
        top: int = 100,
        skip: int = 0,
        count: bool = False,
        context: HttpRequest | Any = None,
    ) -> EntityResultSetDTO[EntityResultSetDTO]:
        """"""

        return await self.get_collection()

    async def get_datastreams(
        self,
        filters: _Node | None = None,
        orderby: list[OrderByField] | None = None,
        group_by: str | None = None,
        select: list[str] | None = None,
        top: int = 100,
        skip: int = 0,
        count: bool = False,
        context: HttpRequest | Any = None,
    ) -> EntityResultSetDTO[EntityResultSetDTO]:
        """"""

        return await self.get_collection()

    async def get_observations(
        self,
        filters: _Node | None = None,
        orderby: list[OrderByField] | None = None,
        group_by: str | None = None,
        select: list[str] | None = None,
        top: int = 100,
        skip: int = 0,
        count: bool = False,
        context: HttpRequest | Any = None,
    ) -> EntityResultSetDTO[EntityResultSetDTO]:
        """"""

        return await self.get_collection()

    async def get_features_of_interest(
        self,
        filters: _Node | None = None,
        orderby: list[OrderByField] | None = None,
        group_by: str | None = None,
        select: list[str] | None = None,
        top: int = 100,
        skip: int = 0,
        count: bool = False,
        context: HttpRequest | Any = None,
    ) -> EntityResultSetDTO[EntityResultSetDTO]:
        """"""

        return await self.get_collection()
