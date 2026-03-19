from typing import Any, Callable, Optional
from dataclasses import dataclass
from ninja import Router


@dataclass(frozen=True)
class OperationDefinition:
    path: str
    methods: list[str]
    view_func: Callable
    response: dict[int, Any] | None = None
    auth: Optional[Callable] = None
    by_alias: bool = True
    exclude_none: bool = True
    exclude_unset: bool = True
    include_in_schema: bool = True


@dataclass
class RouterDefinition:
    router: Router
    operations: dict[str, OperationDefinition]

    def apply(self) -> Router:
        """
        Register all API operations on the router.
        """

        for operation in self.operations.values():
            self.router.add_api_operation(
                path=operation.path,
                methods=operation.methods,
                view_func=operation.view_func,
                auth=operation.auth,
                response=operation.response,
                by_alias=operation.by_alias,
                exclude_none=operation.exclude_none,
                exclude_unset=operation.exclude_unset,
                include_in_schema=operation.include_in_schema,
            )

        return self.router
