from sensorthings.v1_1.conf import app_settings


class IOT:
    VERSION = "v1.1"
    ID = "@iot.id"
    SELF_LINK = "@iot.selfLink"
    COUNT = "@iot.count"
    NEXT_LINK = "@iot.nextLink"
    NAVIGATION_LINK = "@iot.navigationLink"

    THINGS = "Things"
    THING = "Thing"

    LOCATIONS = "Locations"
    LOCATION = "Location"

    HISTORICAL_LOCATIONS = "HistoricalLocations"
    HISTORICAL_LOCATION = "HistoricalLocation"

    DATASTREAMS = "Datastreams"
    DATASTREAM = "Datastream"

    OBSERVED_PROPERTIES = "ObservedProperties"
    OBSERVED_PROPERTY = "ObservedProperty"

    SENSORS = "Sensors"
    SENSOR = "Sensor"

    OBSERVATIONS = "Observations"
    OBSERVATION = "Observation"

    FEATURES_OF_INTEREST = "FeaturesOfInterest"
    FEATURE_OF_INTEREST = "FeatureOfInterest"

    @staticmethod
    def _iot_id_part(iot_id: app_settings.ID_TYPE) -> str:
        return f"({app_settings.ID_DELIMITER}{iot_id}{app_settings.ID_DELIMITER})"

    def build_entity_link(self, entity: str) -> str:
        return f"{app_settings.SERVICE_URL}/{self.VERSION}/{entity}"

    def build_self_link(self, entity: str, iot_id: app_settings.ID_TYPE) -> str:
        return f"{self.build_entity_link(entity)}{self._iot_id_part(iot_id)}"

    def build_nav_link(self, entity: str, iot_id: app_settings.ID_TYPE, related_entity: str) -> str:
        return f"{self.build_self_link(entity, iot_id)}/{related_entity}"
