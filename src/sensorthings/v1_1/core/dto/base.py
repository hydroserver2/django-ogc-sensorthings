from typing import Optional, Dict, List, Union, ClassVar, TypeVar, Generic
from pydantic.alias_generators import to_snake
from dataclasses import dataclass, fields, field
from sensorthings.v1_1.core import iot
from sensorthings.types import Absent
from sensorthings.v1_1.conf import app_settings

T = TypeVar("T")


@dataclass
class BaseEntityDTO:
    iot_id: Optional[app_settings.ID_TYPE] = None

    _entity: ClassVar[str]
    _related_entities: ClassVar[List[str]]

    def build_response(
        self,
        select: Optional[List[str]] = None,
        expand: Optional[Dict[str, Union["CollectionDTO", "BaseEntityDTO"]]] = None
    ):
        select_set = set(select or [])
        expand_keys = set(expand or {})

        for related_entity in self._related_entities:
            related_entity_ref = to_snake(related_entity)
            related_entity_link_ref = f"{related_entity_ref}_link"
            related_nav_link = iot.build_nav_link(self._entity, self.iot_id, related_entity)

            if (not select_set or related_entity_link_ref in select_set) and related_entity_ref not in expand_keys:
                setattr(self, related_entity_link_ref, related_nav_link)

            if related_entity_ref in expand_keys:  # TODO
                setattr(self, f"{related_entity_ref}_count", expand[related_entity_ref]["count"])
                setattr(self, related_entity_ref, expand[related_entity_ref]["value"])
                setattr(self, f"{related_entity_ref}_next_link", f"{related_nav_link}?$skip=100&$top=100")

        if select_set:
            for f in fields(self):
                if f.name not in select_set:
                    setattr(self, f.name, Absent)


@dataclass
class CollectionDTO(Generic[T]):
    iot_count: Optional[int] = None
    value: List[BaseEntityDTO] = field(default_factory=list)

    def build_response(self):  # TODO
        setattr(self, "iot_next_link", "http://www.example.com/replace?$top=100&$skip=100")

        for entity in self.value:
            entity.build_response()


@dataclass
class GroupedCollectionDTO(Generic[T]):
    grouped_by: Optional[str] = None
    groups: Dict[Optional[app_settings.ID_TYPE], CollectionDTO[T]] = field(default_factory=dict)
