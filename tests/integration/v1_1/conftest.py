import pytest
from django.test import Client


class STAClient:
    """Thin wrapper around Django's test Client that prepends the STA base path."""

    BASE = "/sensorthings/v1.1"

    def __init__(self):
        self._client = Client()

    def get(self, path, **kwargs):
        return self._client.get(f"{self.BASE}{path}", **kwargs)

    def post(self, path, data=None, **kwargs):
        kwargs.setdefault("content_type", "application/json")
        return self._client.post(f"{self.BASE}{path}", data=data, **kwargs)

    def patch(self, path, data=None, **kwargs):
        kwargs.setdefault("content_type", "application/json")
        return self._client.patch(f"{self.BASE}{path}", data=data, **kwargs)

    def delete(self, path, **kwargs):
        return self._client.delete(f"{self.BASE}{path}", **kwargs)


@pytest.fixture(scope="session")
def client():
    return STAClient()
