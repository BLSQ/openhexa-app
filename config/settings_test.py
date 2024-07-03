from .settings import *  # noqa

# since most existing test assumed that gcp was used in conjunction of the mocked storage
# we make sure the .env doesn't interfere with the test and enforce gcp by default in the tests

WORKSPACE_STORAGE_BACKEND = "hexa.files.backends.dummy.DummyStorageClient"
