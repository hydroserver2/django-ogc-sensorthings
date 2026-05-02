from sensorthings.versions.v1_1.backends.django.models import FeatureOfInterest


def create_test_feature_of_interest(
    *,
    name: str = "Test Feature of Interest",
    description: str = "This is a feature of interest used for testing.",
    encoding_type: str = FeatureOfInterest.GEOJSON,
    feature: dict | None = None,
    properties: dict | None = None,
) -> FeatureOfInterest:

    if feature is None:
        feature = {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [-111.891, 40.7608]},
            "properties": {}
        }

    return FeatureOfInterest.objects.create(
        name=name,
        description=description,
        encoding_type=encoding_type,
        feature=feature,
        properties=properties,
    )
