from itertools import groupby
from typing import Literal
from pydantic.alias_generators import to_camel, to_snake
from django.http import HttpRequest
from sensorthings.http import validate_select, build_self_link
from sensorthings.types import EntityType
from sensorthings.versions.v1_1 import sta, app_settings


class DataArrayServiceMixin:
    async def get_collection(
        self,
        entity_type: EntityType,
        context: HttpRequest,
        filters: str | None = None,
        count: bool | None = None,
        orderby: str | None = None,
        skip: int | None = None,
        top: int | None = None,
        select: str | None = None,
        select_extra: list[str] | None = None,
        expand: str | None = None,
        group_by: tuple[str, list[app_settings.ID_TYPE]] | None = None,
        next_link_target: list[str] | None = None,
        result_format: Literal["dataArray"] | None = None
    ) -> dict:
        if result_format == "dataArray" and group_by is not None:
            raise ValueError("$resultFormat is not supported inside $expand elements")

        if entity_type.name == "Observation" and result_format == "dataArray":
            select_extra = ["datastream_id"]
            orderby = f"Datastream/id desc,{orderby}" if orderby else "Datastream/id desc"

        collection = await super().get_collection(  # noqa
            entity_type=entity_type,
            context=context,
            filters=filters,
            count=count,
            orderby=orderby,
            skip=skip,
            top=top,
            select=select,
            select_extra=select_extra,
            expand=expand,
            group_by=group_by,
            next_link_target=next_link_target,
        )

        if entity_type.name != "Observation" or result_format != "dataArray":
            return collection

        validated_select = validate_select(entity_type, select)

        if not validated_select:
            components = [
                *entity_type.primitive_properties,
                *entity_type.complex_properties,
            ]
            validated_select = [
                to_snake(field) for field in components
            ]
        else:
            components = [
                to_camel(field) for field in validated_select
            ]

        response = {
            "value": [
                {
                    "datastream_link": build_self_link(
                        entity_type_set_name="Datastreams",
                        iot_id=datastream_id,
                        protocol=sta,
                        settings=app_settings
                    ),
                    "components": components,
                    "data_array": [
                        [entity.get(field) for field in validated_select]
                        for entity in group
                    ]
                }
                for datastream_id, group in groupby(
                    collection["value"],
                    key=lambda entity: entity.get("datastream_id")
                )
            ]
        }

        if collection.get("iot_count"):
            response["iot_count"] = collection["iot_count"]

        if collection.get("iot_next_link"):
            response["iot_next_link"] = collection["iot_next_link"]

        return response
