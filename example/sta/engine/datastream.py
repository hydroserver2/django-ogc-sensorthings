from sensorthings.components.datastreams.engine import DatastreamBaseEngine
from sensorthings.components.datastreams.schemas import DatastreamPostBody, DatastreamPatchBody
from .utils import SensorThingsUtils
from ..data import datastreams


class DatastreamEngine(DatastreamBaseEngine, SensorThingsUtils):
    def get_datastreams(
            self,
            datastream_ids: list[int] = None,
            observed_property_ids: list[int] = None,
            sensor_ids: list[int] = None,
            thing_ids: list[int] = None,
            pagination: dict = None,
            ordering: dict = None,
            filters: dict = None,
            expanded: bool = False,
            get_count: bool = False
    ) -> (list[int, dict], int):

        response = datastreams
        response = self.apply_filters(response, filters)
        response = self.apply_order(response, ordering)

        if get_count:
            count = len(response)
        else:
            count = None

        if pagination is not None:
            response = self.apply_pagination(response, pagination)

        return response, count

    def create_datastream(
            self,
            datastream: DatastreamPostBody,
    ) -> int:

        return 1

    def update_datastream(
            self,
            datastream_id: int,
            datastream: DatastreamPatchBody
    ) -> None:

        return None

    def delete_datastream(
            self,
            datastream_id: int
    ) -> None:

        return None
