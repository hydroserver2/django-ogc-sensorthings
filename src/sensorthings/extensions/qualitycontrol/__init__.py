from sensorthings import SensorThingsExtension
from .views import quality_control_endpoints

quality_control_extension = SensorThingsExtension(
    endpoints=quality_control_endpoints,
)

__all__ = [
    "quality_control_extension",
]
