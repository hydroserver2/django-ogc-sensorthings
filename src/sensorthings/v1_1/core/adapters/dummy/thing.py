from typing import Any
from odata_query.ast import _Node  # noqa
from django.http import HttpRequest
from sensorthings.v1_1.core.dto import (
    GroupedCollectionDTO,
    CollectionDTO,
    ThingDTO,
    OrderByField,
)


class ThingAdapterMixin:
    def get_things(
        self,
        filters: _Node | None = None,
        order_by: list[OrderByField] | None = None,
        group_by: str | None = None,
        select: list[str] | None = None,
        top: int = 100,
        skip: int = 0,
        count: bool = False,
        context: HttpRequest | Any = None,
    ) -> GroupedCollectionDTO[ThingDTO] | CollectionDTO[ThingDTO]:
        """"""

        thing = ThingDTO(
            iot_id=1,
            name="Example Thing",
            description="This is an example of a SensorThings thing entity.",
            properties={
                "region": "A",
                "code": 12345
            }
        )

        return CollectionDTO(iot_count=10, value=[thing])
