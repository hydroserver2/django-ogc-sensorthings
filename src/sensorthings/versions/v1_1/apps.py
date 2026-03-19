from django.apps import AppConfig


class SensorThingsV11Config(AppConfig):
    name = "sensorthings.versions.v1_1"
    label = "sensorthings_v1_1"
    verbose_name = "SensorThings v1.1"

    def ready(self) -> None:
        from sensorthings.types import EntityType
        from sensorthings.versions.v1_1 import STA

        STA.register_entity(
            EntityType(
                name="Thing",
                set_name="Things",
                primitive_properties=["id", "name", "description"],
                complex_properties=["properties"],
                related_entity_type_names=[],
                related_entity_type_set_names=["Locations", "HistoricalLocations", "Datastreams"]
            )
        )

        STA.register_entity(
            EntityType(
                name="Location",
                set_name="Locations",
                primitive_properties=["id", "name", "description", "encodingType"],
                complex_properties=["location", "properties"],
                related_entity_type_names=[],
                related_entity_type_set_names=["Things", "HistoricalLocations"]
            )
        )

        STA.register_entity(
            EntityType(
                name="HistoricalLocation",
                set_name="HistoricalLocations",
                primitive_properties=["id", "time"],
                complex_properties=[],
                related_entity_type_names=["Thing"],
                related_entity_type_set_names=["Locations"]
            )
        )

        STA.register_entity(
            EntityType(
                name="Datastream",
                set_name="Datastreams",
                primitive_properties=["id", "name", "description", "observationType", "phenomenonTime", "resultTime"],
                complex_properties=["properties", "unitOfMeasurement", "observedArea"],
                related_entity_type_names=["Thing", "Sensor", "ObservedProperty"],
                related_entity_type_set_names=["Observations"]
            )
        )

        STA.register_entity(
            EntityType(
                name="ObservedProperty",
                set_name="ObservedProperties",
                primitive_properties=["id", "name", "definition", "description"],
                complex_properties=["properties"],
                related_entity_type_names=[],
                related_entity_type_set_names=["Datastreams"]
            )
        )

        STA.register_entity(
            EntityType(
                name="Sensor",
                set_name="Sensors",
                primitive_properties=["id", "name", "description", "encodingType"],
                complex_properties=["metadata", "properties"],
                related_entity_type_names=[],
                related_entity_type_set_names=["Datastreams"]
            )
        )

        STA.register_entity(
            EntityType(
                name="Observation",
                set_name="Observations",
                primitive_properties=["id", "phenomenonTime", "result", "resultTime", "validTime"],
                complex_properties=["resultQuality", "parameters"],
                related_entity_type_names=["Datastream", "FeatureOfInterest"],
                related_entity_type_set_names=[]
            )
        )

        STA.register_entity(
            EntityType(
                name="FeatureOfInterest",
                set_name="FeaturesOfInterest",
                primitive_properties=["id", "name", "description", "encodingType"],
                complex_properties=["feature", "properties"],
                related_entity_type_names=[],
                related_entity_type_set_names=["Observations"]
            )
        )

        from sensorthings.versions.v1_1.schemas import (
            ThingResponse, LocationResponse, HistoricalLocationResponse,
            SensorResponse, ObservedPropertyResponse, FeatureOfInterestResponse,
            DatastreamResponse, ObservationResponse,
            ThingPostBody, LocationPostBody, HistoricalLocationPostBody,
            SensorPostBody, ObservedPropertyPostBody, FeatureOfInterestPostBody,
            DatastreamPostBody, ObservationPostBody,
            ThingCollectionResponse, LocationCollectionResponse,
            HistoricalLocationCollectionResponse, SensorCollectionResponse,
            ObservedPropertyCollectionResponse, FeatureOfInterestCollectionResponse,
            DatastreamCollectionResponse, ObservationCollectionResponse,
        )

        for model in [
            ThingResponse, LocationResponse, HistoricalLocationResponse,
            SensorResponse, ObservedPropertyResponse, FeatureOfInterestResponse,
            DatastreamResponse, ObservationResponse,
            ThingPostBody, LocationPostBody, HistoricalLocationPostBody,
            SensorPostBody, ObservedPropertyPostBody, FeatureOfInterestPostBody,
            DatastreamPostBody, ObservationPostBody,
            ThingCollectionResponse, LocationCollectionResponse,
            HistoricalLocationCollectionResponse, SensorCollectionResponse,
            ObservedPropertyCollectionResponse, FeatureOfInterestCollectionResponse,
            DatastreamCollectionResponse, ObservationCollectionResponse,
        ]:
            model.model_rebuild()
