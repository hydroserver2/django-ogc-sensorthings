from typing import Any
from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema


class AbsentType:
    def __repr__(self):
        return "<ABSENT>"

    def __bool__(self):
        return False

    @classmethod
    def __get_pydantic_core_schema__(
            cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:

        def serialize(value: Any):
            return None

        def validate(value: Any):
            return cls

        schema = core_schema.union_schema([
            core_schema.is_instance_schema(cls),
        ])

        return core_schema.no_info_after_validator_function(
            validate,
            schema,
            serialization=core_schema.plain_serializer_function_ser_schema(
                serialize, when_used="json"
            ),
        )


Absent = AbsentType()
