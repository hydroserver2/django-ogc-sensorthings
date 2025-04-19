from sensorthings.components.historicallocations.engine import HistoricalLocationBaseEngine
from sensorthings.components.historicallocations.schemas import HistoricalLocationPostBody, HistoricalLocationPatchBody

from .utils import SensorThingsUtils
from ..data import historical_locations


class HistoricalLocationEngine(HistoricalLocationBaseEngine, SensorThingsUtils):
    def get_historical_locations(
            self,
            historical_location_ids: list[int] = None,
            thing_ids: list[int] = None,
            location_ids: list[int] = None,
            pagination: dict = None,
            ordering: dict = None,
            filters: dict = None,
            expanded: bool = False,
            get_count: bool = False
    ) -> (list[int, dict], int):

        response = historical_locations
        response = self.apply_filters(response, filters)
        response = self.apply_order(response, ordering)

        if get_count:
            count = len(response)
        else:
            count = None

        if pagination is not None:
            response = self.apply_pagination(response, pagination)

        return response, count

    def create_historical_location(
            self,
            historical_location: HistoricalLocationPostBody,
    ) -> int:

        return 1

    def update_historical_location(
            self,
            historical_location_id: int,
            historical_location: HistoricalLocationPatchBody
    ) -> None:

        return None

    def delete_historical_location(
            self,
            historical_location_id: int
    ) -> None:

        return None
