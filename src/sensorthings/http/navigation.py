from sensorthings.core import BaseSettings, BaseProtocol


def build_iot_id(
    iot_id: str,
    app_settings: BaseSettings
) -> str:
    """Format an entity ID using the configured ID delimiter."""

    return f"({app_settings.ID_DELIMITER}{iot_id}{app_settings.ID_DELIMITER})"


def build_entity_link(
    entity_type_set_name: str,
    protocol: BaseProtocol,
    settings: BaseSettings,
) -> str:
    """Build the base URL for a given entity type."""

    return f"{settings.SERVICE_URL}/{protocol.VERSION}/{entity_type_set_name}"


def build_self_link(
    entity_type_set_name: str,
    iot_id: str,
    protocol: BaseProtocol,
    settings: BaseSettings,
) -> str:
    """Build the self-link for a specific entity instance."""

    return f"{build_entity_link(entity_type_set_name, protocol, settings)}{build_iot_id(iot_id, settings)}"


def build_nav_link(
    entity_type_set_name: str,
    iot_id: str,
    related_entity_type_name: str,
    protocol: BaseProtocol,
    settings: BaseSettings,
) -> str:
    """Build a navigation link from one entity instance to a related entity type or set."""

    return f"{build_self_link(entity_type_set_name, iot_id, protocol, settings)}/{related_entity_type_name}"


def _split_entity_and_options(segment: str) -> tuple[str, str | None]:
    """Return (entity_name, options_content) — options_content excludes surrounding parens."""

    parenthesis_start = segment.find("(")

    if parenthesis_start == -1:
        return segment, None

    return segment[:parenthesis_start], segment[parenthesis_start + 1: -1]


def _increment_chain_skip(chain: list[str], target_location: list[str]) -> list[str]:
    """
    Recursively walk a slash-separated $expand chain and increment $skip on the
    segment identified by target_location.
    """

    if len(target_location) > 1:
        next_entity, _ = _split_entity_and_options(chain[1])

        return [chain[0]] + _increment_chain_skip(chain[1:], target_location[1:])

    else:
        entity_name, options_content = _split_entity_and_options(chain[0])
        params = {
            k.strip(): v.strip()
            for token in options_content.split(";")
            for k, _, v in [token.partition("=")] if v
        } if options_content else {}

        top = int(params.get("$top", 100))
        skip = int(params.get("$skip", 0))

        params["$top"] = str(top)
        params["$skip"] = str(skip + top)

        return [f"{entity_name}({';'.join(f'{k}={v}' for k, v in params.items())})"] + chain[1:]


def build_next_link_expand(expand_str: str, target_location: list[str]) -> str:
    """Build the next link for a collection of entities requested by an $expand parameter."""

    result_parts = []

    for part in expand_str.split(","):
        chain = part.split("/")

        if chain[0].split("(")[0] == target_location[0]:
            chain = _increment_chain_skip(chain, target_location)

        result_parts.append("/".join(chain))

    return ",".join(result_parts)


def build_next_link(
    nav_link: str,
    query_params: dict,
    target_location: list[str] | None = None
) -> str:
    """Build the next link for a collection of entities."""

    if target_location:
        expand_param = query_params.pop("$expand")

        if isinstance(expand_param, list):
            expand_param = expand_param[0]

        next_expand = build_next_link_expand(expand_param, target_location)

        next_link_query_params = {
            **query_params,
            "$expand": next_expand
        }

    else:
        top_value = query_params.pop("$top", None)
        skip_value = query_params.pop("$skip", None)

        if isinstance(top_value, list):
            top_value = top_value[0] if top_value else None
        if isinstance(skip_value, list):
            skip_value = skip_value[0] if skip_value else None

        top = int(top_value) if top_value is not None else 100
        skip = int(skip_value) if skip_value is not None else 0
        next_skip = skip + top

        next_link_query_params = {
            **query_params,
            "$top": top,
            "$skip": next_skip,
        }

    parts = [
        f"{key}={item}"
        for key, value in next_link_query_params.items()
        if value is not None
        for item in (value if isinstance(value, list) else [value])
    ]

    query_param_string = f"?{'&'.join(parts)}"

    return nav_link + query_param_string
