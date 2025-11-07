from .base import BaseHandler
from sensorthings.v1_1 import iot


class SensorHandler(BaseHandler):
    primitive_fields: list[str] = ["id", "name", "description", "encodingType"]
    complex_fields: list[str] = ["metadata", "properties"]
    related_entities: list[str] = []
    related_collections: list[str] = [iot.DATASTREAMS]
