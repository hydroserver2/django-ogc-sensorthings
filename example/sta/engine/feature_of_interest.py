from sensorthings.components.featuresofinterest.engine import FeatureOfInterestBaseEngine
from sensorthings.components.featuresofinterest.schemas import FeatureOfInterestPostBody, FeatureOfInterestPatchBody
from .utils import SensorThingsUtils
from ..data import features_of_interest


class FeatureOfInterestEngine(FeatureOfInterestBaseEngine, SensorThingsUtils):
    def get_features_of_interest(
            self,
            feature_of_interest_ids: list[int] = None,
            observation_ids: list[int] = None,
            pagination: dict = None,
            ordering: dict = None,
            filters: dict = None,
            expanded: bool = False,
            get_count: bool = False
    ) -> (list[int, dict], int):

        response = features_of_interest
        response = self.apply_filters(response, filters)
        response = self.apply_order(response, ordering)

        if get_count:
            count = len(response)
        else:
            count = None

        if pagination is not None:
            response = self.apply_pagination(response, pagination)

        return response, count

    def create_feature_of_interest(
            self,
            feature_of_interest: FeatureOfInterestPostBody,
    ) -> int:

        return 1

    def update_feature_of_interest(
            self,
            feature_of_interest_id: int,
            feature_of_interest: FeatureOfInterestPatchBody
    ) -> None:

        return None

    def delete_feature_of_interest(
            self,
            feature_of_interest_id: int
    ) -> None:

        return None
