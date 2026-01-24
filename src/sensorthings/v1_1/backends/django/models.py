from uuid_utils import uuid7
from django.db import models


class Thing(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid7, editable=False)
    name = models.TextField()
    description = models.TextField()
    properties = models.JSONField(null=True, blank=True)
    location = models.ForeignKey(
        "Location",
        related_name="things",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )


class Location(models.Model):
    GEOJSON = "application/geo+json"

    ENCODING_TYPE_CHOICES = [
        (GEOJSON, GEOJSON),
    ]

    id = models.UUIDField(primary_key=True, default=uuid7, editable=False)
    name = models.TextField()
    description = models.TextField()
    encoding_type = models.TextField(choices=ENCODING_TYPE_CHOICES, default=GEOJSON)
    location = models.JSONField()
    properties = models.JSONField(null=True, blank=True)


class HistoricalLocation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid7, editable=False)
    time = models.DateTimeField()
    thing = models.ForeignKey(
        Thing, on_delete=models.CASCADE, related_name="historical_locations"
    )
    location = models.ForeignKey(
        Location, on_delete=models.CASCADE, related_name="historical_locations"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["thing", "time"], name="unique_historical_location_per_time"
            )
        ]


class Sensor(models.Model):
    PDF = "application/pdf"
    SENSOR_ML = "http://www.opengis.net/doc/IS/SensorML/2.0"
    HTML = "text/html"

    ENCODING_TYPE_CHOICES = [
        (PDF, PDF),
        (SENSOR_ML, SENSOR_ML),
        (HTML, HTML),
    ]

    id = models.UUIDField(primary_key=True, default=uuid7, editable=False)
    name = models.TextField()
    description = models.TextField()
    encoding_type = models.TextField(choices=ENCODING_TYPE_CHOICES)
    metadata = models.TextField()
    properties = models.JSONField(null=True, blank=True)


class ObservedProperty(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid7, editable=False)
    name = models.TextField()
    definition = models.TextField()
    description = models.TextField()
    properties = models.JSONField(null=True, blank=True)


class Datastream(models.Model):
    OM_MEASUREMENT = (
        f"http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement"
    )

    OBSERVATION_TYPE_CHOICES = [
        (OM_MEASUREMENT, OM_MEASUREMENT),
    ]

    id = models.UUIDField(primary_key=True, default=uuid7, editable=False)
    name = models.TextField()
    description = models.TextField()
    unit_of_measurement = models.JSONField()
    observation_type = models.TextField(choices=OBSERVATION_TYPE_CHOICES)
    properties = models.JSONField(null=True, blank=True)
    observed_area = models.JSONField(null=True, blank=True)
    phenomenon_time_begin = models.DateTimeField(null=True, blank=True)
    phenomenon_time_end = models.DateTimeField(null=True, blank=True)
    result_time_begin = models.DateTimeField(null=True, blank=True)
    result_time_end = models.DateTimeField(null=True, blank=True)
    thing = models.ForeignKey(
        Thing, on_delete=models.CASCADE, related_name="datastreams"
    )
    sensor = models.ForeignKey(
        Sensor, on_delete=models.CASCADE, related_name="datastreams"
    )
    observed_property = models.ForeignKey(
        ObservedProperty, on_delete=models.CASCADE, related_name="datastreams"
    )


class FeatureOfInterest(models.Model):
    GEOJSON = "application/geo+json"

    ENCODING_TYPE_CHOICES = [
        (GEOJSON, GEOJSON),
    ]

    id = models.UUIDField(primary_key=True, default=uuid7, editable=False)
    name = models.TextField()
    description = models.TextField()
    encoding_type = models.TextField(choices=ENCODING_TYPE_CHOICES)
    feature = models.JSONField()
    properties = models.JSONField(null=True, blank=True)


class Observation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid7, editable=False)
    phenomenon_time_begin = models.DateTimeField()
    phenomenon_time_end = models.DateTimeField(null=True, blank=True)
    result = models.FloatField()
    result_time = models.DateTimeField()
    result_quality = models.JSONField(null=True, blank=True)
    valid_time_begin = models.DateTimeField(null=True, blank=True)
    valid_time_end = models.DateTimeField(null=True, blank=True)
    parameters = models.JSONField(null=True, blank=True)
    datastream = models.ForeignKey(
        Datastream, on_delete=models.CASCADE, related_name="observations"
    )
    feature_of_interest = models.ForeignKey(
        FeatureOfInterest, on_delete=models.CASCADE, related_name="observations"
    )
