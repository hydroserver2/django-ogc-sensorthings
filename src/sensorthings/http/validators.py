from pydantic.alias_generators import to_snake
from odata_query.exceptions import ODataException
from odata_query.grammar import ODataParser, ODataLexer
from odata_query.ast import _Node  # noqa
from sensorthings.types import EntityType
from sensorthings.core import BaseProtocol
from sensorthings.versions.v1_1.dto import OrderByField, OrderByDirection


lexer = ODataLexer()
parser = ODataParser()


def validate_select(
    entity_type: EntityType,
    select: str | None = None
) -> list[str] | None:
    """
    Parse and validate a $select clause for a given entity type.

    This method validates selected fields against the entity's allowed
    primitive, complex, and navigation properties, and normalizes field
    names to their internal representation.
    """

    if not select:
        return None

    # ------------------------------------------------------------------
    # Parse and deduplicate selected fields
    # ------------------------------------------------------------------

    selected_fields = list(
        dict.fromkeys(
            "id" if field.strip() == "@iot.id" else field.strip()
            for field in select.split(",")
            if field.strip()
        )
    )

    # ------------------------------------------------------------------
    # Determine allowed fields
    # ------------------------------------------------------------------

    allowed_fields = {
        *entity_type.primitive_properties,
        *entity_type.complex_properties,
        *entity_type.related_entity_type_names,
        *entity_type.related_entity_type_set_names,
    }

    # ------------------------------------------------------------------
    # Validate selection
    # ------------------------------------------------------------------

    invalid_fields = [
        field for field in selected_fields
        if field not in allowed_fields
    ]

    if invalid_fields:
        raise ValueError(
            f"Invalid fields in $select: {', '.join(invalid_fields)}"
        )

    # ------------------------------------------------------------------
    # Normalize field names
    # ------------------------------------------------------------------

    return [
        to_snake(field) for field in selected_fields
    ]


def tokenize_expand(
    expand: str | None
) -> dict[str: str | None]:
    """"""

    if not expand:
        return []

    tokens: dict[str, str | None] = {}
    token_chars: list[str] = []
    param_chars: list[str] = []

    paren_depth = 0
    token_has_params = False
    token_has_nested = False

    for char in expand:
        if char == "/":
            token_has_nested = True
            if paren_depth == 0 and token_has_params:
                raise ValueError(f"Nested expand after parameters is invalid: {''.join(token_chars)}{char}")
        if char == "(" or char == ")":
            token_has_params = True
            if token_has_nested:
                raise ValueError(f"Parameters after nested expand is invalid: {''.join(token_chars)}{char}")
        if paren_depth < 0:
            raise ValueError(f"Unexpected closing parenthesis at: {''.join(token_chars)}{char}")

        if char == "(":
            paren_depth += 1
        elif char == ")":
            paren_depth -= 1
        elif char == "," and paren_depth == 0:
            token = "".join(token_chars).strip()
            if token_has_nested:
                token_parts = token.split("/")
                entity = token_parts[0].strip()
                token_params = f"$expand={'/'.join(token_parts[1:])}"
            else:
                entity = token.strip()
                token_params = "".join(param_chars).strip() if param_chars else None
            if entity:
                tokens[entity] = token_params
            token_chars.clear()
            param_chars.clear()
            token_has_params = False
            token_has_nested = False
            continue

        if paren_depth == 0:
            token_chars.append(char)
        else:
            param_chars.append(char)

    if token_chars:
        token = "".join(token_chars).strip()
        if token_has_nested:
            token_parts = token.split("/")
            entity = token_parts[0].strip()
            token_params = f"$expand={'/'.join(token_parts[1:])}"
        else:
            entity = token.strip().rstrip(")")
            token_params = "".join(param_chars).strip().lstrip("(") if param_chars else None
        if entity:
            tokens[entity] = token_params

    if paren_depth != 0:
        raise ValueError

    return tokens


def split_top_level(
    text: str,
    delimiter: str = ",",
    open_char: str = "(",
    close_char: str = ")"
) -> list[str]:
    """"""

    tokens: list[str] = []
    token_chars: list[str] = []
    depth = 0

    for char in text:
        if char == open_char:
            depth += 1
        elif char == close_char:
            depth -= 1
            if depth < 0:
                raise ValueError("Closing character cannot precede opening character")
        elif char == delimiter and depth == 0:
            tokens.append("".join(token_chars))
            token_chars.clear()
            continue

        token_chars.append(char)

    if depth != 0:
        raise ValueError("Opening and closing characters must be balanced")

    if token_chars:
        tokens.append("".join(token_chars))

    return tokens


