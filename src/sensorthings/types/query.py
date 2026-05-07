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
