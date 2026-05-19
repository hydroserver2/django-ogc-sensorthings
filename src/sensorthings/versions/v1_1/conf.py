from dataclasses import dataclass, field
from typing import Any, ClassVar, Literal
from sensorthings.core import BaseSettings


SETTINGS_PREFIX = "SENSORTHINGS_V1_1_"


@dataclass(frozen=True)
class AppSettings(BaseSettings):
    """
    Application-level configuration for the SensorThings v1.1 service.

    Each attribute can be overridden by defining a Django setting with
    the same name prefixed by ``SENSORTHINGS_V1_1_``.
    """

    SETTINGS_PREFIX = "SENSORTHINGS_V1_1_"

    IMPORT_STRING_SETTINGS: ClassVar[frozenset[str]] = BaseSettings.IMPORT_STRING_SETTINGS | frozenset({
        "RENDERER",
        "PROPERTIES_SCHEMAS",
        "LOCATION_ENCODING_TYPE_SCHEMA",
        "LOCATION_ENCODING_TYPE_VALUE_LITERAL",
        "OBSERVATION_TYPE_SCHEMA",
        "OBSERVATION_TYPE_VALUE_LITERAL",
        "SENSOR_METADATA_ENCODING_TYPE_SCHEMA",
        "SENSOR_METADATA_ENCODING_TYPE_VALUE_LITERAL",
        "FEATURE_OF_INTEREST_ENCODING_TYPE_SCHEMA",
        "FEATURE_OF_INTEREST_ENCODING_TYPE_VALUE_LITERAL",
    })

    RENDERER: Any = None
    """Custom Django Ninja renderer instance (subclass of ninja.renderers.BaseRenderer). May be a dotted import string."""

    DOCS_ENABLED: bool = True
    """Whether to expose the Swagger UI and OpenAPI schema endpoints."""

    PROPERTIES_SCHEMAS: dict[str, Any] = field(default_factory=dict)
    """Custom schemas for entity property fields. Dict values may be dotted import strings."""

    LOCATION_ENCODING_TYPE_SCHEMA: type = dict
    """Type declaration for location encoding."""

    LOCATION_ENCODING_TYPE_VALUE_LITERAL: Literal = field(
        default_factory=lambda: Literal["application/geo+json"]
    )
    """Allowed values for location encoding type."""

    OBSERVATION_TYPE_SCHEMA: type = float
    """Type declaration for observation result."""

    OBSERVATION_TYPE_VALUE_LITERAL: Literal = field(
        default_factory=lambda: Literal[
            "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_CategoryObservation",
            "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_CountObservation",
            "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement",
            "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Observation",
            "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_TruthObservation",
        ]
    )
    """Allowed values for observation type."""

    SENSOR_METADATA_ENCODING_TYPE_SCHEMA: type = str
    """Type declaration for sensor metadata encoding."""

    SENSOR_METADATA_ENCODING_TYPE_VALUE_LITERAL: Literal = field(
        default_factory=lambda: Literal[
            "application/pdf",
            "http://www.opengis.net/doc/IS/SensorML/2.0",
            "text/html",
        ]
    )
    """Allowed values for sensor metadata encoding type."""

    FEATURE_OF_INTEREST_ENCODING_TYPE_SCHEMA: type = dict
    """Type declaration for feature of interest encoding."""

    FEATURE_OF_INTEREST_ENCODING_TYPE_VALUE_LITERAL: Literal = field(
        default_factory=lambda: Literal["application/geo+json"]
    )
    """Allowed values for feature of interest encoding type."""


app_settings = AppSettings()
