from ninja import NinjaAPI
from ninja.renderers import JSONRenderer
from django.urls import path
from django.apps import apps
from sensorthings.versions.v1_1 import STA
from sensorthings.versions.v1_1.conf import app_settings
from sensorthings.versions.v1_1.views import (
    root_router_definition,
    thing_router_definition,
    location_router_definition,
    historical_location_router_definition,
    datastream_router_definition,
    sensor_router_definition,
    observed_property_router_definition,
    observation_router_definition,
    feature_of_interest_router_definition,
    resolver_router_definition,
    batch_router_definition
)
from sensorthings.versions.v1_1.schemas import (
    ThingResponse,
    ThingCollectionResponse,
    ThingPostBody,
    LocationResponse,
    LocationCollectionResponse,
    LocationPostBody,
    HistoricalLocationResponse,
    HistoricalLocationCollectionResponse,
    HistoricalLocationPostBody,
    DatastreamResponse,
    DatastreamCollectionResponse,
    DatastreamPostBody,
    SensorResponse,
    SensorCollectionResponse,
    SensorPostBody,
    ObservedPropertyResponse,
    ObservedPropertyCollectionResponse,
    ObservedPropertyPostBody,
    ObservationResponse,
    ObservationCollectionResponse,
    ObservationPostBody,
    FeatureOfInterestResponse,
    FeatureOfInterestCollectionResponse,
    FeatureOfInterestPostBody,
)

if apps.is_installed("sensorthings.v1_1.extensions.multidatastream"):
    from sensorthings.versions.v1_1.extensions.multidatastream.views import (
        multi_datastream_router_definition
    )
    from sensorthings.versions.v1_1.extensions.multidatastream.schemas import (
        MultiDatastreamResponse,
        MultiDatastreamCollectionResponse,
        MultiDatastreamPostBody,
    )


api = NinjaAPI(
    title="SensorThings API",
    version=STA.VERSION,
    urls_namespace="sensorthings_v1_1",
    renderer=app_settings.RENDERER or JSONRenderer(),
)
"""The main Django Ninja API instance for SensorThings version 1.1."""

api.add_router("", root_router_definition.apply())

api.add_router("", thing_router_definition.apply())
api.add_router("", location_router_definition.apply())
api.add_router("", historical_location_router_definition.apply())
api.add_router("", datastream_router_definition.apply())

if apps.is_installed("sensorthings.v1_1.extensions.multidatastream"):
    api.add_router("", multi_datastream_router_definition.apply())

api.add_router("", sensor_router_definition.apply())
api.add_router("", observed_property_router_definition.apply())

api.add_router("", observation_router_definition.apply())

api.add_router("", feature_of_interest_router_definition.apply())

api.add_router("", resolver_router_definition.apply())
api.add_router("", batch_router_definition.apply())

urlpatterns = [path(f"{STA.VERSION}/", api.urls)]
