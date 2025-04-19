from typing import List
from pydantic import Field, ConfigDict
from ninja import Schema


class ServerSettings(Schema):
    """
    A schema representing server settings.

    Attributes
    ----------
    conformance : List[str]
        The conformance settings of the server.
    """

    conformance: List[str]


class ServerCapabilities(Schema):
    """
    A schema representing server capabilities.

    Attributes
    ----------
    name : str, optional
        The name of the server capability.
    url : str, optional
        The URL of the server capability.
    """

    name: str = None
    url: str = None


class ServerRootResponse(Schema):
    """
    A schema representing the root response of the server.

    Attributes
    ----------
    server_settings : ServerSettings, optional
        The server settings.
    server_capabilities : List[ServerCapabilities], optional
        The server capabilities.
    """

    model_config = ConfigDict(populate_by_name=True)

    server_settings: ServerSettings = Field(None, alias='serverSettings')
    server_capabilities: List[ServerCapabilities] = Field(None, alias='value')
