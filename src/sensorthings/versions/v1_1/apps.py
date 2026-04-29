from django.apps import AppConfig


class SensorThingsV11Config(AppConfig):
    name = "sensorthings.versions.v1_1"
    label = "sensorthings_v1_1"
    verbose_name = "SensorThings v1.1"

    def ready(self) -> None:
        from sensorthings.types import EntityType
        from sensorthings.versions.v1_1 import STA
        from sensorthings.versions.v1_1.dto import (
            ThingDTO, LocationDTO, HistoricalLocationDTO, SensorDTO,
            ObservedPropertyDTO, DatastreamDTO, ObservationDTO, FeatureOfInterestDTO,
        )

        STA.register_entity(
            EntityType(
                name="Thing",
                set_name="Things",
                primitive_properties=["id", "name", "description"],
                complex_properties=["properties"],
                related_entity_type_names=[],
                related_entity_type_set_names=["Locations", "HistoricalLocations", "Datastreams"],
                optional_properties=["properties"],
                dto_class=ThingDTO,
            )
        )

        STA.register_entity(
            EntityType(
                name="Location",
                set_name="Locations",
                primitive_properties=["id", "name", "description", "encodingType"],
                complex_properties=["location", "properties"],
                related_entity_type_names=[],
                related_entity_type_set_names=["Things", "HistoricalLocations"],
                optional_properties=["properties"],
                dto_class=LocationDTO,
            )
        )

        STA.register_entity(
            EntityType(
                name="HistoricalLocation",
                set_name="HistoricalLocations",
                primitive_properties=["id", "time"],
                complex_properties=[],
                related_entity_type_names=["Thing"],
                related_entity_type_set_names=["Locations"],
                dto_class=HistoricalLocationDTO,
            )
        )

        STA.register_entity(
            EntityType(
                name="Datastream",
                set_name="Datastreams",
                primitive_properties=["id", "name", "description", "observationType", "phenomenonTime", "resultTime"],
                complex_properties=["properties", "unitOfMeasurement", "observedArea"],
                related_entity_type_names=["Thing", "Sensor", "ObservedProperty"],
                related_entity_type_set_names=["Observations"],
                optional_properties=["properties", "observedArea", "phenomenonTime", "resultTime"],
                dto_class=DatastreamDTO,
            )
        )

        STA.register_entity(
            EntityType(
                name="ObservedProperty",
                set_name="ObservedProperties",
                primitive_properties=["id", "name", "definition", "description"],
                complex_properties=["properties"],
                related_entity_type_names=[],
                related_entity_type_set_names=["Datastreams"],
                optional_properties=["properties"],
                dto_class=ObservedPropertyDTO,
            )
        )

        STA.register_entity(
            EntityType(
                name="Sensor",
                set_name="Sensors",
                primitive_properties=["id", "name", "description", "encodingType"],
                complex_properties=["metadata", "properties"],
                related_entity_type_names=[],
                related_entity_type_set_names=["Datastreams"],
                optional_properties=["properties"],
                dto_class=SensorDTO,
            )
        )

        STA.register_entity(
            EntityType(
                name="Observation",
                set_name="Observations",
                primitive_properties=["id", "phenomenonTime", "result", "resultTime", "validTime"],
                complex_properties=["resultQuality", "parameters"],
                related_entity_type_names=["Datastream", "FeatureOfInterest"],
                related_entity_type_set_names=[],
                optional_properties=["resultQuality", "parameters", "validTime"],
                dto_class=ObservationDTO,
            )
        )

        STA.register_entity(
            EntityType(
                name="FeatureOfInterest",
                set_name="FeaturesOfInterest",
                primitive_properties=["id", "name", "description", "encodingType"],
                complex_properties=["feature", "properties"],
                related_entity_type_names=[],
                related_entity_type_set_names=["Observations"],
                optional_properties=["properties"],
                dto_class=FeatureOfInterestDTO,
            )
        )

        import sensorthings.versions.v1_1.schemas  # noqa: F401 — triggers centralized schema build
