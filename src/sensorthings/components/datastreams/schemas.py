from typing import TYPE_CHECKING, Literal, List, Union, Dict, Optional
from pydantic import Field, ConfigDict
from ninja import Schema
from sensorthings.schemas import (BaseComponent, BaseListResponse, BaseGetResponse, BasePostBody, BasePatchBody,
                                  EntityId)
from sensorthings.types import ISOTimeString, ISOIntervalString, AnyHttpUrlString

if TYPE_CHECKING:
    from sensorthings.components.things.schemas import Thing
    from sensorthings.components.sensors.schemas import Sensor
    from sensorthings.components.observedproperties.schemas import ObservedProperty
    from sensorthings.components.observations.schemas import Observation

observationTypes = Literal[
    'http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_CategoryObservation',
    'http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_CountObservation',
    'http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement',
    'http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Observation',
    'http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_TruthObservation'
]


class UnitOfMeasurement(Schema):
    """
    A schema representing the unit of measurement for a datastream.

    Attributes
    ----------
    name : str
        The name of the unit of measurement.
    symbol : str
        The symbol of the unit of measurement.
    definition : str
        The definition of the unit of measurement.
    """

    name: str = Field(..., alias="name")
    symbol: str = Field(..., alias="symbol")
    definition: str = Field(..., alias="definition")


class DatastreamFields(Schema):
    """
    A schema representing the fields of a datastream.

    Attributes
    ----------
    name : str
        The name of the datastream.
    description : str
        The description of the datastream.
    unit_of_measurement : UnitOfMeasurement
        The unit of measurement used by the datastream.
    observation_type : observationTypes
        The type of observation conducted by the datastream.
    observed_area : dict, optional
        The geographical area observed by the datastream.
    phenomenon_time : Union[ISOTimeString, ISOIntervalString, None], optional
        The time period during which the phenomenon was observed.
    result_time : Union[ISOTimeString, ISOIntervalString, None], optional
        The time when the result was generated.
    properties : dict, optional
        Additional properties of the datastream.
    """

    name: str = Field(..., alias='name')
    description: str = Field(..., alias='description')
    unit_of_measurement: UnitOfMeasurement = Field(..., alias='unitOfMeasurement')
    observation_type: observationTypes = Field(..., alias='observationType')
    observed_area: Optional[dict] = Field(None, alias='observedArea')
    phenomenon_time: Optional[Union[ISOTimeString, ISOIntervalString]] = Field(None, alias='phenomenonTime')
    result_time: Optional[Union[ISOTimeString, ISOIntervalString]] = Field(None, alias='resultTime')
    properties: Optional[dict] = Field(None, alias='properties')


class DatastreamRelations(Schema):
    """
    A schema representing the relations of a datastream to other components.

    Attributes
    ----------
    thing : 'Thing'
        The thing associated with the datastream.
    sensor : 'Sensor'
        The sensor associated with the datastream.
    observed_property : 'ObservedProperty'
        The observed property associated with the datastream.
    observations : List['Observation']
        The list of observations related to the datastream.
    """

    thing: 'Thing' = Field(
        ..., alias='Thing', json_schema_extra={'relationship': 'many_to_one', 'back_ref': 'thing_id'}
    )
    sensor: 'Sensor' = Field(
        ..., alias='Sensor', json_schema_extra={'relationship': 'many_to_one', 'back_ref': 'sensor_id'}
    )
    observed_property: 'ObservedProperty' = Field(
        ..., alias='ObservedProperty',
        json_schema_extra={'relationship': 'many_to_one', 'back_ref': 'observed_property_id'}
    )
    observations: List['Observation'] = Field(
        [], alias='Observations', json_schema_extra={'relationship': 'one_to_many', 'back_ref': 'datastream_id'}
    )


class Datastream(BaseComponent, DatastreamFields, DatastreamRelations):
    """
    A schema representing a datastream.

    This class combines the fields and relations of a datastream, and extends the BaseComponent class.
    """

    model_config = ConfigDict(json_schema_extra={'name_ref': ('Datastreams', 'datastream', 'datastreams')})


class DatastreamPostBody(BasePostBody, DatastreamFields):
    """
    A schema for the body of a POST request to create a new datastream.

    Attributes
    ----------
    thing : Union[EntityId]
        The thing associated with the datastream.
    sensor : Union[EntityId]
        The sensor associated with the datastream.
    observed_property : Union[EntityId]
        The observed property associated with the datastream.
    """

    thing: Union[EntityId] = Field(
        ..., alias='Thing', json_schema_extra={'nested_class': 'ThingPostBody'}
    )
    sensor: Union[EntityId] = Field(
        ..., alias='Sensor', json_schema_extra={'nested_class': 'SensorPostBody'}
    )
    observed_property: Union[EntityId] = Field(
        ..., alias='ObservedProperty', json_schema_extra={'nested_class': 'ObservedPropertyPostBody'}
    )


class DatastreamPatchBody(BasePatchBody, DatastreamFields):
    """
    A schema for the body of a PATCH request to update an existing datastream.

    Attributes
    ----------
    thing : Optional[EntityId]
        The thing associated with the datastream.
    sensor : Optional[EntityId]
        The sensor associated with the datastream.
    observed_property : Optional[EntityId]
        The observed property associated with the datastream.
    """

    thing: Optional[EntityId] = Field(None, alias='Thing')
    sensor: Optional[EntityId] = Field(None, alias='Sensor')
    observed_property: Optional[EntityId] = Field(None, alias='ObservedProperty')


class DatastreamGetResponse(DatastreamFields, BaseGetResponse):
    """
    A schema for the response of a GET request for a datastream.

    Attributes
    ----------
    thing_link : AnyHttpUrlString, optional
        The navigation link for the thing associated with the datastream.
    thing_rel : Dict, optional
        The relationship details for the thing associated with the datastream.
    sensor_link : AnyHttpUrlString, optional
        The navigation link for the sensor associated with the datastream.
    sensor_rel : Dict, optional
        The relationship details for the sensor associated with the datastream.
    observed_property_link : AnyHttpUrlString, optional
        The navigation link for the observed property associated with the datastream.
    observed_property_rel : Dict, optional
        The relationship details for the observed property associated with the datastream.
    observations_link : AnyHttpUrlString, optional
        The navigation link for the observations associated with the datastream.
    observations_rel : Union[List[dict], dict], optional
        The relationship details for the observations associated with the datastream.
    """

    thing_link: AnyHttpUrlString = Field(None, alias='Thing@iot.navigationLink')
    thing_rel: Dict = Field(None, alias='Thing', json_schema_extra={'nested_class': 'ThingGetResponse'})
    sensor_link: AnyHttpUrlString = Field(None, alias='Sensor@iot.navigationLink')
    sensor_rel: Dict = Field(None, alias='Sensor', json_schema_extra={'nested_class': 'SensorGetResponse'})
    observed_property_link: AnyHttpUrlString = Field(None, alias='ObservedProperty@iot.navigationLink')
    observed_property_rel: Dict = Field(
        None, alias='ObservedProperty',
        json_schema_extra={'nested_class': 'ObservedPropertyGetResponse'}
    )
    observations_link: AnyHttpUrlString = Field(None, alias='Observations@iot.navigationLink')
    observations_rel: Union[List[dict], dict] = Field(
        None, alias='Observations', json_schema_extra={'nested_class': 'ObservationGetResponse'}
    )


class DatastreamListResponse(BaseListResponse):
    """
    A schema for the response of a GET request for a list of datastreams.

    Attributes
    ----------
    value : List[DatastreamGetResponse]
        The list of datastreams.
    """

    value: List[DatastreamGetResponse]
