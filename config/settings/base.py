"""
Django settings for hexa.

Generated by 'django-admin startproject' using Django 3.1.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

import os
from pathlib import Path

from corsheaders.defaults import default_headers
from django.utils.translation import gettext_lazy as _

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY")

# SECURITY WARNING: keep the encryption key used in production secret!
ENCRYPTION_KEY = os.environ.get("ENCRYPTION_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("DEBUG", "false") == "true"

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "").split(",")

# Domain of the new frontend (it is used to redirect the user to new pages not implemented in Django)
NEW_FRONTEND_DOMAIN = os.environ.get("NEW_FRONTEND_DOMAIN")

# Application definition
INSTALLED_APPS = [
    # http://whitenoise.evans.io/en/stable/django.html#using-whitenoise-in-development
    "whitenoise.runserver_nostatic",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.gis",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.postgres",
    "django.contrib.staticfiles",
    "corsheaders",
    "django_countries",
    "django_ltree",
    "ariadne_django",
    "dpq",
    "hexa.user_management",
    "hexa.analytics",
    "hexa.core",
    "hexa.catalog",
    "hexa.countries",
    "hexa.notebooks",
    "hexa.pipelines",
    "hexa.comments",
    "hexa.tags",
    "hexa.ui",
    "hexa.plugins.connector_dhis2",
    "hexa.plugins.connector_s3",
    "hexa.plugins.connector_airflow",
    "hexa.plugins.connector_postgresql",
    "hexa.plugins.connector_accessmod",
    "hexa.workspaces",
    "hexa.databases",
    "hexa.files",
    "hexa.datasets",
    "django_otp",
    "django_otp.plugins.otp_static",
    "django_otp.plugins.otp_email",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "hexa.user_management.middlewares.TwoFactorMiddleware",
    "hexa.user_management.middlewares.UserLanguageMiddleware",
    "hexa.plugins.connector_airflow.middlewares.dag_run_authentication_middleware",
    "hexa.pipelines.middlewares.pipeline_run_authentication_middleware",
    "hexa.workspaces.middlewares.workspace_token_authentication_middleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "hexa.user_management.middlewares.login_required_middleware",
    "hexa.analytics.middlewares.set_analytics_middleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "hexa" / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "hexa.core.context_processors.global_variables",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "HOST": os.environ.get("DATABASE_HOST"),
        "PORT": os.environ.get("DATABASE_PORT"),
        "NAME": os.environ.get("DATABASE_NAME"),
        "USER": os.environ.get("DATABASE_USER"),
        "PASSWORD": os.environ.get("DATABASE_PASSWORD"),
    }
}


# Auth settings
LOGIN_URL = "core:login"
LOGOUT_REDIRECT_URL = "core:login"

# Custom user model
# https://docs.djangoproject.com/en/4.0/topics/auth/customizing/#substituting-a-custom-user-model
AUTH_USER_MODEL = "user_management.User"

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 8,
        },
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Authentication backends
# https://docs.djangoproject.com/en/4.0/topics/auth/customizing/#authentication-backends
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "hexa.user_management.backends.PermissionsBackend",
]


# Additional security settings
SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "true") != "false"
CSRF_COOKIE_SECURE = os.environ.get("CSRF_COOKIE_SECURE", "true") != "false"
SECURE_SSL_REDIRECT = os.environ.get("SECURE_SSL_REDIRECT", "true") != "false"
SECURE_REDIRECT_EXEMPT = [r"^ready$"]

RAW_CSRF_TRUSTED_ORIGINS = os.environ.get("CSRF_TRUSTED_ORIGINS")
if RAW_CSRF_TRUSTED_ORIGINS is not None:
    CSRF_TRUSTED_ORIGINS = RAW_CSRF_TRUSTED_ORIGINS.split(",")

SESSION_COOKIE_DOMAIN = os.environ.get("SESSION_COOKIE_DOMAIN", None)
CSRF_COOKIE_DOMAIN = os.environ.get("CSRF_COOKIE_DOMAIN", None)
SECURE_HSTS_SECONDS = os.environ.get(
    "SECURE_HSTS_SECONDS", 60 * 60
)  # TODO: increase to one year if ok


# by default users need to login every 2 weeks -> update to 1 year
SESSION_COOKIE_AGE = 365 * 24 * 3600

# Trust the X_FORWARDED_PROTO header from the GCP load balancer so Django is aware it is accessed by https
if "TRUST_FORWARDED_PROTO" in os.environ:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# CORS (For GraphQL)
# https://github.com/adamchainz/django-cors-headers

RAW_CORS_ALLOWED_ORIGINS = os.environ.get("CORS_ALLOWED_ORIGINS")
if RAW_CORS_ALLOWED_ORIGINS is not None:
    CORS_ALLOWED_ORIGINS = RAW_CORS_ALLOWED_ORIGINS.split(",")
    CORS_URLS_REGEX = r"^[/graphql/(\w+\/)?|/analytics/track]$"
    CORS_ALLOW_CREDENTIALS = True


CORS_ALLOW_HEADERS = list(default_headers) + [
    "sentry-trace",
]

# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_COOKIE_NAME = "hexa_language"
LANGUAGES = [
    ("en", _("English")),
    ("fr", _("French")),
]
LOCALE_PATHS = [BASE_DIR / "hexa" / "locale"]
LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "static"
STATICFILES_DIRS = [BASE_DIR / "hexa" / "static"]

# Whitenoise
# http://whitenoise.evans.io/en/stable/django.html#add-compression-and-caching-support
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Notebooks component
NOTEBOOKS_URL = os.environ.get("NOTEBOOKS_URL", "http://localhost:8001")
NOTEBOOKS_HUB_URL = os.environ.get("NOTEBOOKS_HUB_URL", "http://jupyterhub:8000/hub")
HUB_API_TOKEN = os.environ.get("HUB_API_TOKEN", "")

GRAPHQL_DEFAULT_PAGE_SIZE = 10
GRAPHQL_MAX_PAGE_SIZE = 10_000

# Logging
if os.environ.get("DEBUG_LOGGING", "false") == "true":
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
            },
        },
        "loggers": {
            "": {
                "handlers": ["console"],
                "level": "INFO",
            },
        },
    }

# Email settings
EMAIL_HOST = os.environ.get("EMAIL_HOST")
EMAIL_PORT = os.environ.get("EMAIL_PORT")
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS") == "true"
DEFAULT_FROM_EMAIL = os.environ.get(
    "DEFAULT_FROM_EMAIL", "OpenHEXA <hexatron@notifications.openhexa.org>"
)

if all([EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD]):
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Sync settings: sync datasource with a worker (good for scaling) or in the web serv (good for dev)
EXTERNAL_ASYNC_REFRESH = os.environ.get("EXTERNAL_ASYNC_REFRESH") == "true"


if os.environ.get("DEBUG_TOOLBAR", "false") == "true":
    INSTALLED_APPS.append("debug_toolbar")
    MIDDLEWARE.append("debug_toolbar.middleware.DebugToolbarMiddleware")
    # Django Debug Toolbar specifically ask for INTERNAL_IPS to be set
    INTERNAL_IPS = ["127.0.0.1"]

    DEBUG_TOOLBAR_CONFIG = {
        "SHOW_TOOLBAR_CALLBACK": lambda request: request.user.is_staff,
    }

if os.environ.get("STORAGE", "local") == "google-cloud":
    # activate google cloud storage, used for dashboard screenshot, ...
    # user generated content
    DEFAULT_FILE_STORAGE = "storages.backends.gcloud.GoogleCloudStorage"
    GS_BUCKET_NAME = os.environ.get("STORAGE_BUCKET")
    GS_FILE_OVERWRITE = False
else:
    MEDIA_ROOT = BASE_DIR / "static" / "uploads"

# Accessmod settings
ACCESSMOD_BUCKET_NAME = os.environ.get("ACCESSMOD_BUCKET_NAME")
ACCESSMOD_MANAGE_REQUESTS_URL = os.environ.get("ACCESSMOD_MANAGE_REQUESTS_URL")
ACCESSMOD_SET_PASSWORD_URL = os.environ.get("ACCESSMOD_SET_PASSWORD_URL")

# Specific settings for airflow plugins

# number of second of airflow dag reloading setting
AIRFLOW_SYNC_WAIT = 61
GCS_TOKEN_LIFETIME = os.environ.get("GCS_TOKEN_LIFETIME")

# Needed so that external component know how to hit us back
# Do not add a trailing slash
BASE_URL = os.environ.get("BASE_URL", "http://localhost:8000")


# Pipeline settings
PIPELINE_SCHEDULER_SPAWNER = os.environ.get("PIPELINE_SCHEDULER_SPAWNER", "kubernetes")
PIPELINE_API_URL = os.environ.get("PIPELINE_API_URL", BASE_URL)
DEFAULT_WORKSPACE_IMAGE = os.environ.get(
    "DEFAULT_WORKSPACE_IMAGE", "blsq/openhexa-blsq-environment:latest"
)
PIPELINE_DEFAULT_CONTAINER_CPU_LIMIT = os.environ.get(
    "PIPELINE_DEFAULT_CONTAINER_CPU_LIMIT", "2"
)
PIPELINE_DEFAULT_CONTAINER_MEMORY_LIMIT = os.environ.get(
    "PIPELINE_DEFAULT_CONTAINER_MEMORY_LIMIT", "4G"
)
PIPELINE_DEFAULT_CONTAINER_CPU_REQUEST = os.environ.get(
    "PIPELINE_DEFAULT_CONTAINER_CPU_REQUEST", "0.05"
)
PIPELINE_DEFAULT_CONTAINER_MEMORY_REQUEST = os.environ.get(
    "PIPELINE_DEFAULT_CONTAINER_MEMORY_REQUEST", "100M"
)
PIPELINE_RUN_DEFAULT_TIMEOUT = os.environ.get("PIPELINE_RUN_DEFAULT_TIMEOUT", 14400)
PIPELINE_RUN_MAX_TIMEOUT = os.environ.get("PIPELINE_RUN_MAX_TIMEOUT", 43200)

# Two Factor Authentication
OTP_EMAIL_BODY_TEMPLATE_PATH = "user_management/token.txt"
OTP_EMAIL_SENDER = DEFAULT_FROM_EMAIL
OTP_EMAIL_SUBJECT = "OpenHEXA Verification Token"

# Workspace Database settings
WORKSPACES_DATABASE_ROLE = os.environ.get("WORKSPACES_DATABASE_ROLE")
WORKSPACES_DATABASE_PASSWORD = os.environ.get("WORKSPACES_DATABASE_PASSWORD")
WORKSPACES_DATABASE_HOST = os.environ.get("WORKSPACES_DATABASE_HOST")
WORKSPACES_DATABASE_PORT = os.environ.get("WORKSPACES_DATABASE_PORT")
WORKSPACES_DATABASE_DEFAULT_DB = os.environ.get("WORKSPACES_DATABASE_DEFAULT_DB")
WORKSPACES_DATABASE_PROXY_HOST = os.environ.get("WORKSPACES_DATABASE_PROXY_HOST")

# Filesystem configuration
WORKSPACE_BUCKET_PREFIX = os.environ.get("WORKSPACE_BUCKET_PREFIX", "hexa-")
WORKSPACE_BUCKET_REGION = os.environ.get("WORKSPACE_BUCKET_REGION", "europe-west1")
WORKSPACE_STORAGE_ENGINE = os.environ.get("WORKSPACE_STORAGE_ENGINE", "gcp")
WORKSPACE_BUCKET_VERSIONING_ENABLED = (
    os.environ.get("WORKSPACE_BUCKET_VERSIONING_ENABLED", "false") == "true"
)

WORKSPACE_STORAGE_ENGINE_AWS_ENDPOINT_URL = os.environ.get(
    "WORKSPACE_STORAGE_ENGINE_AWS_ENDPOINT_URL"
)

# This is the endpoint URL used when generating presigned URLs called by the client since the client
# does not have access to storage engine in local mode (http://minio:9000)
WORKSPACE_STORAGE_ENGINE_AWS_PUBLIC_ENDPOINT_URL = os.environ.get(
    "WORKSPACE_STORAGE_ENGINE_AWS_PUBLIC_ENDPOINT_URL"
)
WORKSPACE_STORAGE_ENGINE_AWS_ACCESS_KEY_ID = os.environ.get(
    "WORKSPACE_STORAGE_ENGINE_AWS_ACCESS_KEY_ID"
)
WORKSPACE_STORAGE_ENGINE_AWS_SECRET_ACCESS_KEY = os.environ.get(
    "WORKSPACE_STORAGE_ENGINE_AWS_SECRET_ACCESS_KEY"
)
WORKSPACE_STORAGE_ENGINE_AWS_BUCKET_REGION = os.environ.get(
    "WORKSPACE_STORAGE_ENGINE_AWS_BUCKET_REGION"
)

# Datasets config
WORKSPACE_DATASETS_BUCKET = os.environ.get("WORKSPACE_DATASETS_BUCKET")
WORKSPACE_DATASETS_FILE_SNAPSHOT_SIZE = os.environ.get(
    "WORKSPACE_DATASETS_FILE_SNAPSHOT_SIZE", 50
)

# Base64 encoded service account key
# To generate a service account key, follow the instructions here:
# import base64
# import json
# base64.b64encode(json.dumps(service_account_key_content).encode("utf-8"))
GCS_SERVICE_ACCOUNT_KEY = os.environ.get("GCS_SERVICE_ACCOUNT_KEY", "")

# S3 settings
AWS_USERNAME = os.environ.get("AWS_USERNAME", "")
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY", "")
AWS_ENDPOINT_URL = os.environ.get("AWS_ENDPOINT_URL", "")
AWS_DEFAULT_REGION = os.environ.get("AWS_DEFAULT_REGION", "")
AWS_USER_ARN = os.environ.get("AWS_USER_ARN", "")
AWS_APP_ROLE_ARN = os.environ.get("AWS_APP_ROLE_ARN", "")
AWS_PERMISSIONS_BOUNDARY_POLICY_ARN = os.environ.get(
    "AWS_PERMISSIONS_BOUNDARY_POLICY_ARN", ""
)

# MIXPANEL
MIXPANEL_TOKEN = os.environ.get("MIXPANEL_TOKEN")
