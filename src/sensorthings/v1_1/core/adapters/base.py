from abc import ABC, abstractmethod
from typing import Any
from odata_query.ast import _Node  # noqa
from django.http import HttpRequest
from sensorthings.v1_1.core.dto import GroupedCollectionDTO, ThingDTO, OrderByField


class BackendAdapter(ABC):
    """"""

    @abstractmethod
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
    ) -> GroupedCollectionDTO[ThingDTO]:
        """"""
        ...
