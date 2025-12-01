from .base import BaseHandler
from sensorthings.v1_1 import iot


class FeatureOfInterestHandler(BaseHandler):
    primitive_properties: list[str] = ["id", "name", "description", "encodingType"]
    complex_properties: list[str] = ["feature", "properties"]
    related_entities: list[str] = []
    related_collections: list[str] = [iot.OBSERVATIONS]
