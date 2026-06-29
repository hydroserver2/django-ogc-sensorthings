from django.apps import AppConfig


class SensorThingsV11Config(AppConfig):
    name = "sensorthings.versions.v1_1"
    label = "sensorthings_v1_1"
    verbose_name = "SensorThings v1.1"

    def ready(self) -> None:
        from sensorthings.types import EntityType
        from sensorthings.versions.v1_1 import STA
        from sensorthings.versions.v1_1.backends.base import BASE_CONFORMANCE_URI, conformance_registry
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
                optional_related_entity_type_names=["FeatureOfInterest"],
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

        # TODO: Allow more granular customization of server conformance.
        # conformance_registry.extend([
        #     f"{BASE_CONFORMANCE_URI}/datamodel/entity-control-information/common-control-information",
        #     f"{BASE_CONFORMANCE_URI}/datamodel/thing/properties",
        #     f"{BASE_CONFORMANCE_URI}/datamodel/thing/relations",
        #     f"{BASE_CONFORMANCE_URI}/datamodel/location/properties",
        #     f"{BASE_CONFORMANCE_URI}/datamodel/location/relations",
        #     f"{BASE_CONFORMANCE_URI}/datamodel/historical-location/properties",
        #     f"{BASE_CONFORMANCE_URI}/datamodel/historical-location/relations",
        #     f"{BASE_CONFORMANCE_URI}/datamodel/datastream/properties",
        #     f"{BASE_CONFORMANCE_URI}/datamodel/datastream/relations",
        #     f"{BASE_CONFORMANCE_URI}/datamodel/sensor/properties",
        #     f"{BASE_CONFORMANCE_URI}/datamodel/sensor/relations",
        #     f"{BASE_CONFORMANCE_URI}/datamodel/observed-property/properties",
        #     f"{BASE_CONFORMANCE_URI}/datamodel/observed-property/relations",
        #     f"{BASE_CONFORMANCE_URI}/datamodel/observation/properties",
        #     f"{BASE_CONFORMANCE_URI}/datamodel/observation/relations",
        #     f"{BASE_CONFORMANCE_URI}/datamodel/feature-of-interest/properties",
        #     f"{BASE_CONFORMANCE_URI}/datamodel/feature-of-interest/relations",
        #     f"{BASE_CONFORMANCE_URI}/resource-path/resource-path-to-entities",
        #     f"{BASE_CONFORMANCE_URI}/request-data/status-code",
        #     f"{BASE_CONFORMANCE_URI}/request-data/query-status-code",
        #     f"{BASE_CONFORMANCE_URI}/request-data/order",
        #     f"{BASE_CONFORMANCE_URI}/request-data/orderby",
        #     f"{BASE_CONFORMANCE_URI}/request-data/top",
        #     f"{BASE_CONFORMANCE_URI}/request-data/skip",
        #     f"{BASE_CONFORMANCE_URI}/request-data/count",
        #     f"{BASE_CONFORMANCE_URI}/request-data/filter",
        #     f"{BASE_CONFORMANCE_URI}/request-data/built-in-filter-operations",
        #     f"{BASE_CONFORMANCE_URI}/request-data/built-in-query-functions",
        #     f"{BASE_CONFORMANCE_URI}/request-data/expand",
        #     f"{BASE_CONFORMANCE_URI}/request-data/select",
        #     f"{BASE_CONFORMANCE_URI}/request-data/pagination",
        #     f"{BASE_CONFORMANCE_URI}/create-update-delete/create-entity",
        #     f"{BASE_CONFORMANCE_URI}/create-update-delete/link-to-existing-entities",
        #     f"{BASE_CONFORMANCE_URI}/create-update-delete/deep-insert",
        #     f"{BASE_CONFORMANCE_URI}/create-update-delete/deep-insert-status-code",
        #     f"{BASE_CONFORMANCE_URI}/create-update-delete/update-entity",
        #     f"{BASE_CONFORMANCE_URI}/create-update-delete/delete-entity",
        #     f"{BASE_CONFORMANCE_URI}/create-update-delete/historical-location-auto-creation",
        #     f"{BASE_CONFORMANCE_URI}/create-update-delete/historical-location-manual-creation",
        # ])

        conformance_registry.extend([
            f"{BASE_CONFORMANCE_URI}/datamodel",
            f"{BASE_CONFORMANCE_URI}/resource-path",
            f"{BASE_CONFORMANCE_URI}/request-data",
            f"{BASE_CONFORMANCE_URI}/create-update-delete",
        ])

        import sensorthings.versions.v1_1.schemas  # noqa: F401 — triggers centralized schema build
