from google.cloud.storage._helpers import _validate_name

from hexa.files.backends.exceptions import NotFound

from .blob import MockBlob


class MockBucket:
    versioning_enabled = False
    lifecycle_rules = []

    def __init__(self, client, name=None, user_project=None, labels: dict = None):
        name = _validate_name(name)
        self.name = name
        self.labels = labels or {}
        self._client = client
        self._user_project = user_project
        self._blobs = []

    def __repr__(self):
        return f"<Bucket: {self.name}>"

    @property
    def client(self):
        return self._client

    def exists(self, client=None):
        if self.name in self.client.backend.buckets.keys():
            return True
        else:
            return False

    def list_blobs(self, *args, **kwargs):
        return self.client.list_blobs(self, *args, **kwargs)

    def get_blob(self, name, *args, **kwargs):
        existing = [b for b in self._blobs if b.name == name]
        if len(existing) == 0:
            raise NotFound("key not found")

        return existing[0]

    def blob(self, *args, **kwargs):
        b = MockBlob(*args, bucket=self, **kwargs)
        self._blobs.append(b)
        return b

    def patch(self):
        pass

    def delete_blob(self, name):
        existing = [b for b in self._blobs if b.name == name]
        if len(existing) == 0:
            raise NotFound("key not found")

        self._blobs = [b for b in self._blobs if b.name != name]
