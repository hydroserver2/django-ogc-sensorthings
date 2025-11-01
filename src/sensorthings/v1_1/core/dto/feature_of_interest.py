from typing import Optional, Dict
from dataclasses import dataclass
from sensorthings.v1_1.core import iot
from sensorthings.v1_1.conf import app_settings
from .base import BaseEntityDTO


@dataclass
class FeatureOfInterestDTO(BaseEntityDTO):
    name: Optional[str] = None
    description: Optional[str] = None
    encoding_type: Optional[
        app_settings.FEATURE_OF_INTEREST_ENCODING_TYPE_VALUE_LITERAL
    ] = None
    feature: Optional[app_settings.FEATURE_OF_INTEREST_ENCODING_TYPE_SCHEMA] = None
    properties: Optional[app_settings.PROPERTIES_SCHEMAS.get("Location", Dict)] = None

    _entity = iot.FEATURES_OF_INTEREST
    _related_entities = [iot.OBSERVATIONS]
