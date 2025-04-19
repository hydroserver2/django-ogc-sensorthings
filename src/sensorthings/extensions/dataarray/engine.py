from abc import ABCMeta, abstractmethod
from typing import List, Union, Dict
from itertools import groupby
from sensorthings.schemas import EntityId
from sensorthings.components.observations.schemas import ObservationPostBody
from sensorthings.extensions.dataarray.schemas import ObservationDataArrayFields
from .schemas import ObservationDataArrayPostBody
from sensorthings import settings


id_type = settings.ST_API_ID_TYPE
id_qualifier = settings.ST_API_ID_QUALIFIER


class DataArrayBaseEngine(metaclass=ABCMeta):

    @abstractmethod
    def create_observations(
            self,
            observations: ObservationDataArrayPostBody,
    ) -> List[id_type]:
        """
        Create Observations using data array format.

        Parameters:
        - component (Type['BaseComponent']): The type of component.
        - observations ('ObservationDataArrayPostBody'): The entity body.

        Returns:
        - List[id_type]: The list of observation IDs.
        """

        pass

    @ staticmethod
    def convert_from_data_array(
            observations: List[ObservationDataArrayPostBody],
    ) -> Dict[id_type, List[ObservationPostBody]]:
        """
        Convert Observations data array to dict of Observations grouped by Datastream.

        Parameters:
        - observations ('ObservationDataArrayPostBody'): The entity body.

        Returns:
        - dict: The Observations grouped by Datastream.
        """

        return {
            data_array.datastream.id: [
                ObservationPostBody(
                    datastream=EntityId(id=data_array.datastream.id),
                    **{
                        (field if field != 'FeatureOfInterest/id' else 'feature_of_interest'):
                        (observation[i] if field != 'FeatureOfInterest/id' else EntityId(id=observation[i]))
                        for i, field in enumerate(data_array.components)
                    },
                ) for observation in data_array.data_array
            ] for data_array in observations
        }

    def convert_to_data_array(
            self,
            response: dict,
            select: Union[str, None] = None
    ) -> dict:
        """
        Convert Observations response to a data array.

        Parameters:
        - response (dict): The response dictionary.
        - select (Union[str, None]): Optional parameter to select specific fields.

        Returns:
        - dict: The converted data array response.
        """

        if select:
            selected_fields = [
                field[0] for field in ObservationDataArrayFields.model_fields.items()
                if field[1].alias in select.split(',')
            ]
            if 'id' in select.split(','):
                selected_fields = ['id'] + selected_fields
        else:
            selected_fields = [
                field for field in ObservationDataArrayFields.model_fields if field in ['phenomenon_time', 'result']
            ]

        response['value'] = [
            {
                'datastream_id': datastream_id,
                'datastream': f'{self.request.sensorthings_url}/'  # noqa
                              f'Datastreams({id_qualifier}{datastream_id}{id_qualifier})',
                'components': [
                    '@iot.id' if field == 'id' else ObservationDataArrayFields.model_fields[field].alias
                    for field in selected_fields
                ],
                'data_array': [
                    [  # TODO Validate Result Quality Fields
                        observation[field] for field in selected_fields
                    ] for observation in observations
                    # [
                    #     value for field, value in ObservationDataArrayFields(**observation).dict().items()
                    #     if field in selected_fields
                    # ] for observation in observations
                ]
            } for datastream_id, observations in groupby(response['value'], key=lambda x: x['datastream_id'])
        ]

        return response
