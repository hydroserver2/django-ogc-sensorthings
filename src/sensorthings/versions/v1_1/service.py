from sensorthings.core.service import SensorThingsService
from sensorthings.versions.v1_1 import STA, app_settings
from sensorthings.versions.v1_1.backends import get_backend_adapter

sensorthings_service = SensorThingsService(
    protocol=STA,
    settings=app_settings,
    get_backend_adapter=get_backend_adapter
)
