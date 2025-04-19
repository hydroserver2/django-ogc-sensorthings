from abc import ABCMeta, abstractmethod
from typing import Optional
from datetime import datetime
from sensorthings import settings


id_type = settings.ST_API_ID_TYPE
id_qualifier = settings.ST_API_ID_QUALIFIER


class QualityControlBaseEngine(metaclass=ABCMeta):

    @abstractmethod
    def delete_observations(
            self,
            datastream_id: id_type,
            start_time: Optional[datetime] = None,
            end_time: Optional[datetime] = None
    ) -> None:
        """
        Delete multiple Observations from a Datastream.

        Parameters:
        - datastream_id: The ID of the Datastream Observations will be deleted from.
        - start_time (Optional[datetime]): The phenomenon time after which Observations will be deleted
        - end_time (Optional[datetime]): The phenomenon time before which Observations will be deleted.
        """

        pass
