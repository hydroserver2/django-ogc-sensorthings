from django.apps import AppConfig


class DataArrayConfig(AppConfig):
    name = "sensorthings.v1_1.extensions.dataarray"
    verbose_name = "SensorThings v1.1: Data Array"

    def ready(self):
        from sensorthings.v1_1.protocol.entity import EntityType
        from sensorthings.v1_1.protocol.core import STA
