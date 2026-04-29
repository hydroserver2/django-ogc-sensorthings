from sensorthings.versions.v1_1.backends.django.models import Thing, HistoricalLocation, Location


def create_test_thing(
    *,
    name: str = "Test Thing",
    description: str = "This is a thing used for testing.",
    properties: dict | None = None,
    locations: list[Location] | None = None,
    historical_locations: list[HistoricalLocation] | None = None,
) -> Thing:

    thing = Thing.objects.create(
        name=name,
        description=description,
        properties=properties,
    )

    if locations:
        thing.locations.set(locations)

    if historical_locations:
        thing.historical_locations.set(historical_locations)

    return thing
