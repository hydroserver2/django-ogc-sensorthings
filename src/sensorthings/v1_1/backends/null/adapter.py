from typing import Any
from odata_query.ast import _Node  # noqa
from django.http import HttpRequest
from sensorthings.v1_1.dto import EntityResultSetDTO, CollectionDTO, OrderByField, ThingDTO, LocationDTO
from ..base import BaseBackendAdapter


class NullBackendAdapter(
    BaseBackendAdapter,
):
    """"""

    async def get_things(
        self,
        filters: _Node | None = None,
        order_by: list[OrderByField] | None = None,
        group_by: str | None = None,
        select: list[str] | None = None,
        top: int = 100,
        skip: int = 0,
        count: bool = False,
        context: HttpRequest | Any = None,
    ) -> EntityResultSetDTO[ThingDTO]:
        """"""

        return EntityResultSetDTO(
            collections={
                1: CollectionDTO(entity_count=1, entity_ids=[1])
            },
            entities={
                1: ThingDTO(
                    iot_id=1, name="Test Thing", description="This is a test thing.", properties={"code": "A"}
                )
            }
        )

    async def get_locations(
        self,
        filters: _Node | None = None,
        order_by: list[OrderByField] | None = None,
        group_by: str | None = None,
        select: list[str] | None = None,
        top: int = 100,
        skip: int = 0,
        count: bool = False,
        context: HttpRequest | Any = None,
    ) -> EntityResultSetDTO[LocationDTO]:
        """"""

        return EntityResultSetDTO(
            collections={
                1: CollectionDTO(entity_count=1, entity_ids=[1])
            },
            entities={
                1: LocationDTO(
                    iot_id=1, name="Test Location", description="This is a test location.", location={},
                    encoding_type="application/geo+json", properties={"code": "A"}
                )
            }
        )
