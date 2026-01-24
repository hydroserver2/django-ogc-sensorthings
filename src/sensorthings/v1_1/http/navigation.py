from urllib.parse import urlencode
from sensorthings.v1_1.conf import app_settings
from sensorthings.v1_1.protocol import sta


def build_iot_id(iot_id: app_settings.ID_TYPE) -> str:
    """Format an entity ID using the configured ID delimiter."""

    return f"({app_settings.ID_DELIMITER}{iot_id}{app_settings.ID_DELIMITER})"


def build_entity_link(entity_type_set_name: str) -> str:
    """Build the base URL for a given entity type."""

    return f"{app_settings.SERVICE_URL}/{sta.VERSION}/{entity_type_set_name}"


def build_self_link(
    entity_type_set_name: str,
    iot_id: app_settings.ID_TYPE
) -> str:
    """Build the self-link for a specific entity instance."""

    return f"{build_entity_link(entity_type_set_name)}{build_iot_id(iot_id)}"


def build_nav_link(
    entity_type_set_name: str,
    iot_id: app_settings.ID_TYPE,
    related_entity_type_name: str,
) -> str:
    """Build a navigation link from one entity instance to a related entity type or set."""

    return f"{build_self_link(entity_type_set_name, iot_id)}/{related_entity_type_name}"


def build_next_link(
    nav_link: str,
    query_parameters: dict
) -> str:
    """Build the next link for a collection of entities."""

    query_parameters["$top"] = int(query_parameters.get("$top", 100))
    query_parameters["$skip"] = int(query_parameters.get("$skip", 0)) + query_parameters["$top"]

    # return f"{app_settings.SERVICE_URL}/{sta.VERSION}/{relative_path}?{urlencode(query_parameters, safe='$')}"

    return f"{nav_link}?{urlencode(query_parameters, safe='$')}"
