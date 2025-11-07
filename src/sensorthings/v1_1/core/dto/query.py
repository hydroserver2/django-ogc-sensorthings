from enum import Enum
from odata_query.ast import _Node  # noqa
from dataclasses import dataclass, field


class OrderByDirection(str, Enum):
    ASC = "asc"
    DESC = "desc"


@dataclass
class OrderByField:
    path: list[str]
    direction: OrderByDirection = OrderByDirection.ASC


@dataclass
class QueryDTO:
    select: list[str] | None = None
    expand: dict[str, "QueryDTO"] = field(default_factory=dict)
    filter: _Node | None = None
    count: bool = False
    order_by: list[OrderByField] = field(default_factory=list)
    skip: int = 0
    top: int = 100
