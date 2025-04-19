from abc import ABCMeta, abstractmethod
from typing import List, Dict
from .schemas import FeatureOfInterestPostBody, FeatureOfInterestPatchBody
from sensorthings import settings


id_type = settings.ST_API_ID_TYPE


class FeatureOfInterestBaseEngine(metaclass=ABCMeta):
    """
    Abstract base class for handling Features of Interest.

    This class defines the required methods for managing features of interest. These methods must be implemented
    to allow the SensorThings API to interface with an underlying database.
    """

    @abstractmethod
    def get_features_of_interest(
            self,
            feature_of_interest_ids: List[id_type] = None,
            observation_ids: List[id_type] = None,
            pagination: dict = None,
            ordering: dict = None,
            filters: dict = None,
            expanded: bool = False
    ) -> (Dict[id_type, dict], int):
        """
        Retrieve features of interest based on the given criteria.

        Parameters
        ----------
        feature_of_interest_ids : List[id_type], optional
            List of feature of interest IDs to filter by.
        observation_ids : List[id_type], optional
            List of observation IDs to filter by.
        pagination : dict, optional
            Pagination options.
        ordering : dict, optional
            Ordering options.
        filters : dict, optional
            Additional filtering options.
        expanded : bool, optional
            Whether to include expanded related entities.

        Returns
        -------
        tuple
            A tuple containing a dictionary of features of interest and the total count.
        """

        pass

    @abstractmethod
    def create_feature_of_interest(
            self,
            feature_of_interest: FeatureOfInterestPostBody
    ) -> id_type:
        """
        Create a new feature of interest.

        Parameters
        ----------
        feature_of_interest : FeatureOfInterestPostBody
            The feature of interest object to create.

        Returns
        -------
        id_type
            The ID of the newly created feature of interest.
        """

        pass

    @abstractmethod
    def update_feature_of_interest(
            self,
            feature_of_interest_id: id_type,
            feature_of_interest: FeatureOfInterestPatchBody
    ) -> None:
        """
        Update an existing feature of interest.

        Parameters
        ----------
        feature_of_interest_id : id_type
            The ID of the feature of interest to update.
        feature_of_interest : FeatureOfInterestPatchBody
            The updated feature of interest object.

        Returns
        -------
        None
        """

        pass

    @abstractmethod
    def delete_feature_of_interest(
            self,
            feature_of_interest_id: id_type
    ) -> None:
        """
        Delete an existing feature of interest.

        Parameters
        ----------
        feature_of_interest_id : id_type
            The ID of the feature of interest to delete.

        Returns
        -------
        None
        """

        pass
