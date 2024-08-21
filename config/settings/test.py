from .dev import *  # noqa: F403, F401

DEBUG = False

# Custom test runner
TEST_RUNNER = "hexa.core.test.runner.DiscoverRunner"
WORKSPACE_STORAGE_BACKEND = {"engine": "hexa.files.backends.dummy.DummyStorageClient"}
