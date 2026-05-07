from django.apps import AppConfig


class MultiDatastreamConfig(AppConfig):
    name = "sensorthings.versions.v1_1.extensions.multidatastream"
    label = "sensorthings_v1_1_multidatastream_ext"
    verbose_name = "SensorThings v1.1: MultiDatastream"

    def ready(self):
        from django.core.exceptions import ImproperlyConfigured
        from sensorthings.types import EntityType
        from sensorthings.versions.v1_1 import STA
        from sensorthings.versions.v1_1.backends import get_backend_adapter
        from sensorthings.versions.v1_1.backends.base import BASE_CONFORMANCE_URI, conformance_registry
        from sensorthings.versions.v1_1.extensions.multidatastream.backends import BaseMultiDatastreamAdapterMixin
        from sensorthings.versions.v1_1.schemas import schema_factory
        from sensorthings.versions.v1_1.extensions.multidatastream.schemas.multi_datastream import MultiDatastreamFields

        STA.register_entity(
            EntityType(
                name="MultiDatastream",
                set_name="MultiDatastreams",
                primitive_properties=["id", "name", "description", "observationType", "phenomenonTime", "resultTime"],
                complex_properties=["properties", "unitOfMeasurements", "multiObservationDataTypes", "observedArea"],
                related_entity_type_names=["Thing", "Sensor", "ObservedProperty"],
                related_entity_type_set_names=["Observations"],
                optional_properties=["properties", "observedArea", "phenomenonTime", "resultTime"],
            )
        )

        STA.extend_entity("Thing", related_entity_type_set_names=["MultiDatastreams"])
        STA.extend_entity("Sensor", related_entity_type_set_names=["MultiDatastreams"])
        STA.extend_entity("ObservedProperty", related_entity_type_set_names=["MultiDatastreams"])
        STA.extend_entity("Observation", related_entity_type_names=["MultiDatastream"])

        adapter = get_backend_adapter()
        if not isinstance(adapter, BaseMultiDatastreamAdapterMixin):
            raise ImproperlyConfigured(
                f"The MultiDatastream extension requires the configured backend adapter "
                f"({adapter.__class__.__name__}) to subclass BaseMultiDatastreamAdapterMixin. "
                f"See sensorthings.versions.v1_1.extensions.multidatastream.backends for details."
            )

        schema_factory.register("MultiDatastream", MultiDatastreamFields)
        multi_datastream_entity = STA.get_entity_type("MultiDatastream")

        multi_datastream_response = schema_factory.build_entity_response(multi_datastream_entity)
        multi_datastream_collection_response = schema_factory.build_collection_response(multi_datastream_entity)
        multi_datastream_post_body = schema_factory.build_post_body(multi_datastream_entity)
        multi_datastream_patch_body = schema_factory.build_patch_body(multi_datastream_entity)

        for _entity_type_name in ("Thing", "Sensor", "ObservedProperty"):
            _related_type = STA.get_entity_type(_entity_type_name)
            schema_factory.build_post_body(
                multi_datastream_entity,
                exclude={_entity_type_name},
                parent_name=_entity_type_name,
            )
            schema_factory.build_post_body(
                _related_type,
                exclude={"MultiDatastream"},
                parent_name="MultiDatastream",
            )

        _ext_types = schema_factory.all_schemas()
        for _schema in (
            multi_datastream_response,
            multi_datastream_collection_response,
            multi_datastream_post_body,
            multi_datastream_patch_body,
        ):
            _schema.model_rebuild(_types_namespace=_ext_types)

        conformance_registry.extend([
            f"{BASE_CONFORMANCE_URI}/multi-datastream",
        ])
