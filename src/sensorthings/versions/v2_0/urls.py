from ninja import NinjaAPI
from django.urls import path


api = NinjaAPI(
    title="SensorThings API",
    version="v2.0",
    urls_namespace="sensorthings_v2_0",
)
"""The main Django Ninja API instance for SensorThings version 2.0."""


urlpatterns = [path(f"v2.0/", api.urls)]  # TODO
