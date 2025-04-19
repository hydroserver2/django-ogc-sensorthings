from .datastreams.schemas import *
from .featuresofinterest.schemas import *
from .historicallocations.schemas import *
from .locations.schemas import *
from .observations.schemas import *
from .observedproperties.schemas import *
from .root.schemas import *
from .sensors.schemas import *
from .things.schemas import *


DatastreamRelations.model_rebuild()
FeatureOfInterestRelations.model_rebuild()
HistoricalLocationRelations.model_rebuild()
LocationRelations.model_rebuild()
ObservationRelations.model_rebuild()
ObservedPropertyRelations.model_rebuild()
SensorRelations.model_rebuild()
ThingRelations.model_rebuild()
