from dataclasses import dataclass, field
from typing import Any, Dict, List, Callable, Type, Literal, Union
from django.conf import settings as django_settings


SETTINGS_PREFIX = "SENSORTHINGS_V1_1_"


@dataclass(frozen=True)
class AppSettings:
    SERVICE_URL: str = ""
    """The base service URL SensorThings will be served from."""

    ID_TYPE: type = int
    """The type used for entity IDs."""

    ID_DELIMITER: str = ""
    """The delimiter character for entity IDs in resource paths."""

    ID_EXAMPLE: Union[str, None] = None
    """An example value for entity IDs."""

    MAX_TOP: int = 100
    """The maximum length of a collection response returned by the service."""

    AUTH_HANDLERS: Dict = field(default_factory=dict)
    """Custom authentication handlers for HTTP endpoints."""

    DEFAULT_AUTH_HANDLER: Union[List[Callable], None] = None
    """Default authentication handler for HTTP endpoints."""

    PROPERTIES_SCHEMAS: Dict = field(default_factory=dict)
    """Custom schemas for entity properties fields."""

    LOCATION_ENCODING_TYPE_SCHEMA: Type = Dict
    """Type declaration for location encoding."""

    LOCATION_ENCODING_TYPE_VALUE_LITERAL: Literal = field(default_factory=lambda: Literal[
        "application/geo+json"
    ])
    """Allowed values for location encoding type."""

    OBSERVATION_TYPE_SCHEMA: Type = float
    """Type declaration for observation result."""

    OBSERVATION_TYPE_VALUE_LITERAL: Literal = field(default_factory=lambda: Literal[
        "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_CategoryObservation",
        "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_CountObservation",
        "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement",
        "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Observation",
        "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_TruthObservation"
    ])
    """Allowed values for observation type."""

    SENSOR_METADATA_ENCODING_TYPE_SCHEMA: Type = str
    """Type declaration for sensor encoding."""

    SENSOR_METADATA_ENCODING_TYPE_VALUE_LITERAL: Literal = field(default_factory=lambda: Literal[
        "application/pdf",
        "http://www.opengis.net/doc/IS/SensorML/2.0",
        "text/html"
    ])
    """Allowed values for sensor encoding type."""

    FEATURE_OF_INTEREST_ENCODING_TYPE_SCHEMA: Type = Dict
    """Type declaration for feature of interest encoding."""

    FEATURE_OF_INTEREST_ENCODING_TYPE_VALUE_LITERAL: Literal = field(default_factory=lambda: Literal[
        "application/geo+json"
    ])

    def __getattribute__(self, name: str) -> Any:
        if name in ("__dict__", "__class__"):
            return super().__getattribute__(name)

        prefixed_name = f"{SETTINGS_PREFIX}{name}"
        if hasattr(django_settings, prefixed_name):
            return getattr(django_settings, prefixed_name)

        return super().__getattribute__(name)


app_settings = AppSettings()
