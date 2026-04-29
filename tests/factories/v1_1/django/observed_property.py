from sensorthings.versions.v1_1.backends.django.models import ObservedProperty


def create_test_observed_property(
    *,
    name: str = "Test Observed Property",
    definition: str = "https://www.example.com/observed-properties/test",
    description: str = "This is an observed property used for testing.",
    properties: dict | None = None,
) -> ObservedProperty:

    return ObservedProperty.objects.create(
        name=name,
        definition=definition,
        description=description,
        properties=properties,
    )
