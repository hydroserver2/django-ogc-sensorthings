from .base import BaseHandler
from sensorthings.v1_1 import iot


class ObservedPropertyHandler(BaseHandler):
    primitive_fields: list[str] = ["id", "name", "definition", "description"]
    complex_fields: list[str] = ["properties"]
    related_entities: list[str] = []
    related_collections: list[str] = [iot.DATASTREAMS]
