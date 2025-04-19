from sensorthings.components.things.engine import ThingBaseEngine
from sensorthings.components.things.schemas import ThingPostBody, ThingPatchBody
from .utils import SensorThingsUtils
from ..data import things


class ThingEngine(ThingBaseEngine, SensorThingsUtils):
    def get_things(
            self,
            thing_ids: list[int] = None,
            location_ids: list[int] = None,
            pagination: dict = None,
            ordering: dict = None,
            filters: dict = None,
            expanded: bool = False,
            get_count: bool = False
    ) -> (list[int, dict], int):

        response = things
        response = self.apply_filters(response, filters)
        response = self.apply_order(response, ordering)

        if get_count:
            count = len(response)
        else:
            count = None

        if pagination is not None:
            response = self.apply_pagination(response, pagination)

        return response, count

    def create_thing(
            self,
            thing: ThingPostBody
    ) -> int:

        return 3

    def update_thing(
            self,
            thing_id: int,
            thing: ThingPatchBody
    ) -> None:

        return None

    def delete_thing(
            self,
            thing_id: int
    ) -> None:

        return None
