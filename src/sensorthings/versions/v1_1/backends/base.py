from abc import ABC, abstractmethod
from typing import Any, Callable, Awaitable
from odata_query.ast import _Node  # noqa
from pydantic.alias_generators import to_snake
from django.http import HttpRequest
from sensorthings.types import EntityType
from sensorthings.versions.v1_1 import sta
from sensorthings.versions.v1_1.dto import EntityResultSetDTO, OrderByField, ThingDTO, LocationDTO


class BaseBackendAdapter(ABC):
    """
    Abstract base class for SensorThings backend adapters.

    A backend adapter implements persistence- or service-specific operations
    for SensorThings entities (e.g., Thing, Datastream). Concrete adapters
    expose methods following a naming convention of the form: <method>_<entity>
    where:
    - <method> is one of: get, create, update, delete
    - <entity> is the lowercase SensorThings entity name (e.g., "things")
    """

    def resolve_operation(
        self,
        method: str,
        entity_type: EntityType
    ) -> Callable[..., object] | Callable[..., Awaitable[object]]:
        """
        Resolve a backend operation for the given method and entity type.

        This method validates that the requested operation and entity type
        are supported and then returns the corresponding callable on the
        backend adapter instance. The resolved callable is expected to
        implement the backend-specific behavior for the operation.
        """

        if method not in {"get", "create", "update", "delete"}:
            raise ValueError(f"Unsupported method: {method}")

        if str(entity_type.name) not in sta.entity_types:
            raise ValueError(f"Unsupported entity type: {entity_type}")

        operation_name = f"{method}_{to_snake(entity_type.set_name)}"

        operation = getattr(self, operation_name, None)

        if operation is None:
            raise NotImplementedError(
                f"{method} not implemented for entity {entity_type}"
            )

        return operation

    @abstractmethod
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
    ) -> EntityResultSetDTO[ThingDTO]:
        """
        Retrieve Thing entities from the backend.

        This method returns a collection of Thing entities matching the
        provided query parameters. Implementations are responsible for
        translating SensorThings-style query semantics (filters, ordering,
        pagination, projection) into backend-specific queries.
        """
        ...

    @abstractmethod
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
    ) -> EntityResultSetDTO[LocationDTO]:
        """
        Retrieve Location entities from the backend.

        This method returns a collection of Location entities matching the
        provided query parameters. Implementations are responsible for
        mapping SensorThings query semantics to the underlying storage or
        service layer.
        """
        ...
