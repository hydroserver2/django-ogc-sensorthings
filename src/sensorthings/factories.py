from ninja import Schema
from typing import Type, Optional, List, Callable, Union
from dataclasses import dataclass
from sensorthings.router import SensorThingsRouter


@dataclass
class SensorThingsRouterFactory:
    name: str
    tags: List[str]
    endpoints: List['SensorThingsEndpointFactory']


@dataclass
class SensorThingsEndpointFactory:
    router_name: str
    endpoint_route: str
    view_function: Callable
    view_method: Union[
        SensorThingsRouter.st_list, SensorThingsRouter.st_get, SensorThingsRouter.st_post, SensorThingsRouter.st_patch,
        SensorThingsRouter.st_delete
    ]
    enabled: Optional[bool] = True
    view_authentication: Optional[Callable] = None
    view_authorization: Optional[Callable] = None
    view_response_schema: Optional[Type[Schema]] = None
    view_response_override: Optional[dict] = None


@dataclass
class SensorThingsEndpointHookFactory:
    endpoint_name: str
    view_wrapper: Optional[Callable] = None
    enabled: Optional[bool] = True
    view_authentication: Optional[Union[Callable, List[Callable]]] = None
    view_authorization: Optional[Union[Callable, List[Callable]]] = None
    view_query_params: Optional[Type[Schema]] = None
    view_body_schema: Optional[Type[Schema]] = None
    view_response_schema: Optional[Type[Schema]] = None
    view_response_override: Optional[dict] = None
