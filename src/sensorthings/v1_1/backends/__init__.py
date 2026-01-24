from functools import lru_cache
from django.utils.module_loading import import_string
from sensorthings.v1_1.conf import app_settings
from .base import BaseBackendAdapter
from .null import NullBackendAdapter


@lru_cache(maxsize=1)
def get_backend_adapter() -> BaseBackendAdapter:
    """
    Return the configured SensorThings backend adapter instance.

    This function resolves the backend adapter specified by
    ``SENSORTHINGS_V1_1_BACKEND_ADAPTER`` (via ``app_settings.BACKEND_ADAPTER``),
    imports the adapter class, instantiates it, and returns a shared singleton
    instance.

    All backend adapters are required to subclass ``BaseBackendAdapter``.
    The adapter is loaded lazily and cached for the lifetime of the process,
    ensuring consistent behavior and avoiding repeated instantiation.

    If no backend adapter is configured, a ``NullBackendAdapter`` instance
    is returned.
    """

    backend_path = app_settings.BACKEND_ADAPTER

    if backend_path:
        backend_cls = import_string(backend_path)
    else:
        backend_cls = NullBackendAdapter

    return backend_cls()
