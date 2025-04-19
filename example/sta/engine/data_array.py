from typing import List
from sensorthings.extensions.dataarray.engine import DataArrayBaseEngine
from sensorthings.extensions.dataarray.schemas import ObservationDataArrayPostBody
from .utils import SensorThingsUtils


class DataArrayEngine(DataArrayBaseEngine, SensorThingsUtils):
    def create_observations(
            self,
            observations: List[ObservationDataArrayPostBody]
    ) -> list[int]:

        return []
