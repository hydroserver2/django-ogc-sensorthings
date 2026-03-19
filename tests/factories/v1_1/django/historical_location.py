from datetime import datetime
from sensorthings.versions.v1_1 import HistoricalLocation, Location, Thing
from .thing import create_test_thing


def create_test_historical_location(
    *,
    time: datetime = datetime.utcnow(),
    thing: Thing | None = None,
    locations: list[Location] | None = None,
) -> HistoricalLocation:
    """"""

    if thing is None:
        thing = create_test_thing()

    return HistoricalLocation.objects.create(
        time=time,
        thing=thing,
        locations=locations,
    )
