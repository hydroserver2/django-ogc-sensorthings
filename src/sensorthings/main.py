import functools
import types
from copy import deepcopy
from dataclasses import dataclass
from typing import Type, NewType, List, Optional, Literal
from django.urls import re_path
from ninja import NinjaAPI, Router
from sensorthings.engine import SensorThingsBaseEngine
from sensorthings.renderer import SensorThingsRenderer
from sensorthings.router import SensorThingsRouter
from sensorthings.factories import (SensorThingsRouterFactory, SensorThingsEndpointFactory,
                                    SensorThingsEndpointHookFactory)
from sensorthings.components.root.views import router as root_router, handle_advanced_path
from sensorthings.components.datastreams.views import datastream_router_factory
from sensorthings.components.featuresofinterest.views import feature_of_interest_router_factory
from sensorthings.components.historicallocations.views import historical_location_router_factory
from sensorthings.components.locations.views import location_router_factory
from sensorthings.components.observations.views import observation_router_factory
from sensorthings.components.observedproperties.views import observed_property_router_factory
from sensorthings.components.sensors.views import sensor_router_factory
from sensorthings.components.things.views import thing_router_factory


class SensorThingsAPI(NinjaAPI):
    def __init__(
            self,
            version: Literal["1.1"] = "1.1",
            engine: Optional[Type[NewType('SensorThingsEngine', SensorThingsBaseEngine)]] = None,
            extensions: Optional[List['SensorThingsExtension']] = None,
            **kwargs
    ):
        if kwargs.get('urls_namespace'):
            kwargs['urls_namespace'] = f'{kwargs.get("urls_namespace")}-sensorthings-v{version}-api'
        else:
            kwargs['urls_namespace'] = f'sensorthings-v{version}-api'

        kwargs['version'] = version

        super().__init__(renderer=SensorThingsRenderer(), **kwargs)

        self.routers = {}
        self.engine = engine
        self.get_response_schemas = {}
        self.extensions = extensions or []
        self.handle_advanced_path = self._copy_view(handle_advanced_path)

        self._stage_routers()
        self._initialize_default_routers()
        self.handle_advanced_path.__api__ = self

    def _stage_routers(self):
        """
        Stage routers for SensorThings components and extensions.
        """

        self.routers = self._get_default_routers()

        # Add extension routers and endpoints
        for extension in self.extensions:
            extension_copy = deepcopy(extension)
            self._add_extension_routers(extension_copy)
            self._add_extension_endpoints(extension_copy)

    @staticmethod
    def _get_default_routers():
        """
        Return the default routers for SensorThings components.
        """

        return {
            'datastream': deepcopy(datastream_router_factory),
            'feature_of_interest': deepcopy(feature_of_interest_router_factory),
            'historical_location': deepcopy(historical_location_router_factory),
            'location': deepcopy(location_router_factory),
            'observation': deepcopy(observation_router_factory),
            'observed_property': deepcopy(observed_property_router_factory),
            'sensor': deepcopy(sensor_router_factory),
            'thing': deepcopy(thing_router_factory),
        }

    def _add_extension_routers(self, extension):
        """
        Add routers from an extension to the main routers.
        """

        self.routers.update(extension.routers or {})

    def _add_extension_endpoints(self, extension):
        """
        Add endpoints from an extension to the appropriate routers.
        """

        for endpoint in extension.endpoints or []:
            if endpoint.router_name in self.routers:
                self.routers[endpoint.router_name].endpoints.append(endpoint)

    def _initialize_default_routers(self):
        """
        Add default and staged routers to the API.
        """

        self.add_router('', deepcopy(root_router))
        for name, router in self.routers.items():
            self.add_router('', self._build_router(name, router))

    def _build_router(self, name: str, router: SensorThingsRouterFactory) -> Router:
        """
        Build a SensorThings router with endpoints.
        """

        st_router = SensorThingsRouter(tags=router.tags)

        for endpoint in router.endpoints:
            self._configure_endpoint(st_router, name, endpoint)

        return st_router

    def _configure_endpoint(self, st_router, name, endpoint):
        """
        Configure a single endpoint with authentication, authorization, and response schemas.
        """

        # Apply extensions to the endpoint
        for extension in self.extensions:
            self._apply_endpoint_hook(extension, name, endpoint)

        # Store response schemas for GET requests
        self._store_get_response_schema(endpoint.view_response_schema)

        # Add endpoint to the router
        getattr(st_router, endpoint.view_method.__name__)(
            endpoint.endpoint_route,
            url_name=endpoint.view_function.__name__,
            response_schema=endpoint.view_response_schema,
            response_dict=endpoint.view_response_override,
            deprecated=not endpoint.enabled,
            auth=endpoint.view_authentication
        )(self._apply_authorization(endpoint.view_function, endpoint.view_authorization or []))

    def _apply_endpoint_hook(self, extension, name, endpoint):
        """
        Apply hooks from extensions to modify the endpoint's behavior.
        """

        endpoint_hook = next((
            hook for hook in extension.endpoint_hooks if hook.endpoint_name == endpoint.view_function.__name__
        ), None) if extension.endpoint_hooks else None

        if endpoint_hook:
            endpoint.view_response_schema = endpoint_hook.view_response_schema or endpoint.view_response_schema
            endpoint.view_response_override = endpoint_hook.view_response_override or endpoint.view_response_override
            endpoint.enabled = endpoint_hook.enabled and endpoint.enabled
            endpoint.view_authorization = endpoint_hook.view_authorization or endpoint.view_authorization
            endpoint.view_authentication = endpoint_hook.view_authentication or endpoint.view_authentication

            # Apply query params and body schema if provided by the hook
            if endpoint_hook.view_query_params:
                endpoint.view_function.__annotations__['params'] = endpoint_hook.view_query_params
            if endpoint_hook.view_body_schema:
                endpoint.view_function.__annotations__[name] = endpoint_hook.view_body_schema

            # Apply view wrapper if present
            if endpoint_hook.view_wrapper:
                endpoint.view_function = self._wrap_view_function(endpoint_hook.view_wrapper, endpoint.view_function)

    @staticmethod
    def _wrap_view_function(wrapper, view_function):
        """
        Wrap the view function with the provided wrapper.
        """

        @functools.wraps(view_function)
        def wrapped_view(*args, **kwargs):
            return wrapper(view_function)(*args, **kwargs)

        return wrapped_view

    def _store_get_response_schema(self, response_schema):
        """
        Store GET response schemas for later use.
        """

        if response_schema and response_schema.__name__.endswith('GetResponse'):
            self.get_response_schemas[response_schema.__name__] = response_schema

    def _get_urls(self):
        """
        Override to include advanced path handling.
        """

        urls = super()._get_urls()
        urls.append(re_path(r'^.*', self.handle_advanced_path, name='advanced_path_handler'))
        return urls

    @staticmethod
    def _apply_authorization(view_func, auth_callbacks):
        """
        Wrap view function with authorization checks.
        """

        @functools.wraps(view_func)
        def auth_wrapper(*args, **kwargs):
            for auth_callback in auth_callbacks:
                if auth_callback(*args, **kwargs) is not True:
                    return 403, {'detail': 'Forbidden'}
            return view_func(*args, **kwargs)

        return auth_wrapper

    @staticmethod
    def _copy_view(view):
        fn = types.FunctionType(
            view.__code__,
            view.__globals__,
            view.__name__,
            view.__defaults__,
            view.__closure__
        )
        fn.__dict__.update(view.__dict__)

        return fn


@dataclass
class SensorThingsExtension:
    routers: Optional[dict[str, 'SensorThingsRouterFactory']] = None
    endpoints: Optional[dict[str, 'SensorThingsEndpointFactory']] = None
    endpoint_hooks: Optional[List['SensorThingsEndpointHookFactory']] = None
