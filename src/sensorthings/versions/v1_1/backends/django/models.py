from uuid import UUID
from uuid_utils import uuid7
from django.db import models


def uuid7_uuid() -> UUID:
    return UUID(int=uuid7().int)


class Thing(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid7_uuid, editable=False)
    name = models.TextField()
    description = models.TextField()
    properties = models.JSONField(null=True, blank=True)

    objects = models.Manager()


class Location(models.Model):
    GEOJSON = "application/geo+json"

    ENCODING_TYPE_CHOICES = [
        (GEOJSON, GEOJSON),
    ]

    id = models.UUIDField(primary_key=True, default=uuid7_uuid, editable=False)
    name = models.TextField()
    description = models.TextField()
    encoding_type = models.TextField(choices=ENCODING_TYPE_CHOICES, default=GEOJSON)
    location = models.JSONField()
    properties = models.JSONField(null=True, blank=True)
    things = models.ManyToManyField(
        Thing,
        related_name="locations",
        blank=True,
    )

    objects = models.Manager()


class HistoricalLocation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid7_uuid, editable=False)
    time = models.DateTimeField()
    thing = models.ForeignKey(
        Thing, on_delete=models.CASCADE, related_name="historical_locations"
    )

    locations = models.ManyToManyField(
        Location,
        related_name="historical_locations",
        blank=True,
    )

    objects = models.Manager()

    class Meta:
        verbose_name_plural = "Historical Locations"
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

    id = models.UUIDField(primary_key=True, default=uuid7_uuid, editable=False)
    name = models.TextField()
    description = models.TextField()
    encoding_type = models.TextField(choices=ENCODING_TYPE_CHOICES)
    metadata = models.TextField()
    properties = models.JSONField(null=True, blank=True)

    objects = models.Manager()


class ObservedProperty(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid7_uuid, editable=False)
    name = models.TextField()
    definition = models.TextField()
    description = models.TextField()
    properties = models.JSONField(null=True, blank=True)

    objects = models.Manager()

    class Meta:
        verbose_name_plural = "Observed Properties"


class Datastream(models.Model):
    OM_MEASUREMENT = (
        f"http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement"
    )

    OBSERVATION_TYPE_CHOICES = [
        (OM_MEASUREMENT, OM_MEASUREMENT),
    ]

    id = models.UUIDField(primary_key=True, default=uuid7_uuid, editable=False)
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

    objects = models.Manager()


class FeatureOfInterest(models.Model):
    GEOJSON = "application/geo+json"

    ENCODING_TYPE_CHOICES = [
        (GEOJSON, GEOJSON),
    ]

    id = models.UUIDField(primary_key=True, default=uuid7_uuid, editable=False)
    name = models.TextField()
    description = models.TextField()
    encoding_type = models.TextField(choices=ENCODING_TYPE_CHOICES)
    feature = models.JSONField()
    properties = models.JSONField(null=True, blank=True)

    objects = models.Manager()

    class Meta:
        verbose_name_plural = "Features of Interest"


class Observation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid7_uuid, editable=False)
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

    objects = models.Manager()