def validate_expand(
    entity_type: EntityType,
    expand: str | None = None,
) -> dict[str, dict]:
    """
    Parse and validate an $expand clause for a given entity type.

    This method validates expanded navigation properties against the entity's
    related entity types and entity sets, parses nested expansions and query
    options, and returns a normalized structure suitable for recursive
    expansion processing.
    """

    if not expand:
        return {}

    validated_expand: dict[str, dict] = {}

    allowed_entities = {
        *entity_type.related_entity_type_names,
        *entity_type.related_entity_type_set_names,
    }

    for expand_token in split_top_level(expand):
        nested_tokens = split_top_level(expand_token, "/")
        entity, _, param_string = nested_tokens[0].partition("(")
        param_string = param_string[:-1] if param_string else None
        params = {
            to_snake(param_token.split("=")[0].lstrip("$")): "=".join(param_token.split("=")[1:])
            for param_token in split_top_level(param_string, ";")
        } if param_string else {}

        if len(nested_tokens) > 1:
            params["expand"] = "/".join(nested_tokens[1:])

        if entity not in allowed_entities:
            raise ValueError(f"Invalid entity in $expand: {entity}")

        validated_expand[entity] = params

    return validated_expand


def validate_orderby(
    entity_type: EntityType,
    protocol: BaseProtocol,
    orderby: str | None = None,
) -> list[OrderByField] | None:
    """
    Parse and validate an $orderby clause for a given entity type.

    This method validates each order-by segment, resolves sort direction,
    verifies that the referenced property path is valid for the entity type,
    and returns a normalized list of OrderByField objects.
    """

    if not orderby:
        return None

    parsed_orderby: list[OrderByField] = []

    # ------------------------------------------------------------------
    # Split and parse order-by segments
    # ------------------------------------------------------------------

    for segment in (part.strip() for part in orderby.split(",")):
        if not segment:
            continue

        tokens = segment.split()

        if len(tokens) not in (1, 2):
            raise ValueError(f"Invalid $orderby segment: '{segment}'")

        # ------------------------------------------------------------------
        # Resolve sort direction
        # ------------------------------------------------------------------

        field_token = tokens[0]
        direction = OrderByDirection.ASC

        if len(tokens) == 2:
            try:
                direction = OrderByDirection(tokens[1].lower())
            except ValueError:
                raise ValueError(f"Invalid $orderby direction: '{segment}'")

        # ------------------------------------------------------------------
        # Validate field path
        # ------------------------------------------------------------------

        field_path = field_token.split("/")

        if not validate_field_path(entity_type, field_path, protocol):
            raise ValueError(f"Invalid $orderby field path: '{field_token}'")

        parsed_orderby.append(
            OrderByField(
                path=field_path,
                direction=direction,
            )
        )

    return parsed_orderby


def validate_filters(filters: str | None = None) -> _Node | None:
    """
    Parse and validate an OData $filter string into an abstract syntax tree.

    Returns a parse tree representing the filter expression, suitable for
    downstream evaluation by the backend adapter. Returns None if no filter
    string is provided.
    """

    if not filters:
        return None

    try:
        return parser.parse(lexer.tokenize(filters.strip()))
    except ODataException as e:
        raise ValueError(f"Invalid $filter: {str(e)}")


def validate_field_path(
    entity_type: EntityType,
    path: list[str],
    protocol: BaseProtocol
) -> bool:
    """
    Validate that a field path is valid for a given entity type.

    A path is valid if it references:
        1. A single primitive property, or
        2. A nested property of a complex type, or
        3. A navigation through related entity types where each step is valid.
    """

    if len(path) == 1 and path[0] in entity_type.primitive_properties:
        return True
    elif len(path) > 1 and path[0] in entity_type.complex_properties:
        return True
    elif (
            len(path) > 1
            and path[0] in entity_type.related_entity_type_names + entity_type.related_entity_type_set_names
            and validate_field_path(protocol.get_entity_type(path[0]), path[1:], protocol)
    ):
        return True
    else:
        return False
