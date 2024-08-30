from .dev import *  # noqa: F403, F401

DEBUG = False

# Custom test runner
TEST_RUNNER = "hexa.core.test.runner.DiscoverRunner"
WORKSPACE_STORAGE_BACKEND = {"engine": "hexa.files.backends.dummy.DummyStorageClient"}


if "hexa.plugins.connector_accessmod" in INSTALLED_APPS:  # noqa: F405
    # Accessmod settings
    ACCESSMOD_BUCKET_NAME = "s3://hexa-demo-accessmod"
    ACCESSMOD_MANAGE_REQUESTS_URL = "http://localhost:3000/admin/access-requests"
    ACCESSMOD_SET_PASSWORD_URL = "http://localhost:3000/account/set-password"
