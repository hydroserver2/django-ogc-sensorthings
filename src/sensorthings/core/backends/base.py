from abc import ABC
from contextlib import asynccontextmanager
from typing import Callable, Awaitable
from pydantic.alias_generators import to_snake
from sensorthings.types import EntityType


class AbstractBaseBackendAdapter(ABC):

    @asynccontextmanager
    async def transaction(self):
        yield

    def resolve_operation(
        self,
        method: str,
        entity_type: EntityType,
    ) -> Callable[..., object] | Callable[..., Awaitable[object]]:
        if method not in {"get", "create", "update", "delete"}:
            raise ValueError(f"Unsupported method: {method}")

        operation_name = f"{method}_{to_snake(entity_type.set_name)}"
        operation = getattr(self, operation_name, None)

        if operation is None:
            raise NotImplementedError(
                f"{method} not implemented for entity {entity_type}"
            )

        return operation
