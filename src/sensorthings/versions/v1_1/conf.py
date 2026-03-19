from dataclasses import dataclass, field
from typing import Any, Callable
from uuid import UUID
from django.conf import settings as django_settings


@dataclass(frozen=True)
class BaseSettings:
    """
    Base class for settings objects whose values can be overridden by
    Django settings using a fixed prefix.
    """

    SETTINGS_PREFIX: str = ""
    """The Django settings prefix to use for the following settings."""

    SERVICE_URL: str = ""
    """The base service URL SensorThings will be served from."""

    ID_TYPE: type = int
    """The type used for entity IDs."""

    ID_DELIMITER: str = ""
    """The delimiter character for entity IDs in resource paths."""

    ID_EXAMPLE: str = None
    """An example value for entity IDs."""

    MAX_TOP: int = 100
    """The maximum length of a collection response returned by the service."""

    AUTH_HANDLERS: dict[str, Callable] = field(default_factory=dict)
    """Custom authentication handlers for HTTP endpoints."""

    DEFAULT_AUTH_HANDLER: list[Callable] | None = None
    """Default authentication handler for HTTP endpoints."""

    BACKEND_ADAPTER: None = None  # type("BackendAdapter") = None  # TODO
    """The backend adapter this service is connected to."""

    def __post_init__(self):
        id_examples: dict[type, str] = {
            int: "1",
            str: "string",
            UUID: "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        }

        if self.ID_EXAMPLE is None:
            object.__setattr__(
                self,
                "ID_EXAMPLE",
                id_examples.get(self.ID_TYPE, 1),
            )

    def __getattribute__(self, name: str) -> Any:
        if name in ("__dict__", "__class__", "SETTINGS_PREFIX"):
            return super().__getattribute__(name)

        prefixed_name = f"{self.SETTINGS_PREFIX}{name}"

        if hasattr(django_settings, prefixed_name):
            return getattr(django_settings, prefixed_name)

        return super().__getattribute__(name)


...


from dataclasses import dataclass, field
from typing import Any, Literal
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

    PROPERTIES_SCHEMAS: dict[str, Any] = field(default_factory=dict)
    """Custom schemas for entity property fields."""

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
