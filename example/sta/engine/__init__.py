from sensorthings import SensorThingsBaseEngine
from .datastream import DatastreamEngine
from .feature_of_interest import FeatureOfInterestEngine
from .historical_location import HistoricalLocationEngine
from .location import LocationEngine
from .observation import ObservationEngine
from .observed_property import ObservedPropertyEngine
from .quality_control import QualityControlEngine
from .sensor import SensorEngine
from .thing import ThingEngine
from .data_array import DataArrayEngine


class TestSensorThingsEngine(
    DatastreamEngine,
    FeatureOfInterestEngine,
    HistoricalLocationEngine,
    LocationEngine,
    ObservationEngine,
    ObservedPropertyEngine,
    SensorEngine,
    ThingEngine,
    SensorThingsBaseEngine
):
    pass


class TestDataArraySensorThingsEngine(
    DatastreamEngine,
    FeatureOfInterestEngine,
    HistoricalLocationEngine,
    LocationEngine,
    ObservationEngine,
    ObservedPropertyEngine,
    SensorEngine,
    ThingEngine,
    SensorThingsBaseEngine,
    DataArrayEngine
):
    pass


class TestQualityControlSensorThingsEngine(
    DatastreamEngine,
    FeatureOfInterestEngine,
    HistoricalLocationEngine,
    LocationEngine,
    ObservationEngine,
    ObservedPropertyEngine,
    SensorEngine,
    ThingEngine,
    SensorThingsBaseEngine,
    QualityControlEngine
):
    pass
