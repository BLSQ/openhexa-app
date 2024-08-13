from .dev import *  # noqa: F403, F401
from .dev import INSTALLED_APPS

DEBUG = False

# Custom test runner
TEST_RUNNER = "hexa.core.test.runner.DiscoverRunner"

INSTALLED_APPS += ["hexa", "hexa.core.tests.soft_delete"]
