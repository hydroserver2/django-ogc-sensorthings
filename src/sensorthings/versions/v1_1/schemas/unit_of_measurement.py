from .base import BaseSchema


class UnitOfMeasurement(BaseSchema):
    name: str
    symbol: str
    definition: str
