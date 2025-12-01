from .base import BaseHandler
from sensorthings.v1_1 import iot


class SensorHandler(BaseHandler):
    primitive_properties: list[str] = ["id", "name", "description", "encodingType"]
    complex_properties: list[str] = ["metadata", "properties"]
    related_entities: list[str] = []
    related_collections: list[str] = [iot.DATASTREAMS]
