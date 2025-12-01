from .thing import ThingHandler
from .location import LocationHandler
from .historical_location import HistoricalLocationHandler
from .sensor import SensorHandler
from .observed_property import ObservedPropertyHandler
from .datastream import DatastreamHandler
from .observation import ObservationHandler
from .feature_of_interest import FeatureOfInterestHandler
from sensorthings.v1_1.conf import app_settings
from sensorthings.v1_1.core.adapters import DummyBackendAdapter


class SensorThingsService:
    """Core SensorThings service layer."""

    def __init__(self):
        self.backend = (
            app_settings.BACKEND_ADAPTER()
            if app_settings.BACKEND_ADAPTER
            else DummyBackendAdapter()
        )

        self.things = ThingHandler(service=self)
        self.locations = LocationHandler(service=self)
        self.historical_locations = HistoricalLocationHandler(service=self)
        self.sensors = SensorHandler(service=self)
        self.observed_properties = ObservedPropertyHandler(service=self)
        self.datastreams = DatastreamHandler(service=self)
        self.observations = ObservationHandler(service=self)
        self.features_of_interest = FeatureOfInterestHandler(service=self)

    def get_entity_handler(self, entity_name: str):
        """"""

        entity_handler_map = {
            "Things": self.things,
            "Thing": self.things,
            "Locations": self.locations,
            "Location": self.locations,
            "HistoricalLocations": self.historical_locations,
            "HistoricalLocation": self.historical_locations,
            "Datastreams": self.datastreams,
            "Datastream": self.datastreams,
            "Sensors": self.sensors,
            "Sensor": self.sensors,
            "ObservedProperties": self.observed_properties,
            "ObservedProperty": self.observed_properties,
            "Observations": self.observations,
            "Observation": self.observations,
            "FeaturesOfInterest": self.features_of_interest,
            "FeatureOfInterest": self.features_of_interest,
        }

        return entity_handler_map.get(entity_name)


sensorthings_service = SensorThingsService()
