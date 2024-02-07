from .dev import *  # noqa: F403, F401

DEBUG = False
WORKSPACE_STORAGE_ENGINE = "gcp"

# Custom test runner
TEST_RUNNER = "hexa.core.test.runner.DiscoverRunner"
