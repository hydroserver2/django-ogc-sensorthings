from typing import TYPE_CHECKING, Literal, List, Optional
from pydantic import Field, ConfigDict
from ninja import Schema
from sensorthings.schemas import EntityId, BaseComponent, BaseListResponse, BaseGetResponse, BasePostBody, BasePatchBody
from sensorthings.types import AnyHttpUrlString

if TYPE_CHECKING:
    from sensorthings.components.datastreams.schemas import Datastream


sensorEncodingTypes = Literal[
    'application/pdf',
    'http://www.opengis.net/doc/IS/SensorML/2.0',
    'text/html'
]


class SensorFields(Schema):
    """
    A schema representing the fields of a sensor.

    Attributes
    ----------
    name : str
        The name of the sensor.
    description : str
        The description of the sensor.
    encoding_type : sensorEncodingTypes
        The encoding type of the sensor.
    metadata : str
        The metadata of the sensor.
    properties : Optional[dict], optional
        Additional properties of the sensor.
    """

    name: str = Field(..., alias='name')
    description: str = Field(..., alias='description')
    encoding_type: sensorEncodingTypes = Field(..., alias='encodingType')
    metadata: str = Field(..., alias='metadata')
    properties: Optional[dict] = Field(None, alias='properties')


class SensorRelations(Schema):
    """
    A schema representing the relations of a sensor to other components.

    Attributes
    ----------
    datastreams : List['Datastream']
        The datastreams associated with the sensor.
    """

    datastreams: List['Datastream'] = Field(
        [], alias='Datastreams', json_schema_extra={'relationship': 'one_to_many', 'back_ref': 'sensor_id'}
    )


class Sensor(BaseComponent, SensorFields, SensorRelations):
    """
    A schema representing a sensor.

    This class combines the fields and relations of a sensor, and extends the BaseComponent class.
    """

    model_config = ConfigDict(json_schema_extra={'name_ref': ('Sensors', 'sensor', 'sensors')})


class SensorPostBody(BasePostBody, SensorFields):
    """
    A schema for the body of a POST request to create a new sensor.

    Attributes
    ----------
    datastreams : List[EntityId]
        The IDs of the datastreams associated with the sensor.
    """

    datastreams: List[EntityId] = Field(
        [], alias='Datastreams', json_schema_extra={'nested_class': 'DatastreamPostBody'}
    )


class SensorPatchBody(BasePatchBody, SensorFields):
    """
    A schema for the body of a PATCH request to update an existing sensor.
    """

    pass


class SensorGetResponse(SensorFields, BaseGetResponse):
    """
    A schema for the response of a GET request for a sensor.

    Attributes
    ----------
    datastreams_link : AnyHttpUrlString
        The navigation link for the datastreams associated with the sensor.
    datastreams_rel : List[dict]
        The relationship details for the datastreams associated with the sensor.
    """

    datastreams_link: AnyHttpUrlString = Field(None, alias='Datastreams@iot.navigationLink')
    datastreams_rel: List[dict] = Field(
        None, alias='Datastreams', json_schema_extra={'nested_class': 'DatastreamGetResponse'}
    )


class SensorListResponse(BaseListResponse):
    """
    A schema for the response of a GET request for a list of sensors.

    Attributes
    ----------
    value : List[SensorGetResponse]
        The list of sensors.
    """

    value: List[SensorGetResponse]
