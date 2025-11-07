from .base import BaseHandler
from sensorthings.v1_1 import iot


class HistoricalLocationHandler(BaseHandler):
    primitive_fields: list[str] = ["id", "time"]
    complex_fields: list[str] = []
    related_entities: list[str] = [iot.THING]
    related_collections: list[str] = [iot.LOCATIONS]
