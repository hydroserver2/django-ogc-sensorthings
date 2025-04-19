from abc import ABCMeta, abstractmethod
from typing import List, Dict
from .schemas import ObservationPostBody, ObservationPatchBody
from sensorthings import settings


id_type = settings.ST_API_ID_TYPE


class ObservationBaseEngine(metaclass=ABCMeta):
    """
    Abstract base class for handling Observations.

    This class defines the required methods for managing observations. These methods must be implemented
    to allow the SensorThings API to interface with an underlying database.
    """

    @abstractmethod
    def get_observations(
            self,
            observation_ids: List[id_type] = None,
            datastream_ids: List[id_type] = None,
            feature_of_interest_ids: List[id_type] = None,
            pagination: dict = None,
            ordering: dict = None,
            filters: dict = None,
            expanded: bool = False
    ) -> (Dict[id_type, dict], int):
        """
        Retrieve observations based on provided parameters.

        Parameters
        ----------
        observation_ids : List[id_type], optional
            List of observation IDs to filter the results.
        datastream_ids : List[id_type], optional
            List of datastream IDs to filter the results.
        feature_of_interest_ids : List[id_type], optional
            List of feature of interest IDs to filter the results.
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
            A dictionary of observations, keyed by their IDs.
        int
            The total number of observations matching the query.
        """

        pass

    @abstractmethod
    def create_observation(
            self,
            observation: ObservationPostBody
    ) -> id_type:
        """
        Create a new observation.

        Parameters
        ----------
        observation : ObservationPostBody
            The observation data to be created.

        Returns
        -------
        id_type
            The ID of the newly created observation.
        """

        pass

    @abstractmethod
    def update_observation(
            self,
            observation_id: id_type,
            observation: ObservationPatchBody
    ) -> None:
        """
        Update an existing observation.

        Parameters
        ----------
        observation_id : id_type
            The ID of the observation to update.
        observation : ObservationPatchBody
            The updated observation data.

        Returns
        -------
        None
        """

        pass

    @abstractmethod
    def delete_observation(
            self,
            observation_id: id_type
    ) -> None:
        """
        Delete an observation.

        Parameters
        ----------
        observation_id : id_type
            The ID of the observation to delete.

        Returns
        -------
        None
        """

        pass
