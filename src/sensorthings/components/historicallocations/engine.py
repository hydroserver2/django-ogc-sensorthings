from abc import ABCMeta, abstractmethod
from typing import List, Dict
from .schemas import HistoricalLocationPostBody, HistoricalLocationPatchBody
from sensorthings import settings


id_type = settings.ST_API_ID_TYPE


class HistoricalLocationBaseEngine(metaclass=ABCMeta):
    """
    Abstract base class for handling Historical Locations.

    This class defines the required methods for managing historical locations. These methods must be implemented
    to allow the SensorThings API to interface with an underlying database.
    """

    @abstractmethod
    def get_historical_locations(
            self,
            historical_location_ids: List[id_type] = None,
            thing_ids: List[id_type] = None,
            location_ids: List[id_type] = None,
            pagination: dict = None,
            ordering: dict = None,
            filters: dict = None,
            expanded: bool = False
    ) -> (Dict[id_type, dict], int):
        """
        Retrieve historical locations based on provided parameters.

        Parameters
        ----------
        historical_location_ids : List[id_type], optional
            List of historical location IDs to filter the results.
        thing_ids : List[id_type], optional
            List of thing IDs to filter the results.
        location_ids : List[id_type], optional
            List of location IDs to filter the results.
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
            A dictionary of historical locations, keyed by their IDs.
        int
            The total number of historical locations matching the query.
        """

        pass

    @abstractmethod
    def create_historical_location(
            self,
            historical_location: HistoricalLocationPostBody,
    ) -> id_type:
        """
        Create a new historical location.

        Parameters
        ----------
        historical_location : HistoricalLocationPostBody
            The historical location data to be created.

        Returns
        -------
        id_type
            The ID of the newly created historical location.
        """

        pass

    @abstractmethod
    def update_historical_location(
            self,
            historical_location_id: id_type,
            historical_location: HistoricalLocationPatchBody,
    ) -> None:
        """
        Update an existing historical location.

        Parameters
        ----------
        historical_location_id : id_type
            The ID of the historical location to update.
        historical_location : HistoricalLocationPatchBody
            The updated historical location data.

        Returns
        -------
        None
        """

        pass

    @abstractmethod
    def delete_historical_location(
            self,
            historical_location_id: id_type
    ) -> None:
        """
        Delete a historical location.

        Parameters
        ----------
        historical_location_id : id_type
            The ID of the historical location to delete.

        Returns
        -------
        None
        """

        pass
