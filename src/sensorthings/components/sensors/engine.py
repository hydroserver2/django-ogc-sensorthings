from abc import ABCMeta, abstractmethod
from typing import List, Dict
from .schemas import SensorPostBody, SensorPatchBody
from sensorthings import settings


id_type = settings.ST_API_ID_TYPE


class SensorBaseEngine(metaclass=ABCMeta):
    """
    Abstract base class for handling Sensors.

    This class defines the required methods for managing sensors. These methods must be implemented
    to allow the SensorThings API to interface with an underlying database.
    """

    @abstractmethod
    def get_sensors(
            self,
            sensor_ids: List[id_type] = None,
            pagination: dict = None,
            ordering: dict = None,
            filters: dict = None,
            expanded: bool = False
    ) -> (Dict[id_type, dict], int):
        """
        Retrieve sensors based on provided parameters.

        Parameters
        ----------
        sensor_ids : List[id_type], optional
            List of sensor IDs to filter the results.
        pagination : dict, optional
            Pagination information to limit the number of results.
        ordering : dict, optional
            Ordering information to sort the results.
        filters : dict, optional
            Additional filters to apply to the query.
        expanded : bool, optional
            Whether to include expanded information in the results.

        Returns
        -------
        Dict[id_type, dict]
            A dictionary of sensors, keyed by their IDs.
        int
            The total number of sensors matching the query.
        """

        pass

    @abstractmethod
    def create_sensor(
            self,
            sensor: SensorPostBody
    ) -> id_type:
        """
        Create a new sensor.

        Parameters
        ----------
        sensor : SensorPostBody
            The sensor data to be created.

        Returns
        -------
        id_type
            The ID of the newly created sensor.
        """

        pass

    @abstractmethod
    def update_sensor(
            self,
            sensor_id: id_type,
            sensor: SensorPostBody
    ) -> None:
        """
        Update an existing sensor.

        Parameters
        ----------
        sensor_id : id_type
            The ID of the sensor to update.
        sensor : SensorPatchBody
            The updated sensor data.

        Returns
        -------
        None
        """

        pass

    @abstractmethod
    def delete_sensor(
            self,
            sensor_id: id_type
    ) -> None:
        """
        Delete a sensor.

        Parameters
        ----------
        sensor_id : id_type
            The ID of the sensor to delete.

        Returns
        -------
        None
        """

        pass
