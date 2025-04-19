import re
import pytz
from abc import ABCMeta
from typing import TYPE_CHECKING, List, Optional, Type, Dict, Callable, Tuple, ForwardRef
from uuid import UUID
from datetime import datetime
from dateutil.parser import isoparse
from django.http import HttpResponse
from ninja.errors import HttpError
from odata_query.grammar import ODataParser, ODataLexer
from odata_query.exceptions import ParsingException, TokenizingException
from sensorthings.components.things.engine import ThingBaseEngine
from sensorthings.components.locations.engine import LocationBaseEngine
from sensorthings.components.historicallocations.engine import HistoricalLocationBaseEngine
from sensorthings.components.datastreams.engine import DatastreamBaseEngine
from sensorthings.components.sensors.engine import SensorBaseEngine
from sensorthings.components.observedproperties.engine import ObservedPropertyBaseEngine
from sensorthings.components.featuresofinterest.engine import FeatureOfInterestBaseEngine
from sensorthings.components.observations.engine import ObservationBaseEngine
from sensorthings.schemas import ListQueryParams
from sensorthings.components import field_schemas
from sensorthings.components.datastreams.schemas import DatastreamPatchBody
from sensorthings import settings


if TYPE_CHECKING:
    from sensorthings.schemas import BaseComponent, BaseGetResponse, BasePostBody, BasePatchBody
    from sensorthings.http import SensorThingsHttpRequest


id_qualifier = settings.ST_API_ID_QUALIFIER
id_type = settings.ST_API_ID_TYPE


