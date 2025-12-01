from .base import BaseHandler
from sensorthings.v1_1 import iot


class ResourcePathHandler(BaseHandler):
    entity_name = iot.THINGS
    primitive_properties: list[str] = ["id", "name", "description"]
    complex_properties: list[str] = ["properties"]
    related_entities: list[str] = []
    related_collections: list[str] = [
        iot.LOCATIONS,
        iot.HISTORICAL_LOCATIONS,
        iot.DATASTREAMS,
    ]
