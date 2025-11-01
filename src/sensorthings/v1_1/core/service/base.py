from .thing import ThingService
from .location import LocationService
from .historical_location import HistoricalLocationService
from .observed_property import ObservedPropertyService
from .sensor import SensorService
from .datastream import DatastreamService
from .feature_of_interest import FeatureOfInterestService


class SensorThingsService(
    ThingService,
    LocationService,
    HistoricalLocationService,
    ObservedPropertyService,
    SensorService,
    DatastreamService,
    FeatureOfInterestService,
):
    pass
