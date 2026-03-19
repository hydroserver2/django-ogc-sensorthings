from sensorthings.versions.v1_1 import Location, Thing, HistoricalLocation


def create_test_feature_of_interest(
    *,
    name: str = "Test Feature of Interest",
    description: str = "This is a feature of interest used for testing.",
    encoding_type: str = Location.GEOJSON,
    location: dict | None = None,
    properties: dict | None = None,
    things: list[Thing] | None = None,
    historical_locations: list[HistoricalLocation] | None = None,
) -> Location:
    """"""

    if location is None:
        location = {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [-111.891, 40.7608]},
            "properties": {}
        }

    if things is None:
        things = []

    if historical_locations is None:
        historical_locations = []

    return Location.objects.create(
        name=name,
        description=description,
        encoding_type=encoding_type,
        location=location,
        properties=properties,
        things=things,
        historical_locations=historical_locations,
    )
