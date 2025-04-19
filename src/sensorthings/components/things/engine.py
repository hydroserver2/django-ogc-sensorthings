from abc import ABCMeta, abstractmethod
from typing import List, Dict
from .schemas import ThingPostBody, ThingPatchBody
from sensorthings import settings


id_type = settings.ST_API_ID_TYPE


class ThingBaseEngine(metaclass=ABCMeta):
    """
    Abstract base class for handling Things.

    This class defines the required methods for managing things. These methods must be implemented
    to allow the SensorThings API to interface with an underlying database.
    """

    @abstractmethod
    def get_things(
            self,
            thing_ids: List[id_type] = None,
            location_ids: List[id_type] = None,
            pagination: dict = None,
            ordering: dict = None,
            filters: dict = None,
            expanded: bool = False
    ) -> (Dict[id_type, dict], int):
        """
        Retrieve things based on provided parameters.

        Parameters
        ----------
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
            A dictionary of things, keyed by their IDs.
        int
            The total number of things matching the query.
        """

        pass

    @abstractmethod
    def create_thing(
            self,
            thing: ThingPostBody
    ) -> id_type:
        """
        Create a new thing.

        Parameters
        ----------
        thing : ThingPostBody
            The thing data to be created.

        Returns
        -------
        id_type
            The ID of the newly created thing.
        """

        pass

    @abstractmethod
    def update_thing(
            self,
            thing_id: id_type,
            thing: ThingPatchBody
    ) -> None:
        """
        Update an existing thing.

        Parameters
        ----------
        thing_id : id_type
            The ID of the thing to update.
        thing : ThingPatchBody
            The updated thing data.

        Returns
        -------
        None
        """

        pass

    @abstractmethod
    def delete_thing(
            self,
            thing_id: id_type
    ) -> None:
        """
        Delete a thing.

        Parameters
        ----------
        thing_id : id_type
            The ID of the thing to delete.

        Returns
        -------
        None
        """

        pass
