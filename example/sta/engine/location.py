from sensorthings.components.locations.engine import LocationBaseEngine
from sensorthings.components.locations.schemas import LocationPostBody, LocationPatchBody
from .utils import SensorThingsUtils
from ..data import locations


class LocationEngine(LocationBaseEngine, SensorThingsUtils):
    def get_locations(
            self,
            location_ids: list[int] = None,
            thing_ids: list[int] = None,
            historical_location_ids: list[int] = None,
            pagination: dict = None,
            ordering: dict = None,
            filters: dict = None,
            expanded: bool = False,
            get_count: bool = False
    ) -> (list[int, dict], int):

        response = locations
        response = self.apply_filters(response, filters)
        response = self.apply_order(response, ordering)

        if get_count:
            count = len(response)
        else:
            count = None

        if pagination is not None:
            response = self.apply_pagination(response, pagination)

        return response, count

    def create_location(
            self,
            location: LocationPostBody,
    ) -> int:

        return 1

    def update_location(
            self,
            location_id: int,
            location: LocationPatchBody
    ) -> None:

        return None

    def delete_location(
            self,
            location_id: int
    ) -> None:

        return None
