from datetime import datetime, timezone
from sensorthings.versions.v1_1.backends.django.models import HistoricalLocation, Location, Thing
from .thing import create_test_thing


def create_test_historical_location(
    *,
    time: datetime = datetime.now(timezone.utc),
    thing: Thing | None = None,
    locations: list[Location] | None = None,
) -> HistoricalLocation:

    if thing is None:
        thing = create_test_thing()

    historical_location = HistoricalLocation.objects.create(
        time=time,
        thing=thing,
    )

    if locations:
        historical_location.locations.set(locations)

    return historical_location
