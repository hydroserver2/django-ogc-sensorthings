from django.contrib import admin
from sensorthings.versions.v1_1.backends.django.models import (Thing, Location, HistoricalLocation, Sensor,
                                                               ObservedProperty, Observation, FeatureOfInterest,
                                                               Datastream)


class ThingAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    verbose_name = "Things"


class LocationAdmin(admin.ModelAdmin):
    list_display = ("id", "name")


class HistoricalLocationAdmin(admin.ModelAdmin):
    list_display = ("id", "time")


class SensorAdmin(admin.ModelAdmin):
    list_display = ("id", "name")


class ObservedPropertyAdmin(admin.ModelAdmin):
    list_display = ("id", "name")


class DatastreamAdmin(admin.ModelAdmin):
    list_display = ("id", "name")


class ObservationAdmin(admin.ModelAdmin):
    list_display = ("id", "phenomenon_time_begin", "result")


class FeatureOfInterestAdmin(admin.ModelAdmin):
    list_display = ("id", "name")


admin.site.register(Thing, ThingAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(HistoricalLocation, HistoricalLocationAdmin)
admin.site.register(Sensor, SensorAdmin)
admin.site.register(ObservedProperty, ObservedPropertyAdmin)
admin.site.register(Datastream, DatastreamAdmin)
admin.site.register(Observation, ObservationAdmin)
admin.site.register(FeatureOfInterest, FeatureOfInterestAdmin)
