from ninja import NinjaAPI
from django.urls import path
from sensorthings.v1_1.core import iot
from sensorthings.v1_1.core.views import (
    root_router,
    thing_router,
    location_router,
    historical_location_router,
    datastream_router,
    sensor_router,
    observed_property_router,
    observation_router,
    feature_of_interest_router,
    resolver_router
)


api = NinjaAPI(
    title="SensorThings API",
    version=iot.VERSION,
    urls_namespace="sensorthings_v1_1",
)
"""The main Django Ninja API instance for SensorThings version 1.1."""

api.add_router("", root_router)

api.add_router("", thing_router)
api.add_router("", location_router)
api.add_router("", historical_location_router)
api.add_router("", datastream_router)
api.add_router("", sensor_router)
api.add_router("", observed_property_router)
api.add_router("", observation_router)
api.add_router("", feature_of_interest_router)

api.add_router("", resolver_router)

urlpatterns = [path("v1.1/", api.urls)]
