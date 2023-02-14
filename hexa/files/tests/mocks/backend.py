import functools
import uuid
from unittest.mock import patch


class StorageBackend(object):
    def __init__(self, project=None):
        if project is None:
            project = "test-project-" + str(uuid.uuid1())
        self.project = project
        self.buckets = {}
        self.blobs = {}

    def reset(self):
        self.buckets = {}
        self.blobs = {}

    def create_bucket(self, bucket_name):
        pass

    def create_blob(self, bucket_name, blob_name, **kwargs):
        pass

    @patch("google.oauth2.service_account")
    def mock_storage(self, func, mock_service_account):
        from .client import MockClient

        def create_mock_client(*args, **kwargs):
            client = MockClient(backend=self, *args, **kwargs)
            return client

        def wrapper(*args, **kwargs):
            self.reset()

            with patch("google.cloud.storage.Client", create_mock_client):
                return func(*args, **kwargs)

        functools.update_wrapper(wrapper, func)
        wrapper.__wrapped__ = func
        return wrapper
