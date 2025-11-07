from .base import BaseHandler
from sensorthings.v1_1 import iot


class ThingHandler(BaseHandler):
    primitive_fields: list[str] = ["id", "name", "description"]
    complex_fields: list[str] = ["properties"]
    related_entities: list[str] = []
    related_collections: list[str] = [iot.LOCATIONS, iot.HISTORICAL_LOCATIONS, iot.DATASTREAMS]
