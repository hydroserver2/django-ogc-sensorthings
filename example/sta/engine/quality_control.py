from datetime import datetime
from typing import Optional
from sensorthings.extensions.qualitycontrol.engine import QualityControlBaseEngine, id_type
from .utils import SensorThingsUtils


class QualityControlEngine(QualityControlBaseEngine, SensorThingsUtils):
    def delete_observations(
            self,
            datastream_id: id_type,
            start_time: Optional[datetime] = None,
            end_time: Optional[datetime] = None
    ) -> None:
        return None
