from .backend import StorageBackend


def create_storage_mock(project=None):
    return StorageBackend(project=project)


backend = StorageBackend()
mock_gcp_storage = backend.mock_storage
