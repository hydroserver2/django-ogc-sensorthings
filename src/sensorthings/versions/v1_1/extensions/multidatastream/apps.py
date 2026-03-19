from django.apps import AppConfig


class MultiDatastreamConfig(AppConfig):
    name = "sensorthings.versions.v1_1.extensions.multidatastream"
    label = "sensorthings_v1_1_multidatastream_ext"
    verbose_name = "SensorThings v1.1: MultiDatastream"

    def ready(self):
        from sensorthings.types import EntityType
        from sensorthings.versions.v1_1 import STA

        STA.register_entity(
            EntityType(
                name="MultiDatastream",
                set_name="MultiDatastreams",
                primitive_properties=["id", "name", "description", "observationType", "phenomenonTime", "resultTime"],
                complex_properties=["properties", "unitOfMeasurements", "multiObservationDataTypes", "observedArea"],
                related_entity_type_names=["Thing", "Sensor", "ObservedProperty"],
                related_entity_type_set_names=["Observations"]
            )
        )

        STA.extend_entity("Thing", related_entity_type_set_names=["MultiDatastreams"])
        STA.extend_entity("Sensor", related_entity_type_set_names=["MultiDatastreams"])
        STA.extend_entity("ObservedProperty", related_entity_type_set_names=["MultiDatastreams"])
        STA.extend_entity("Observation", related_entity_type_names=["MultiDatastream"])
