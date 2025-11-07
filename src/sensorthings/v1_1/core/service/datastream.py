from .base import BaseHandler
from sensorthings.v1_1 import iot


class DatastreamHandler(BaseHandler):
    primitive_fields = ["id", "name", "description", "observationType", "phenomenonTime", "resultTime"]
    complex_fields = ["properties", "unitOfMeasurement", "observedArea"]
    related_entities = [iot.THING, iot.SENSOR, iot.OBSERVED_PROPERTY]
    related_collections = [iot.OBSERVATIONS]
