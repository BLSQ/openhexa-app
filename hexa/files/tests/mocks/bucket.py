from google.cloud.storage._helpers import _validate_name


class MockBucket:
    def __init__(self, client, name=None, user_project=None):
        name = _validate_name(name)
        self.name = name
        self._client = client
        self._user_project = user_project
        self._blobs = []

    def __repr__(self):
        return "<Bucket: %s>" % (self.name,)

    @property
    def client(self):
        return self._client

    def exists(self, client=None):
        if self.name in self.client.backend.buckets.keys():
            return True
        else:
            return False
