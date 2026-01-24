from ninja import NinjaAPI
from django.urls import path


api = NinjaAPI(
    title="SensorThings API",
    version="v1.0",
    urls_namespace="sensorthings_v1_0",
)
"""The main Django Ninja API instance for SensorThings version 1.0."""


urlpatterns = [path(f"v1.0/", api.urls)]  # TODO
