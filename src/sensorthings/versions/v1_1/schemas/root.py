from .base import BaseSchema


class EntitySetLink(BaseSchema):
    name: str
    url: str


class ServerSettings(BaseSchema):
    conformance: list[str]


class ServiceRootSchema(BaseSchema):
    server_settings: ServerSettings
    value: list[EntitySetLink]
