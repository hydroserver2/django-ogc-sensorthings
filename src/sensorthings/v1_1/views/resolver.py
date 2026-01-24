import re
from ninja import Router, Query
from ninja.errors import HttpError
from django.http import HttpRequest
from sensorthings.v1_1.protocol import sta
from sensorthings.v1_1.http import RouterDefinition, OperationDefinition
from sensorthings.v1_1.service import sensorthings_service
from sensorthings.v1_1.schemas.base import BaseSchema
from sensorthings.v1_1.schemas import CollectionQuery
from sensorthings.v1_1.conf import app_settings

DELIMITER_RE = re.escape(app_settings.ID_DELIMITER) if app_settings.ID_DELIMITER else ""
SEGMENT_RE = re.compile(
    rf"^(?P<entity_type>[A-Za-z][A-Za-z0-9]*)"
    rf"(?:\((?P<id>{DELIMITER_RE}[^()]+{DELIMITER_RE})\))?$"
)

router_definition = RouterDefinition(
    router=Router(),
    operations={}
)


def resolve_resource_path(
    request: HttpRequest,
    path: str,
    query: Query[CollectionQuery],
) -> tuple[int, BaseSchema]:
    """"""

    path_segments = [segment for segment in path.strip("/").split("/") if segment] if path else []
    path_protocol = None
    path_identifier = None

    ref_only = False
    value_only = False
    selected_property = None
    complex_property_path = []

    for i, segment in enumerate(path_segments):
        segment_match = SEGMENT_RE.match(segment)

        segment_entity_type = segment_match.group("entity_type") if segment_match else segment
        segment_identifier = segment_match.group("id") if segment_match else None
        segment_protocol = sta.get_entity_protocol(segment_entity_type)

        if segment_identifier:
            try:
                segment_identifier = app_settings.ID_TYPE(segment_identifier)
            except (TypeError, ValueError):
                raise HttpError(404, "Not Found")

        if i == 0:
            if segment_protocol and segment_entity_type in sta.entities:
                path_protocol = segment_protocol
                path_identifier = segment_identifier
                continue
            else:
                raise HttpError(404, "Not Found")

        if not path_identifier:
            if segment_entity_type == "$ref" and i == len(path_segments) - 1:
                ref_only = True
                continue
            else:
                raise HttpError(404, "Not Found")

        if complex_property_path:
            if segment_entity_type == "$value":
                if i == len(path_segments) - 1:
                    value_only = True
                else:
                    raise HttpError(404, "Not Found")
            else:
                complex_property_path.append(segment_entity_type)
            continue

        if selected_property:
            if segment_entity_type == "$value" and i == len(path_segments) - 1:
                value_only = True
            else:
                raise HttpError(404, "Not Found")
            continue

        if segment_entity_type in path_protocol.related_entity_sets:
            if segment_identifier and segment_identifier in ["ID_CHECK"]:  # Check if this ID belongs to parent
                raise HttpError(404, "Not Found")

            path_protocol = segment_protocol
            path_identifier = segment_identifier
            continue

        if segment_entity_type in path_protocol.related_entity_types:
            path_protocol = segment_protocol
            path_identifier = "TEST"  # Get the ID of this entity
            continue

        if segment_entity_type in path_protocol.primitive_properties:
            selected_property = segment_entity_type
            continue

        if segment_entity_type in path_protocol.complex_properties:
            selected_property = segment_entity_type
            complex_property_path.append(segment_entity_type)
            continue

        raise HttpError(404, "Not Found")

    if not path_protocol:
        raise HttpError(404, "Not Found")

    # TODO: Connect to requested view.

    return 200, BaseSchema()


router_definition.operations["resolve_resource_path"] = OperationDefinition(
    path="/{path:path}",
    methods=["GET"],
    view_func=resolve_resource_path,
    include_in_schema=False
)
