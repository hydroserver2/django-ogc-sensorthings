from ..base import BackendAdapter
from .thing import ThingAdapterMixin


class DummyBackendAdapter(
    ThingAdapterMixin,
    BackendAdapter,
):
    """"""
