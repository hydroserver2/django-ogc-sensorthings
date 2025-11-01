from .root import ServiceRootSchema
from .query import EntityQuery, CollectionQuery
from .thing import ThingResponse, ThingCollectionResponse, ThingPostBody, ThingPatchBody
from .location import (
    LocationResponse,
    LocationCollectionResponse,
    LocationPostBody,
    LocationPatchBody,
)
from .historical_location import (
    HistoricalLocationResponse,
    HistoricalLocationCollectionResponse,
    HistoricalLocationPostBody,
    HistoricalLocationPatchBody,
)
from .datastream import (
    DatastreamResponse,
    DatastreamCollectionResponse,
    DatastreamPostBody,
    DatastreamPatchBody,
)
from .sensor import (
    SensorResponse,
    SensorCollectionResponse,
    SensorPostBody,
    SensorPatchBody,
)
from .observed_property import (
    ObservedPropertyResponse,
    ObservedPropertyCollectionResponse,
    ObservedPropertyPostBody,
    ObservedPropertyPatchBody,
)
from .observation import (
    ObservationResponse,
    ObservationCollectionResponse,
    ObservationPostBody,
    ObservationPatchBody,
)
from .feature_of_interest import (
    FeatureOfInterestResponse,
    FeatureOfInterestCollectionResponse,
    FeatureOfInterestPostBody,
    FeatureOfInterestPatchBody,
)
from .unit_of_measurement import UnitOfMeasurement


for model in [
    ThingCollectionResponse,
    ThingResponse,
    ThingPostBody,
    LocationCollectionResponse,
    LocationResponse,
    LocationPostBody,
    HistoricalLocationCollectionResponse,
    HistoricalLocationResponse,
    HistoricalLocationPostBody,
    DatastreamCollectionResponse,
    DatastreamResponse,
    DatastreamPostBody,
    SensorCollectionResponse,
    SensorResponse,
    SensorPostBody,
    ObservedPropertyCollectionResponse,
    ObservedPropertyResponse,
    ObservedPropertyPostBody,
    ObservationCollectionResponse,
    ObservationResponse,
    ObservationPostBody,
    FeatureOfInterestCollectionResponse,
    FeatureOfInterestResponse,
    FeatureOfInterestPostBody,
]:
    model.model_rebuild()
