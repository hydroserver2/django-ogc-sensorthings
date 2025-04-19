import sensorthings.components.field_schemas as component_field_schemas
from uuid import UUID
from typing import ForwardRef
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpRequest
from django.urls import resolve
from django.urls.exceptions import Http404
from sensorthings.components import field_schemas
from sensorthings import settings


id_qualifier = settings.ST_API_ID_QUALIFIER
id_type = settings.ST_API_ID_TYPE


class SensorThingsMiddleware(MiddlewareMixin):
    """
    Middleware for processing SensorThings API views.

    This middleware attaches the SensorThings engine to the request and handles advanced paths.
    """

    def process_view(self, request: HttpRequest, view_func, view_args, view_kwargs):
        """
        Process the view before it is called.

        Parameters
        ----------
        request : HttpRequest
            The current HTTP request.
        view_func : Callable
            The view function that will be called.
        view_args : tuple
            The positional arguments for the view function.
        view_kwargs : dict
            The keyword arguments for the view function.

        Returns
        -------
        Callable or None
            The view function to be called, or None if no processing is needed.
        """

        # Check that the request resolved to part of the SensorThings API.
        if not hasattr(request, 'resolver_match') or (not any(
            namespace.endswith(('sensorthings-v1.0-api', 'sensorthings-v1.1-api'))
            for namespace in request.resolver_match.namespaces
        )) or request.resolver_match.url_name in ['openapi-view', 'openapi-json']:
            return None

        # Attach the SensorThings engine to the request.
        sensorthings_api = getattr(view_func, '__api__', None) or view_func.__self__.api
        request.engine = sensorthings_api.engine(
            request=request,
            get_response_schemas=sensorthings_api.get_response_schemas,
        )
        request.nested_path = []
        request.ref_response = False
        request.value_response = False

        # Attempt to resolve advanced SensorThings paths (e.g. nested resource paths, addresses to values, etc.)
        if request.resolver_match.url_name == 'advanced_path_handler':
            view_func = self.handle_advanced_path(request=request)

        # Attach the base SensorThings URL and sub-path to the request object
        base_url = (
            settings.PROXY_BASE_URL
            if settings.PROXY_BASE_URL is not None
            else f"{request.scheme}://{request.get_host()}"
        )
        request.sensorthings_url = f"{base_url}/{settings.ST_API_PREFIX}/v{view_func.__self__.api.version}"
        request.sensorthings_path = '/'.join(
            request.path_info.split('/')[len(request.resolver_match.route.split('/')):]
        )

        # Call the updated view function.
        return view_func(request, *view_args, **request.resolver_match.kwargs)

    def handle_advanced_path(self, request: HttpRequest):
        """
        Handle advanced SensorThings paths.

        Parameters
        ----------
        request : HttpRequest
            The current HTTP request.

        Returns
        -------
        Callable
            The resolved view function for the advanced path.

        Raises
        ------
        Http404
            If the path cannot be resolved.
        """

        # Advanced SensorThings paths are only supported on GET requests.
        if request.method != 'GET':
            raise Http404

        # Split the path into components to check individually.
        route_length = len(request.resolver_match.route.split('/'))
        path_components = request.path_info.split('/')[route_length:]
        path_prefix = '/'.join(request.path_info.split('/')[:route_length])
        effective_resolved_path = None

        for i, path_component in enumerate(path_components):
            try:
                resolved_path = resolve(f'{path_prefix}/{path_component}')
                if effective_resolved_path and effective_resolved_path.url_name.startswith('list'):
                    raise Http404

                # Set the effective resolved path based on the URL name.
                if resolved_path.url_name.startswith('list'):
                    effective_resolved_path = resolved_path
                elif resolved_path.url_name.startswith('get'):
                    effective_resolved_path = resolved_path
                    request.nested_path.append((  # noqa
                        self.get_component_model_from_path(path_component),
                        next(iter(effective_resolved_path.kwargs.items()))[0],
                        next(iter(effective_resolved_path.kwargs.items()))[1],
                    ))
                else:
                    raise Http404
            except StopIteration:
                raise Http404
            except Http404:
                if i == 0 or path_components[i - 1] in ['$value', '$ref'] or not effective_resolved_path:
                    raise Http404
                elif path_component == '$ref' and effective_resolved_path.url_name.startswith('list'):
                    request.ref_response = True
                elif path_component == '$value':
                    request.value_response = True
                else:
                    try:
                        component_model = self.get_component_model_from_path(path_components[i - 1])
                        try:
                            field = next(
                                field for field in component_model.model_fields.values()
                                if path_component == field.alias
                            )
                        except StopIteration:
                            raise Http404

                        field_annotation = getattr(field_schemas, field.annotation.__forward_arg__) if (
                            isinstance(field.annotation, ForwardRef)
                        ) else field.annotation

                        engine_ref = getattr(
                            field_annotation, 'model_config', {}
                        ).get('json_schema_extra', {}).get('name_ref', (None,))[0]

                        if engine_ref:
                            resolved_path = resolve(
                                f'{path_prefix}/{engine_ref}({id_qualifier}{self.get_placeholder_id()}{id_qualifier})'
                            )
                            effective_resolved_path = resolved_path
                            request.nested_path.append((  # noqa
                                self.get_component_model_from_path(path_component),
                                next(iter(effective_resolved_path.kwargs.items()))[0],
                                None,
                            ))
                        else:
                            query_dict = request.GET.copy()
                            query_dict['$select'] = field.alias
                            request.GET = query_dict
                    except StopIteration:
                        raise Http404

        # Update the request's resolver match with the effective resolved path.
        request.resolver_match = effective_resolved_path

        return effective_resolved_path.func

    @staticmethod
    def get_component_model_from_path(path_component: str):
        """
        Get the component model from the path component.

        Parameters
        ----------
        path_component : str
            The path component.

        Returns
        -------
        Type
            The component model class.
        """

        if '(' in path_component:
            path_component = path_component.split('(')[0]

        if path_component in dir(component_field_schemas):
            return getattr(component_field_schemas, path_component)
        else:
            return next(
                getattr(component_field_schemas, schema) for schema in dir(component_field_schemas)
                if getattr(
                    getattr(component_field_schemas, schema), 'model_config', {}
                ).get('json_schema_extra', {}).get('name_ref', (None,))[0] == path_component
            )

    @staticmethod
    def get_placeholder_id():
        """
        Get a placeholder ID based on the ID type.

        Returns
        -------
        Union[str, int, UUID]
            A placeholder ID.
        """

        if id_type == str:
            return '0'
        elif id_type == int:
            return 0
        elif id_type == UUID:
            return '00000000-0000-0000-0000-000000000000'
        else:
            return '0'
