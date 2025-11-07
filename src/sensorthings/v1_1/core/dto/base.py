from typing import Optional, Dict, List, ClassVar, TypeVar, Generic
from dataclasses import dataclass, field
from sensorthings.v1_1.conf import app_settings

T = TypeVar("T")


@dataclass
class BaseEntityDTO:
    iot_id: Optional[app_settings.ID_TYPE] = None

    _entity: ClassVar[str]
    _related_entities: ClassVar[List[str]]


@dataclass
class CollectionDTO(Generic[T]):
    iot_count: Optional[int] = None
    value: List[BaseEntityDTO] = field(default_factory=list)


@dataclass
class GroupedCollectionDTO(Generic[T]):
    grouped_by: Optional[str] = None
    groups: Dict[Optional[app_settings.ID_TYPE], CollectionDTO[T]] = field(
        default_factory=dict
    )
