from .root import ServiceRootSchema
from .query import EntityQuery, CollectionQuery
from .thing import ThingResponse, ThingCollectionResponse, ThingPostBody, ThingPatchBody
from .location import LocationResponse, LocationCollectionResponse, LocationPostBody, LocationPatchBody
from .historical_location import (HistoricalLocationResponse, HistoricalLocationCollectionResponse,
                                  HistoricalLocationPostBody, HistoricalLocationPatchBody)
from .datastream import DatastreamResponse, DatastreamCollectionResponse, DatastreamPostBody, DatastreamPatchBody
from .sensor import SensorResponse, SensorCollectionResponse, SensorPostBody, SensorPatchBody
from .observed_property import (ObservedPropertyResponse, ObservedPropertyCollectionResponse, ObservedPropertyPostBody,
                                ObservedPropertyPatchBody)
from .observation import ObservationResponse, ObservationCollectionResponse, ObservationPostBody, ObservationPatchBody
from .feature_of_interest import (FeatureOfInterestResponse, FeatureOfInterestCollectionResponse,
                                  FeatureOfInterestPostBody, FeatureOfInterestPatchBody)
from .unit_of_measurement import UnitOfMeasurement


ThingCollectionResponse.model_rebuild()
ThingResponse.model_rebuild()
ThingPostBody.model_rebuild()

LocationCollectionResponse.model_rebuild()
LocationResponse.model_rebuild()
LocationPostBody.model_rebuild()

HistoricalLocationCollectionResponse.model_rebuild()
HistoricalLocationResponse.model_rebuild()
HistoricalLocationPostBody.model_rebuild()

DatastreamCollectionResponse.model_rebuild()
DatastreamResponse.model_rebuild()
DatastreamPostBody.model_rebuild()

SensorCollectionResponse.model_rebuild()
SensorResponse.model_rebuild()
SensorPostBody.model_rebuild()

ObservedPropertyCollectionResponse.model_rebuild()
ObservedPropertyResponse.model_rebuild()
ObservedPropertyPostBody.model_rebuild()

ObservationCollectionResponse.model_rebuild()
ObservationResponse.model_rebuild()
ObservationPostBody.model_rebuild()

FeatureOfInterestCollectionResponse.model_rebuild()
FeatureOfInterestResponse.model_rebuild()
FeatureOfInterestPostBody.model_rebuild()