class SensorThingsBaseEngine(
    ThingBaseEngine,
    LocationBaseEngine,
    HistoricalLocationBaseEngine,
    DatastreamBaseEngine,
    SensorBaseEngine,
    ObservedPropertyBaseEngine,
    FeatureOfInterestBaseEngine,
    ObservationBaseEngine,
    metaclass=ABCMeta
):
    """
    Abstract base engine class for handling CRUD operations and querying SensorThings components.

    Attributes
    ----------
    request : SensorThingsHttpRequest
        The HTTP request object used for communication.
    get_response_schemas : Dict[str, Type[BaseGetResponse]]
        Mapping of component names to their corresponding response schemas.
    """

    def __init__(
            self,
            request: "SensorThingsHttpRequest",
            get_response_schemas: Dict[str, Type["BaseGetResponse"]]
    ):
        self.request = request
        self.get_response_schemas = get_response_schemas

    def list_entities(
            self,
            component: Type['BaseComponent'],
            query_params=None
    ) -> Dict:
        """
        Retrieve a list of entities of a specific component type.

        Parameters
        ----------
        component : Type[BaseComponent]
            The type of component to retrieve.
        query_params : Optional[dict], optional
            Optional query parameters for filtering, pagination, etc.

        Returns
        -------
        Dict
            A dictionary containing the retrieved entities and optional metadata.
        """

        nested_entity_id = self.check_nested_path()

        if nested_entity_id:
            nested_entity_filter = f"{self.request.nested_path[-1][0].__name__}/id eq '{nested_entity_id}'"
            query_params['filters'] = f'{query_params["filters"]} and {nested_entity_filter}' \
                if query_params['filters'] else nested_entity_filter

        entities, count = self.fetch_entities(component=component, query_params=query_params)

        next_link = self.build_next_link(
            query_params=query_params,
            length=len(entities),
            count=count
        )

        response = {
            'value': list(entities.values())
        }

        if query_params.get('count') is True:
            response['count'] = count

        if next_link:
            response['next_link'] = next_link

        return response

    def get_entity(self, component: Type['BaseComponent'], entity_id: id_type, query_params) -> Dict:
        """
        Retrieve a single entity of a specific component type by its ID.

        Parameters
        ----------
        component : Type[BaseComponent]
            The type of component to retrieve.
        entity_id : id_type
            The ID of the entity to retrieve.
        query_params : dict
            Optional query parameters for filtering, pagination, etc.

        Returns
        -------
        Dict
            The retrieved entity.
        """

        nested_entity_id = self.check_nested_path()
        if nested_entity_id and entity_id in [UUID('00000000-0000-0000-0000-000000000000'), '0', 0]:
            entity_id = nested_entity_id

        filter_wrap = "'" if id_type == int else ''
        query_params['filters'] = f"id eq {filter_wrap}{str(entity_id)}{filter_wrap}"

        entities, count = self.fetch_entities(
            component=component,
            query_params=query_params
        )

        entity = next(iter(entities.values()), None)

        if not entity:
            raise HttpError(404, f'{component.__name__} not found.')

        if self.request.value_response is True:
            entity = str(entity.get(query_params['select']))

        return entity

    def create_entity(
            self,
            component: Type['BaseComponent'],
            entity_body: 'BasePostBody',
            response: HttpResponse
    ):
        """
        Create a new entity of a specific component type.

        Parameters
        ----------
        component : Type[BaseComponent]
            The type of component to create.
        entity_body : BasePostBody
            The body containing the data for creating the entity.
        response : HttpResponse
            The HTTP response object to populate with the location of the created entity.
        """

        entity_id = getattr(self, f"create_{component.model_config['json_schema_extra']['name_ref'][1]}")(entity_body)
        response['Location'] = self.build_ref_link(component, entity_id)

    def create_entities(
            self,
            component: Type['BaseComponent'],
            entity_body: 'BasePostBody',
    ) -> List[str]:
        """
        Create multiple entities of a specific component type.

        Parameters
        ----------
        component : Type[BaseComponent]
            The type of component to create.
        entity_body : BasePostBody
            The body containing the data for creating the entities.

        Returns
        -------
        List[str]
            A list of IDs of the created entities.
        """

        return getattr(self, f"create_{component.model_config['json_schema_extra']['name_ref'][2]}")(entity_body)

    def update_entity(
            self,
            component: Type['BaseComponent'],
            entity_id: id_type,
            entity_body: 'BasePatchBody',
    ):
        """
        Update an existing entity of a specific component type.

        Parameters
        ----------
        component : Type[BaseComponent]
            The type of component to update.
        entity_id : id_type
            The ID of the entity to update.
        entity_body : BasePatchBody
            The body containing the data for updating the entity.
        """

        getattr(self, f"update_{component.model_config['json_schema_extra']['name_ref'][1]}")(entity_id, entity_body)

    def delete_entity(
            self,
            component: Type['BaseComponent'],
            entity_id: id_type,
    ):
        """
        Delete an entity of a specific component type.

        Parameters
        ----------
        component : Type[BaseComponent]
            The type of component to delete.
        entity_id : id_type
            The ID of the entity to delete.
        """

        getattr(self, f"delete_{component.model_config['json_schema_extra']['name_ref'][1]}")(entity_id)

    def fetch_entities(
            self,
            component: Type['BaseComponent'],
            query_params=None,
            back_ref_ids=None
    ) -> Tuple[Dict[str, dict], int]:
        """
        Fetch entities of a specific component type with optional query parameters.

        Parameters
        ----------
        component : Type[BaseComponent]
            The type of component to fetch.
        query_params : Optional[dict], optional
            Optional query parameters for filtering, pagination, etc.
        back_ref_ids : Optional[dict], optional
            Optional back reference IDs for fetching related entities.

        Returns
        -------
        Tuple[Dict[str, dict], int]
            A tuple containing a dictionary of fetched entities and the total count of entities.
        """

        query_params = query_params or {}

        entities, count = getattr(self, f"get_{component.model_config['json_schema_extra']['name_ref'][2]}")(
            filters=self.parse_filters(query_params),
            pagination=self.parse_pagination(query_params),
            ordering=self.parse_ordering(query_params),
            get_count=True if query_params.get('count') is True else False,
            **back_ref_ids or {}
        )

        entities = self.insert_self_links(entities=entities, component=component)
        entities = self.insert_related_entities(
            entities=entities,
            component=component,
            query_params=query_params or {},
            include_links=True if back_ref_ids is None else False
        )
        entities = self.remove_unselected_fields(
            entities=entities,
            component=component,
            query_params=query_params or {}
        )

        return entities, count

    def check_nested_path(self):
        """
        Check if there is a nested path in the request and return the ID of the nested entity.

        Returns
        -------
        Optional[str]
            The ID of the nested entity or None if no nested path exists.
        """

        previous_entity = None

        for component, entity_filter_field, entity_id in self.request.nested_path:
            try:
                if not previous_entity and not entity_id:
                    raise HttpError(404, f'{component.__name__} not found.')
                if not entity_id:
                    entity_id = previous_entity.get(entity_filter_field)
                previous_entity = list(getattr(
                    self, f"get_{component.model_config['json_schema_extra']['name_ref'][2]}"
                )(
                    **{f'{entity_filter_field}s': [entity_id]}
                )[0].values())[0]
            except IndexError:
                raise HttpError(404, f'{component.__name__} not found.')

        return previous_entity['id'] if previous_entity else None

    def remove_unselected_fields(
            self,
            entities: Dict[str, dict],
            component: Type['BaseComponent'],
            query_params: dict
    ) -> Dict[str, dict]:
        """
        Removes fields from entities that are not selected in query parameters.

        Parameters
        ----------
        entities : dict
            A dictionary of entities with their fields.
        component : Type['BaseComponent']
            The component type to process.
        query_params : dict
            The query parameters specifying the selected fields.

        Returns
        -------
        dict
            A dictionary of entities with only the selected fields.
        """

        unselected_fields = self.parse_select(component=component, query_params=query_params)
        entities = {
            entity_id: {
                field_name: field_value for field_name, field_value in entity.items()
                if field_name not in unselected_fields
            } for entity_id, entity in entities.items()
        }

        return entities

    def insert_related_entities(
            self,
            entities: Dict[str, dict],
            component: Type['BaseComponent'],
            query_params: dict,
            include_links: bool = True
    ) -> Dict[str, dict]:
        """
        Inserts related entities into the entities based on the expand query parameter.

        Parameters
        ----------
        entities : dict
            A dictionary of entities.
        component : Type['BaseComponent']
            The component type of the entities.
        query_params : dict
            The query parameters containing expand information.
        include_links : bool, optional
            Whether to include links to related entities (default is True).

        Returns
        -------
        dict
            A dictionary of entities with related entities inserted.
        """

        expand_properties = self.parse_expand(
            component=component,
            query_params=query_params
        )

        for related_component_name, related_component_field in component.get_related_components().items():
            if related_component_name not in expand_properties:
                if include_links is True:
                    entities = {
                        entity_id: {
                            f'{related_component_name}_link': f'{entity["self_link"]}/{related_component_field.alias}',
                            **entity
                        } for entity_id, entity in entities.items()
                    }
            else:
                related_component = related_component_field.annotation
                back_ref = related_component_field.json_schema_extra['back_ref']
                component_relationship = related_component_field.json_schema_extra['relationship']

                if component_relationship in ['one_to_many', 'many_to_many']:
                    related_component = related_component.__args__[0]
                    back_ref_ids = {f'{back_ref}s': entities.keys()}
                else:
                    back_ref_ids = {f'{back_ref}s': [entity[back_ref] for entity in entities.values()]}

                if isinstance(related_component, ForwardRef):
                    related_component = getattr(field_schemas, related_component.__forward_arg__)

                related_entities, _ = self.fetch_entities(
                    component=related_component,
                    query_params=expand_properties[related_component_name]['query_params'],
                    back_ref_ids=back_ref_ids
                )

                related_response_schema = self.get_response_schemas[f'{related_component.__name__}GetResponse']

                if component_relationship == 'many_to_many':
                    entities = self.insert_entity_field(
                        entities=entities,
                        entity_field_name=f'{related_component_name}_rel',
                        entity_function=lambda entity_id, entity: [
                            related_response_schema(**related_entity).dict(by_alias=True, exclude_unset=True)
                            for related_entity_id, related_entity in related_entities.items()
                            if entity_id in related_entity[f'{back_ref}s']
                        ]
                    )
                elif component_relationship == 'one_to_many':
                    entities = self.insert_entity_field(
                        entities=entities,
                        entity_field_name=f'{related_component_name}_rel',
                        entity_function=lambda entity_id, entity: [
                            related_response_schema(**related_entity).dict(by_alias=True, exclude_unset=True)
                            for related_entity_id, related_entity in related_entities.items()
                            if related_entity[back_ref] == entity_id
                        ]
                    )
                else:
                    entities = self.insert_entity_field(
                        entities=entities,
                        entity_field_name=f'{related_component_name}_rel',
                        entity_function=lambda entity_id, entity: related_response_schema(
                            **related_entities.get(entity[back_ref])
                        ).dict(by_alias=True, exclude_unset=True)
                    )

        return entities

    def insert_self_links(self, entities: Dict[str, dict], component: Type['BaseComponent']) -> Dict[str, dict]:
        """
        Inserts self-links into the entities.

        Parameters
        ----------
        entities : dict
            A dictionary of entities.
        component : Type['BaseComponent']
            The component type of the entities.

        Returns
        -------
        dict
            A dictionary of entities with self-links inserted.
        """

        return self.insert_entity_field(
            entities=entities,
            entity_field_name='self_link',
            entity_function=lambda entity_id, entity: self.build_ref_link(component, entity_id),
        )

    @staticmethod
    def insert_entity_field(
            entities: Dict[str, dict], entity_field_name: str, entity_function: Callable
    ) -> Dict[str, dict]:
        """
        Inserts a field into each entity based on a provided function.

        Parameters
        ----------
        entities : dict
            A dictionary of entities.
        entity_field_name : str
            The name of the field to insert.
        entity_function : Callable
            A function to generate the field value.

        Returns
        -------
        dict
            A dictionary of entities with the new field inserted.
        """

        return {
            entity_id: {
                entity_field_name: entity_function(entity_id, entity),
                **entity
            } for entity_id, entity in entities.items()
        }

    def parse_select(self, component: Type['BaseComponent'], query_params: dict):
        """
        Parses the select query parameter to determine unselected fields.

        Parameters
        ----------
        component : Type['BaseComponent']
            The component type for which to parse the select parameter.
        query_params : dict
            The query parameters containing the select parameter.

        Returns
        -------
        list
            A list of unselected field names.
        """

        select_parameter = query_params.get('select')

        if self.request.ref_response is True:
            select_parameter = ['@iot.selfLink']
        elif not select_parameter:
            return []
        else:
            select_parameter = select_parameter.split(',')
            if 'id' in select_parameter:
                select_parameter.append('@iot.id')

        unselect_components = [
            field[0] for field in self.get_response_schemas[f'{component.__name__}GetResponse'].model_fields.items()
            if field[1].alias not in select_parameter
        ]

        return unselect_components

    @staticmethod
    def parse_filters(query_params: dict):
        """
        Parses the filters query parameter into a filter object.

        Parameters
        ----------
        query_params : dict
            The query parameters containing the filters.

        Returns
        -------
        object
            The parsed filter object, or None if no filters are specified.
        """

        filter_string = query_params.get('filters')

        if not filter_string:
            return None

        lexer = ODataLexer()
        parser = ODataParser()

        try:
            return parser.parse(lexer.tokenize(filter_string))
        except (ParsingException, TokenizingException):
            raise HttpError(422, 'Failed to parse filter parameter.')

    @staticmethod
    def parse_pagination(query_params: dict) -> dict:
        """
        Parses pagination parameters from query parameters.

        Parameters
        ----------
        query_params : dict
            The query parameters containing pagination information.

        Returns
        -------
        dict
            A dictionary containing pagination parameters.
        """

        return {
            'skip': query_params.get('skip') or 0,
            'top': query_params.get('top') or 100,
            'count': query_params.get('count') or False
        }

    @staticmethod
    def parse_ordering(query_params: dict) -> List[dict]:
        """
        Parses ordering parameters from query parameters.

        Parameters
        ----------
        query_params : dict
            The query parameters containing ordering information.

        Returns
        -------
        list of dict
            A list of dictionaries specifying field names and directions for ordering.
        """

        order_by_string = query_params.get('order_by') or ''
        ordering = [
            {
                'field': order_field.strip().split(' ')[0],
                'direction': 'desc' if order_field.strip().endswith('desc') else 'asc'
            } for order_field in order_by_string.split(',')
        ] if order_by_string != '' else []

        return ordering

    @staticmethod
    def parse_expand(component: Type['BaseComponent'], query_params: dict):
        """
        Parses the expand query parameter for related entities and their nested properties.

        Parameters
        ----------
        component : Type['BaseComponent']
            The component type for which to parse expand parameters.
        query_params : dict
            The query parameters containing the expand parameter.

        Returns
        -------
        dict
            A dictionary mapping related component names to their respective query parameters.
        """

        expand = query_params.get('expand') or ''
        expand_properties = {}
        expand_components = re.split(r',(?![^(]*\))', expand)
        related_components = component.get_related_components()

        for expand_component in expand_components:
            component_name = re.sub(r'(?<!^)(?=[A-Z])', '_', expand_component.split('/')[0].split('(')[0]).lower()
            if component_name not in related_components:
                continue

            nested_query_params = re.search(r'\(.*?\)', expand_component.split('/')[0])
            nested_query_params = nested_query_params.group(0)[1:-1] if nested_query_params else ''
            nested_query_params = {
                nested_query_param.split('=')[0]: nested_query_param.split('=')[1]
                for nested_query_param in nested_query_params.split('&') if nested_query_param
            }

            if component_name not in expand_properties:
                expand_properties[component_name] = {
                    'component': related_components[component_name],
                    'query_params': nested_query_params,
                    'join_ids': []
                }

            if len(expand_component.split('/')) > 1:
                expand_properties[component_name]['query_params']['$expand'] = ','.join(
                    (
                        *expand_properties[component_name]['query_params']['$expand'].split(','),
                        '/'.join(expand_component.split('/')[1:]),
                    )
                ) if '$expand' in expand_properties[component_name]['query_params'] else (
                    '/'.join(expand_component.split('/')[1:])
                )

        for expand_property in expand_properties.values():
            expand_property['query_params'] = ListQueryParams(**expand_property['query_params']).dict()

        return expand_properties

    @staticmethod
    def iso_time_interval(start_time: Optional[datetime], end_time: Optional[datetime]):
        """
        Formats a time interval in ISO 8601 format.

        Parameters
        ----------
        start_time : datetime, optional
            The start time of the interval.
        end_time : datetime, optional
            The end time of the interval.

        Returns
        -------
        Optional[str]
            The formatted ISO 8601 time interval string, or None if both times are None.
        """

        if start_time and end_time and start_time != end_time:
            return start_time.isoformat(timespec='seconds') + '/' + end_time.isoformat(timespec='seconds')
        elif start_time and not end_time:
            return start_time.isoformat(timespec='seconds')
        elif end_time and not start_time:
            return end_time.isoformat(timespec='seconds')
        else:
            return None

    def build_ref_link(self, component: Type['BaseComponent'], entity_id: id_type):
        """
        Builds a reference link for an entity.

        Parameters
        ----------
        component : Type['BaseComponent']
            The component type of the entity for which to build the reference link.
        entity_id : id_type
            The ID of the entity.

        Returns
        -------
        str
            The constructed reference link.
        """

        return (
            f'{self.request.sensorthings_url}/'
            f'{component.model_config["json_schema_extra"]["name_ref"][0]}('
            f'{id_qualifier}{str(entity_id)}{id_qualifier})'
        )

    def build_next_link(
            self,
            query_params: dict,
            length: int,
            count: Optional[int] = None
    ):
        """
        Builds the next link for pagination.

        Parameters
        ----------
        query_params : dict
            The current query parameters for pagination.
        length : int
            The length of the current result set.
        count : int, optional
            The total count of entities available.

        Returns
        -------
        Optional[str]
            The constructed next link for pagination, or None if there are no more pages.
        """

        top = query_params.pop('top', None)
        skip = query_params.pop('skip', None)

        if top is None:
            top = 100

        if skip is None:
            skip = 0

        if count is not None and top + skip < count or count is None and top == length:
            query_string = ListQueryParams(
                top=top,
                skip=top + skip,
                **query_params
            ).get_query_string()

            return f'{self.request.sensorthings_url}/{self.request.sensorthings_path}{query_string}'
        else:
            return None

    def update_related_components(self, component: Type['BaseComponent'], related_entity_id: id_type):
        """
        Updates the related components of an entity.

        Parameters
        ----------
        component : Type['BaseComponent']
            The component type of the related entity.
        related_entity_id : id_type
            The ID of the related entity.

        Returns
        -------
        None
        """

        if component.__name__ == 'Datastream':
            first_observation = next(iter(self.list_entities(
                component=field_schemas.Observation,
                query_params=ListQueryParams(
                    select='',
                    filters=f'Datastream/id eq \'{str(related_entity_id)}\'',
                    expand='Datastream',
                    order_by='phenomenonTime asc',
                    top=1,
                    count=False
                ).dict()
            )['value']), {})

            last_observation = next(iter(self.list_entities(
                component=field_schemas.Observation,
                query_params=ListQueryParams(
                    select='',
                    filters=f'Datastream/id eq \'{str(related_entity_id)}\'',
                    expand='Datastream',
                    order_by='phenomenonTime desc',
                    top=1,
                    count=False
                ).dict()
            )['value']), {})

            phenomenon_time_range = []
            result_time_range = []

            for observation in [first_observation, last_observation]:
                if observation.get('phenomenon_time') is not None:
                    phenomenon_time_range.append(isoparse(observation['phenomenon_time']).replace(tzinfo=pytz.UTC))
                else:
                    phenomenon_time_range.append(None)
                if observation.get('result_time') is not None:
                    result_time_range.append(isoparse(observation['result_time']).replace(tzinfo=pytz.UTC))
                else:
                    result_time_range.append(None)

            phenomenon_time = self.iso_time_interval(phenomenon_time_range[0], phenomenon_time_range[1])
            result_time = self.iso_time_interval(result_time_range[0], result_time_range[1])
            phenomenon_time = phenomenon_time.replace('+00:00', 'Z') if phenomenon_time else None  # noqa
            result_time = result_time.replace('+00:00', 'Z') if result_time else None  # noqa

            self.update_entity(
                component=field_schemas.Datastream,
                entity_id=related_entity_id,
                entity_body=DatastreamPatchBody(  # noqa
                    phenomenon_time=phenomenon_time,
                    result_time=result_time
                )  # noqa
            )
