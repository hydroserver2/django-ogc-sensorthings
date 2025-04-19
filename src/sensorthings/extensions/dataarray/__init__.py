from sensorthings import SensorThingsExtension
from .engine import DataArrayBaseEngine
from .views import data_array_endpoints, data_array_endpoint_hooks

data_array_extension = SensorThingsExtension(
    endpoints=data_array_endpoints,
    endpoint_hooks=data_array_endpoint_hooks
)

__all__ = [
    "data_array_extension",
    "DataArrayBaseEngine"
]
