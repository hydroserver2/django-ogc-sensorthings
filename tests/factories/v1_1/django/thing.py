from sensorthings.versions.v1_1 import Thing, HistoricalLocation, Location


def create_test_thing(
    *,
    name: str = "Test Thing",
    description: str = "This is a thing used for testing.",
    properties: dict | None = None,
    locations: list[Location] | None = None,
    historical_locations: list[HistoricalLocation] | None = None,
) -> Thing:
    """"""

    if locations is None:
        locations = []

    if historical_locations is None:
        historical_locations = []

    return Thing.objects.create(
        name=name,
        description=description,
        properties=properties,
        locations=locations,
        historical_locations=historical_locations,
    )
