from sensorthings.versions.v1_1.backends.django.models import Sensor


def create_test_sensor(
    *,
    name: str = "Test Sensor",
    description: str = "This is a sensor used for testing.",
    encoding_type: str = Sensor.PDF,
    metadata: str = "https://www.example.com/sensors/test.pdf",
    properties: dict | None = None,
) -> Sensor:

    return Sensor.objects.create(
        name=name,
        description=description,
        encoding_type=encoding_type,
        metadata=metadata,
        properties=properties,
    )
