from __future__ import annotations

from typing import TYPE_CHECKING

from google.cloud.storage._helpers import _validate_name

from hexa.files.backends.exceptions import NotFound

from .blob import MockBlob

if TYPE_CHECKING:
    from .client import MockClient


class MockBucket:
    versioning_enabled = False
    lifecycle_rules = []

    def __init__(
        self, client: MockClient, name=None, user_project=None, labels: dict = None
    ):
        name = _validate_name(name)
        self.name = name
        self.labels = labels or {}
        self._client = client
        self._user_project = user_project
        self._blobs = {}

    def __repr__(self):
        return f"<Bucket: {self.name}>"

    @property
    def client(self) -> MockClient:
        return self._client

    def exists(self, client=None):
        if self.name in self.client.buckets:
            return True
        else:
            return False

    def list_blobs(self, *args, **kwargs):
        return self.client.list_blobs(self, *args, **kwargs)

    def get_blob(self, name: str, *args, **kwargs):
        if name not in self._blobs:
            raise NotFound(f"Blob {name} not found")
        return self._blobs[name]

    def blob(self, blob_name: str, *args, **kwargs):
        if blob_name in self._blobs:
            return self._blobs[blob_name]
        return MockBlob(blob_name, bucket=self, **kwargs)

    def patch(self, *args, **kwargs):
        pass

    def delete_blob(self, blob_name: str, *args, **kwargs):
        if blob_name not in self._blobs:
            raise NotFound(f"Blob {blob_name} not found")
        del self._blobs[blob_name]

    def delete_blobs(self, blobs, *args, **kwargs):
        for blob in blobs:
            self.delete_blob(blob.name)
