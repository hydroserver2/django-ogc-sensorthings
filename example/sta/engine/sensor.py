from sensorthings.components.sensors.engine import SensorBaseEngine
from sensorthings.components.sensors.schemas import SensorPostBody, SensorPatchBody
from .utils import SensorThingsUtils
from ..data import sensors


class SensorEngine(SensorBaseEngine, SensorThingsUtils):
    def get_sensors(
            self,
            sensor_ids: list[int] = None,
            pagination: dict = None,
            ordering: dict = None,
            filters: dict = None,
            expanded: bool = False,
            get_count: bool = False
    ) -> (list[int, dict], int):

        response = sensors
        response = self.apply_filters(response, filters)
        response = self.apply_order(response, ordering)

        if get_count:
            count = len(response)
        else:
            count = None

        if pagination is not None:
            response = self.apply_pagination(response, pagination)

        return response, count

    def create_sensor(
            self,
            sensor: SensorPostBody
    ) -> int:

        return 1

    def update_sensor(
            self,
            sensor_id: int,
            sensor: SensorPatchBody
    ) -> None:

        return None

    def delete_sensor(
            self,
            sensor_id: int
    ) -> None:

        return None
