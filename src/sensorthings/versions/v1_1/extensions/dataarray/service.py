from itertools import groupby
from typing import Literal
from pydantic.alias_generators import to_camel, to_snake
from django.http import HttpRequest
from sensorthings.http import validate_select, build_self_link
from sensorthings.types import EntityType
from sensorthings.versions.v1_1 import STA, app_settings


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
        if result_format == "dataArray" and next_link_target:
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

        # When called via a nested resource path, the base returns a grouped dict.
        # Unwrap it before transforming, then rewrap so the caller can unwrap as normal.
        if group_by is not None:
            inner_collection = next(iter(collection.values()), {"value": []})
        else:
            inner_collection = collection

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
                        protocol=STA,
                        settings=app_settings
                    ),
                    "components": components,
                    "data_array": [
                        [entity.get(field) for field in validated_select]
                        for entity in group
                    ]
                }
                for datastream_id, group in groupby(
                    inner_collection["value"],
                    key=lambda entity: entity.get("datastream_id")
                )
            ]
        }

        if inner_collection.get("iot_count"):
            response["iot_count"] = inner_collection["iot_count"]

        if inner_collection.get("iot_next_link"):
            response["iot_next_link"] = inner_collection["iot_next_link"]

        if group_by is not None:
            return {next(iter(collection.keys())): response}

        return response

    async def create_observation_entities(
        self,
        payload: list,
        context: HttpRequest,
    ) -> list[str]:
        """
        Create Observations from a list of DataArrayPostGroup objects.

        When the adapter implements create_observations, all DTOs for each group are passed
        in a single call (bulk path). FoI and phenomenonTime resolution are left to the adapter:
        feature_of_interest_id and phenomenon_time are absent from the DTO when not supplied.

        Falls back to per-row create_entity when create_observations is not available.
        """

        results = []
        adapter = self.backend_adapter  # noqa

        if hasattr(adapter, "create_observations"):
            for item in payload:
                n_rows = len(item.data_array)
                try:
                    dtos = []
                    for row in item.data_array:
                        dto_kwargs = {"datastream_id": item.datastream.id}
                        for component, value in zip(item.components, row):
                            if component == "FeatureOfInterest/id":
                                dto_kwargs["feature_of_interest_id"] = value
                            else:
                                dto_kwargs[to_snake(component)] = value
                        dtos.append(STA.OBSERVATION_ENTITY.build_dto(**dto_kwargs))
                    entity_ids = await self.run_adapter_operation(  # noqa
                        "create", STA.OBSERVATION_ENTITY, payload=dtos, context=context
                    )
                    results.extend(
                        build_self_link(
                            entity_type_set_name=STA.OBSERVATION_ENTITY.set_name,
                            iot_id=entity_id,
                            protocol=self.protocol,  # noqa
                            settings=app_settings,
                        )
                        for entity_id in entity_ids
                    )
                except (Exception,):
                    results.extend(["error"] * n_rows)
        else:
            for item in payload:
                for row in item.data_array:
                    obs_payload = {"datastream": {"id": item.datastream.id}}
                    for component, value in zip(item.components, row):
                        if component == "FeatureOfInterest/id":
                            obs_payload["feature_of_interest"] = {"id": value}
                        else:
                            obs_payload[to_snake(component)] = value
                    try:
                        entity = await self.create_entity(  # noqa
                            STA.OBSERVATION_ENTITY, obs_payload, context
                        )
                        results.append(entity["iot_self_link"])
                    except (Exception,):
                        results.append("error")

        return results
