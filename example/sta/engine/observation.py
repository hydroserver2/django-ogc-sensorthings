from sensorthings.components.observations.engine import ObservationBaseEngine
from sensorthings.components.observations.schemas import ObservationPostBody, ObservationPatchBody
from .utils import SensorThingsUtils
from ..data import observations


class ObservationEngine(ObservationBaseEngine, SensorThingsUtils):
    def get_observations(
            self,
            observation_ids: list[int] = None,
            datastream_ids: list[int] = None,
            feature_of_interest_ids: list[int] = None,
            pagination: dict = None,
            ordering: dict = None,
            filters: dict = None,
            expanded: bool = False,
            get_count: bool = False
    ) -> (list[int, dict], int):

        response = observations
        response = self.apply_filters(response, filters)
        response = self.apply_order(response, ordering)

        if get_count:
            count = len(response)
        else:
            count = None

        if pagination is not None:
            response = self.apply_pagination(response, pagination)

        return response, count

    def create_observation(
            self,
            observation: ObservationPostBody,
    ) -> int:

        return 1

    def update_observation(
            self,
            observation_id: int,
            observation: ObservationPatchBody
    ) -> None:

        return None

    def delete_observation(
            self,
            observation_id: int
    ) -> None:

        return None
