from abc import ABC, abstractmethod
from typing import Any
from odata_query.ast import _Node  # noqa
from django.http import HttpRequest
from sensorthings.versions.v1_1.conf import app_settings
from sensorthings.versions.v1_1.dto import EntityResultSetDTO, OrderByField
from sensorthings.versions.v1_1.extensions.multidatastream.dto import MultiDatastreamDTO


class BaseMultiDatastreamAdapterMixin(ABC):

    @abstractmethod
    async def get_multi_datastreams(
        self,
        filters: _Node | None = None,
        orderby: list[OrderByField] | None = None,
        group_by: tuple[str, list] | None = None,
        select: list[str] | None = None,
        top: int = 100,
        skip: int = 0,
        count: bool = False,
        context: HttpRequest | Any = None,
    ) -> EntityResultSetDTO[MultiDatastreamDTO]:
        ...

    @abstractmethod
    async def create_multi_datastreams(
        self,
        payload: list[MultiDatastreamDTO],
        context: HttpRequest | Any = None,
    ) -> list[app_settings.ID_TYPE]:
        ...

    @abstractmethod
    async def update_multi_datastreams(
        self,
        payload: dict[app_settings.ID_TYPE, MultiDatastreamDTO],
        context: HttpRequest | Any = None,
    ) -> None:
        ...

    @abstractmethod
    async def delete_multi_datastreams(
        self,
        entity_ids: list[app_settings.ID_TYPE],
        context: HttpRequest | Any = None,
    ) -> None:
        ...
