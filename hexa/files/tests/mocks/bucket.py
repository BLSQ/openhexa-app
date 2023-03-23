from google.cloud.storage._helpers import _validate_name


class MockBlob:
    def __init__(self):
        pass

    def upload_from_filename(self, *args, **kwargs):
        pass


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

    def list_blobs(self, *args, **kwargs):
        return self.client.list_blobs(self, *args, **kwargs)

    def blob(self, *args, **kwargs):
        return MockBlob()

    def patch(self):
        pass
