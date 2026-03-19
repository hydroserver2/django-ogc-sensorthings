from typing import Dict, List, TypeVar, Generic
from dataclasses import dataclass, field
from sensorthings.versions.v1_1 import app_settings

T = TypeVar("T")


@dataclass
class BaseEntityDTO:
    """
    Represents a base SensorThings entity with an identifier.
    """

    id: app_settings.ID_TYPE | None = None


@dataclass
class CollectionDTO(Generic[T]):
    """
    Represents a collection of entities with an optional total count.

    Each collection references entities by ID, avoiding duplication of the
    entity objects. Counts may be different from the number of entity IDs
    when results are paginated.
    """

    entity_count: int | None = None
    entity_ids: List[app_settings.ID_TYPE] = field(default_factory=list)


@dataclass
class EntityResultSetDTO(Generic[T]):
    """
    Represents a set of entities grouped into multiple collections.

    This structure separates the canonical entity objects from the collections
    that reference them by ID, ensuring that entities are not duplicated.
    Collections are keyed by collection ID, and each collection
    can have its own count and membership.

    Typical usage:
        1. Access `entities` to retrieve the canonical object for a given ID.
        2. Use `collections` to see which entities belong to which collection.
        3. The `grouped_by` field documents the property or field used to
           group the entities.
    """

    grouped_by: str | None = None
    collections: Dict[app_settings.ID_TYPE, CollectionDTO] = field(default_factory=dict)
    entities: Dict[app_settings.ID_TYPE, BaseEntityDTO] = field(default_factory=dict)
