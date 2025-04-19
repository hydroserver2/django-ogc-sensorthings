from abc import ABCMeta, abstractmethod
from typing import List, Dict
from .schemas import ObservedPropertyPostBody, ObservedPropertyPatchBody
from sensorthings import settings


id_type = settings.ST_API_ID_TYPE


class ObservedPropertyBaseEngine(metaclass=ABCMeta):
    """
    Abstract base class for handling Observed Properties.

    This class defines the required methods for managing observed properties. These methods must be implemented
    to allow the SensorThings API to interface with an underlying database.
    """

    @abstractmethod
    def get_observed_properties(
            self,
            observed_property_ids: List[id_type] = None,
            pagination: dict = None,
            ordering: dict = None,
            filters: dict = None,
            expanded: bool = False
    ) -> (Dict[id_type, dict], int):
        """
        Retrieve observed properties based on provided parameters.

        Parameters
        ----------
        observed_property_ids : List[id_type], optional
            List of observed property IDs to filter the results.
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
            A dictionary of observed properties, keyed by their IDs.
        int
            The total number of observed properties matching the query.
        """

        pass

    @abstractmethod
    def create_observed_property(
            self,
            observed_property: ObservedPropertyPostBody
    ) -> id_type:
        """
        Create a new observed property.

        Parameters
        ----------
        observed_property : ObservedPropertyPostBody
            The observed property data to be created.

        Returns
        -------
        id_type
            The ID of the newly created observed property.
        """

        pass

    @abstractmethod
    def update_observed_property(
            self,
            observed_property_id: id_type,
            observed_property: ObservedPropertyPatchBody
    ) -> None:
        """
        Update an existing observed property.

        Parameters
        ----------
        observed_property_id : id_type
            The ID of the observed property to update.
        observed_property : ObservedPropertyPatchBody
            The updated observed property data.

        Returns
        -------
        None
        """

        pass

    @abstractmethod
    def delete_observed_property(
            self,
            observed_property_id: id_type
    ) -> None:
        """
        Delete an observed property.

        Parameters
        ----------
        observed_property_id : id_type
            The ID of the observed property to delete.

        Returns
        -------
        None
        """

        pass
