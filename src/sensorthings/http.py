from django.http import HttpRequest
from typing import List, Tuple, Optional
from sensorthings.engine import SensorThingsBaseEngine
from sensorthings.types import AnyHttpUrlString
from sensorthings.schemas import BaseComponent
from sensorthings.settings import ST_API_ID_TYPE


class SensorThingsHttpRequest(HttpRequest):
    """
    Custom HTTP request class for SensorThings API.

    This class extends the standard Django HttpRequest to include additional attributes
    specific to SensorThings API requests.

    Attributes
    ----------
    sensorthings_url : AnyHttpUrlString
        The SensorThings URL string.
    sensorthings_path : str
        The SensorThings path.
    engine : SensorThingsBaseEngine
        The engine instance for SensorThings.
    nested_path : List[Tuple[BaseComponent, Optional[ST_API_ID_TYPE]]]
        The nested path as a list of tuples, each containing a BaseComponent and an optional ID.
    ref_response : bool
        Indicates whether the response is a reference.
    value_response : bool
        Indicates whether the response is a value.
    """

    sensorthings_url: AnyHttpUrlString
    sensorthings_path: str
    engine: SensorThingsBaseEngine
    nested_path: List[Tuple[BaseComponent, Optional[ST_API_ID_TYPE]]]
    ref_response: bool
    value_response: bool
