from sensorthings.types import EntityType
from sensorthings.core import BaseProtocol


class STA(BaseProtocol):
    """
    Defines the SensorThings API v1.1 controlled vocabulary and conceptual entity model.

    This class provides protocol-level constants and immutable entity definitions that
    describe the SensorThings v1.1 conceptual model, including entity names, properties,
    and relationships. It serves as a central, implementation-independent reference for
    SensorThings semantics and structure, and is intended to be consumed by routing,
    serialization, and link-construction logic rather than representing runtime data
    or persistence models.
    """

    VERSION = "v1.1"
    ID = "@iot.id"
    SELF_LINK = "@iot.selfLink"
    COUNT = "@iot.count"
    NEXT_LINK = "@iot.nextLink"
    NAVIGATION_LINK = "@iot.navigationLink"

    entity_types: dict[str, EntityType] = {}


sta = STA()
