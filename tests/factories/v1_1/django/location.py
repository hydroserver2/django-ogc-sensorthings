from sensorthings.versions.v1_1.backends.django.models import Location, Thing


def create_test_location(
    *,
    name: str = "Test Location",
    description: str = "This is a location used for testing.",
    encoding_type: str = Location.GEOJSON,
    location: dict | None = None,
    properties: dict | None = None,
    things: list[Thing] | None = None,
) -> Location:

    if location is None:
        location = {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [-111.891, 40.7608]},
            "properties": {}
        }

    loc = Location.objects.create(
        name=name,
        description=description,
        encoding_type=encoding_type,
        location=location,
        properties=properties,
    )

    if things:
        loc.things.set(things)

    return loc
