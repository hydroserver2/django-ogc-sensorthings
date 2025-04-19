from typing_extensions import Annotated
from pydantic import AnyHttpUrl, AfterValidator, WithJsonSchema, PlainSerializer


AnyHttpUrlString = Annotated[
    AnyHttpUrl,
    AfterValidator(lambda v: str(v)),
    PlainSerializer(lambda v: str(v)),
    WithJsonSchema({'type': 'string'}, mode='serialization')
]
