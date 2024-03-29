from .base import *  # noqa: F403, F401

DEBUG = True
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False
ALLOWED_HOSTS = ["*"]
CORS_ALLOWED_ORIGINS = ["http://localhost:3000"]
CORS_URLS_REGEX = r"^/graphql/(\w+\/)?$"
CORS_ALLOW_CREDENTIALS = True
CSRF_TRUSTED_ORIGINS = ["http://localhost:3000"]
PIPELINE_SCHEDULER_SPAWNER = "docker"
SECRET_KEY = "))dodw9%n)7q86l-q1by4e-2z#vonph50!%ep7_je)_=x0m2v-"
ENCRYPTION_KEY = "oT7DKt8zf0vsnbBcJ0R36SHkBzbjF2agFIK3hSAVvko="
GCS_TOKEN_LIFETIME = 3600
