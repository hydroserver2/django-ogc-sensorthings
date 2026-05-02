from datetime import datetime
from sensorthings.versions.v1_1.backends.django.models import Datastream, Sensor, Thing, ObservedProperty
from .thing import create_test_thing
from .sensor import create_test_sensor
from .observed_property import create_test_observed_property


def create_test_datastream(
    *,
    name: str = "Test Datastream",
    description: str = "This is a datastream used for testing.",
    unit_of_measurement: dict | None = None,
    observation_type: str = Datastream.OM_MEASUREMENT,
    properties: dict | None = None,
    observed_area: dict | None = None,
    phenomenon_time_begin: datetime | None = None,
    phenomenon_time_end: datetime | None = None,
    result_time_begin: datetime | None = None,
    result_time_end: datetime | None = None,
    thing: Thing | None = None,
    sensor: Sensor | None = None,
    observed_property: ObservedProperty | None = None,
) -> Datastream:

    if unit_of_measurement is None:
        unit_of_measurement = {
            "name": "Test Unit",
            "symbol": "T",
            "definition": "https://www.example.com/units/test"
        }

    if thing is None:
        thing = create_test_thing()

    if sensor is None:
        sensor = create_test_sensor()

    if observed_property is None:
        observed_property = create_test_observed_property()

    return Datastream.objects.create(
        name=name,
        description=description,
        unit_of_measurement=unit_of_measurement,
        observation_type=observation_type,
        properties=properties,
        observed_area=observed_area,
        phenomenon_time_begin=phenomenon_time_begin,
        phenomenon_time_end=phenomenon_time_end,
        result_time_begin=result_time_begin,
        result_time_end=result_time_end,
        thing=thing,
        sensor=sensor,
        observed_property=observed_property,
    )
