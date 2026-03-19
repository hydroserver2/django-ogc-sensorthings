from .base import BaseSchema


class ServerSettings(BaseSchema):
    conformance: list


class ServiceRootSchema(BaseSchema):
    server_settings: ServerSettings
    value: list
