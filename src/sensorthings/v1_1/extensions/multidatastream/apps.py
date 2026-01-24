from django.apps import AppConfig


class MultiDatastreamConfig(AppConfig):
    name = "sensorthings.v1_1.extensions.multidatastream"
    verbose_name = "SensorThings v1.1: MultiDatastream"

    def ready(self):
        from sensorthings.v1_1.protocol.entity import EntityType
        from sensorthings.v1_1.protocol.core import STA

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
