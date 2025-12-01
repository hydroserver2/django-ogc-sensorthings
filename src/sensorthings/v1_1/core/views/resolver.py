import re
from ninja import Router, Query
from ninja.errors import HttpError
from sensorthings.v1_1 import iot
from sensorthings.v1_1.core.service import sensorthings_service
from sensorthings.v1_1.core.schemas.base import BaseSchema
from sensorthings.v1_1.core.schemas import CollectionQuery
from sensorthings.v1_1.conf import app_settings

router = Router()

DELIMITER_RE = re.escape(app_settings.ID_DELIMITER) if app_settings.ID_DELIMITER else ""
SEGMENT_RE = re.compile(
    rf"^(?P<entity>[A-Za-z][A-Za-z0-9]*)"
    rf"(?:\((?P<id>{DELIMITER_RE}[^()]+{DELIMITER_RE})\))?$"
)


@router.get(
    "/{path:path}",
    include_in_schema=False,
    exclude_unset=True,
)
def resolve_resource_path(
    request,
    path: str,
    query: Query[CollectionQuery],
) -> tuple[int, BaseSchema]:
    """"""

    path_segments = [segment for segment in path.strip("/").split("/") if segment] if path else []
    path_handler = None
    path_identifier = None

    ref_only = False
    value_only = False
    selected_property = None
    complex_property_path = []

    for i, segment in enumerate(path_segments):
        segment_match = SEGMENT_RE.match(segment)

        segment_entity = segment_match.group("entity") if segment_match else segment
        segment_identifier = segment_match.group("id") if segment_match else None
        segment_handler = sensorthings_service.get_entity_handler(segment_entity)

        if segment_identifier:
            try:
                segment_identifier = app_settings.ID_TYPE(segment_identifier)
            except (TypeError, ValueError):
                raise HttpError(404, "Not Found")

        if i == 0:
            if segment_handler and segment_entity in iot.SENSING_ENTITIES:
                path_handler = segment_handler
                path_identifier = segment_identifier
                continue
            else:
                raise HttpError(404, "Not Found")

        if not path_identifier:
            if segment_entity == "$ref" and i == len(path_segments) - 1:
                ref_only = True
                continue
            else:
                raise HttpError(404, "Not Found")

        if complex_property_path:
            if segment_entity == "$value":
                if i == len(path_segments) - 1:
                    value_only = True
                else:
                    raise HttpError(404, "Not Found")
            else:
                complex_property_path.append(segment_entity)
            continue

        if selected_property:
            if segment_entity == "$value" and i == len(path_segments) - 1:
                value_only = True
            else:
                raise HttpError(404, "Not Found")
            continue

        if segment_entity in path_handler.related_collections:
            if segment_identifier and segment_identifier in ["ID_CHECK"]:  # Check if this ID belongs to parent
                raise HttpError(404, "Not Found")

            path_handler = segment_handler
            path_identifier = segment_identifier
            continue

        if segment_entity in path_handler.related_entities:
            path_handler = segment_handler
            path_identifier = "TEST"  # Get the ID of this entity
            continue

        if segment_entity in path_handler.primitive_properties:
            selected_property = segment_entity
            continue

        if segment_entity in path_handler.complex_properties:
            selected_property = segment_entity
            complex_property_path.append(segment_entity)
            continue

        raise HttpError(404, "Not Found")

    if not path_handler:
        raise HttpError(404, "Not Found")

    # TODO: Connect to requested view.

    return 200, BaseSchema()
