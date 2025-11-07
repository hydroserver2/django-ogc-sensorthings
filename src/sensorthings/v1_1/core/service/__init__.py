from .thing import ThingHandler
from .location import LocationHandler
from .historical_location import HistoricalLocationHandler
from .sensor import SensorHandler
from .observed_property import ObservedPropertyHandler
from .datastream import DatastreamHandler
from .observation import ObservationHandler
from .feature_of_interest import FeatureOfInterestHandler


class SensorThingsService:
    """Core SensorThings service layer."""

    def __init__(self):
        self.things = ThingHandler(service=self)
        self.locations = LocationHandler(service=self)
        self.historical_locations = HistoricalLocationHandler(service=self)
        self.sensors = SensorHandler(service=self)
        self.observed_properties = ObservedPropertyHandler(service=self)
        self.datastreams = DatastreamHandler(service=self)
        self.observations = ObservationHandler(service=self)
        self.features_of_interest = FeatureOfInterestHandler(service=self)


sensorthings_service = SensorThingsService()
