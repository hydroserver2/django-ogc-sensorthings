from django.apps import AppConfig


class DataArrayConfig(AppConfig):
    name = "sensorthings.versions.v1_1.extensions.dataarray"
    label = "sensorthings_v1_1_data_array_ext"
    verbose_name = "SensorThings v1.1: Data Array"

    def ready(self):
        from sensorthings.versions.v1_1.views import observation_router_definition
        from sensorthings.versions.v1_1 import service as service_module
        from sensorthings.versions.v1_1.backends.base import BASE_CONFORMANCE_URI, conformance_registry
        from sensorthings.versions.v1_1.extensions.dataarray.service import DataArrayServiceMixin
        from sensorthings.versions.v1_1.extensions.dataarray.views.observation import (
            get_observation_collection_operation,
            create_observations_operation,
        )

        data_array_service_class = type(
            "SensorThingsService",
            (DataArrayServiceMixin, service_module.SensorThingsService),
            {}
        )

        service_module.SensorThingsService = data_array_service_class
        service_module.sensorthings_service.__class__ = data_array_service_class

        observation_router_definition.operations["get_observation_collection"] = get_observation_collection_operation
        observation_router_definition.operations["create_observation_entities"] = create_observations_operation

        conformance_registry.extend([
            f"{BASE_CONFORMANCE_URI}/data-array",
        ])
