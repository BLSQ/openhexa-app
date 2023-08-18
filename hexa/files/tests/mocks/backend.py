import functools
import uuid
from unittest.mock import patch


class StorageBackend(object):
    def __init__(self, project=None):
        if project is None:
            project = "test-project-" + str(uuid.uuid1())
        self.project = project
        self.buckets = {}

    def reset(self):
        self.buckets = {}

    def mock_storage(self, func):
        from .client import MockClient

        def create_mock_client(*args, **kwargs):
            client = MockClient(backend=self, *args, **kwargs)
            return client

        def wrapper(*args, **kwargs):
            with patch("hexa.files.api.get_storage_client", create_mock_client):
                return func(*args, **kwargs)

        functools.update_wrapper(wrapper, func)
        wrapper.__wrapped__ = func
        return wrapper
