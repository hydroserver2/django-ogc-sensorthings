from .base import BaseHandler
from sensorthings.v1_1 import iot


class ObservedPropertyHandler(BaseHandler):
    primitive_properties: list[str] = ["id", "name", "definition", "description"]
    complex_properties: list[str] = ["properties"]
    related_entities: list[str] = []
    related_collections: list[str] = [iot.DATASTREAMS]
