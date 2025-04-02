from .dev import *  # noqa: F403, F401

DEBUG = False

ALLOWED_HOSTS = ["*"]
CORS_ALLOWED_ORIGINS = ["http://localhost:3000"]
CORS_ALLOW_CREDENTIALS = True
CSRF_TRUSTED_ORIGINS = ["http://localhost:3000"]

# Custom test runner
TEST_RUNNER = "hexa.core.test.runner.DiscoverRunner"
WORKSPACE_STORAGE_BACKEND = {"engine": "hexa.files.backends.dummy.DummyStorageClient"}

if "hexa.plugins.connector_accessmod" in INSTALLED_APPS:  # noqa: F405
    # Accessmod settings
    ACCESSMOD_BUCKET_NAME = "s3://hexa-demo-accessmod"
    ACCESSMOD_MANAGE_REQUESTS_URL = "http://localhost:3000/admin/access-requests"
    ACCESSMOD_SET_PASSWORD_URL = "http://localhost:3000/account/set-password"

NEW_FRONTEND_DOMAIN = "http://localhost:3000"
NOTEBOOKS_URL = "http://localhost:8001"
