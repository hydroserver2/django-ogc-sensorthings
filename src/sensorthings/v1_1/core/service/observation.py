from .base import BaseHandler
from sensorthings.v1_1 import iot


class ObservationHandler(BaseHandler):
    primitive_properties: list[str] = [
        "id",
        "phenomenonTime",
        "result",
        "resultTime",
        "validTime",
    ]
    complex_properties: list[str] = ["resultQuality", "parameters"]
    related_entities: list[str] = [iot.DATASTREAM, iot.FEATURE_OF_INTEREST]
    related_collections: list[str] = []
