from sensorthings.components.observedproperties.engine import ObservedPropertyBaseEngine
from sensorthings.components.observedproperties.schemas import ObservedPropertyPostBody, ObservedPropertyPatchBody
from .utils import SensorThingsUtils
from ..data import observed_properties


class ObservedPropertyEngine(ObservedPropertyBaseEngine, SensorThingsUtils):
    def get_observed_properties(
            self,
            observed_property_ids: list[int] = None,
            pagination: dict = None,
            ordering: dict = None,
            filters: dict = None,
            expanded: bool = False,
            get_count: bool = False
    ) -> (list[int, dict], int):

        response = observed_properties
        response = self.apply_filters(response, filters)
        response = self.apply_order(response, ordering)

        if get_count:
            count = len(response)
        else:
            count = None

        if pagination is not None:
            response = self.apply_pagination(response, pagination)

        return response, count

    def create_observed_property(
            self,
            observed_property: ObservedPropertyPostBody,
    ) -> int:

        return 1

    def update_observed_property(
            self,
            observed_property_id: int,
            observed_property: ObservedPropertyPatchBody
    ) -> None:

        return None

    def delete_observed_property(
            self,
            observed_property_id: int
    ) -> None:

        return None
