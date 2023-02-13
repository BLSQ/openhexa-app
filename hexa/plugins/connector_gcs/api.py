from __future__ import annotations

from django.conf import settings
from google.cloud import storage
from google.cloud.iam_credentials_v1 import IAMCredentialsClient
from google.oauth2 import service_account
from google.protobuf import duration_pb2

import hexa.plugins.connector_gcs.models as models


def _build_app_gcs_credentials():
    return service_account.Credentials.from_service_account_info(
        {
            "type": "service_account",
            "project_id": settings.GCS_SERVICE_ACCOUNT_PROJECT,
            "private_key_id": settings.GCS_SERVICE_ACCOUNT_KEY_ID,
            "private_key": settings.GCS_SERVICE_ACCOUNT_KEY,
            "client_email": settings.GCS_SERVICE_ACCOUNT_EMAIL,
            "client_id": settings.GCS_SERVICE_ACCOUNT_CLIENT_ID,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": settings.GCS_SERVICE_ACCOUNT_CERT_URL,
        }
    )


def build_app_short_lived_credentials():
    token_lifetime = 3600
    if settings.GCS_TOKEN_LIFETIME is not None:
        token_lifetime = int(settings.GCS_TOKEN_LIFETIME)
    gcs_credentials = _build_app_gcs_credentials()
    iam_credentials = IAMCredentialsClient(credentials=gcs_credentials)
    token = iam_credentials.generate_access_token(
        name=f"projects/-/serviceAccounts/{gcs_credentials._service_account_email}",
        scope=["https://www.googleapis.com/auth/devstorage.full_control"],
        lifetime=duration_pb2.Duration(seconds=token_lifetime),
    )
    return token


def generate_download_url(*, bucket: models.Bucket, target_key: str):
    google_credentials = _build_app_gcs_credentials()
    client = storage.Client(credentials=google_credentials)
    gcs_bucket = client.get_bucket(bucket.name)
    blob = gcs_bucket.get_blob(target_key)
    return blob.generate_signed_url(expiration=600, version="v4")


def generate_upload_url(*, bucket: models.Bucket, target_key: str):
    google_credentials = _build_app_gcs_credentials()
    client = storage.Client(credentials=google_credentials)
    gcs_bucket = client.get_bucket(bucket.name)
    blob = gcs_bucket.blob(target_key)
    return blob.generate_signed_url(expiration=3600, version="v4", method="PUT")


def download_file(*, bucket: models.Bucket, object_key: str, target: str):
    google_credentials = _build_app_gcs_credentials()
    client = storage.Client(credentials=google_credentials)
    gcs_bucket = client.get_bucket(bucket.name)
    blob = gcs_bucket.get_blob(object_key)
    blob.download_to_filename(filename=target)


def upload_file(*, bucket: models.Bucket, object_key: str, src_path: str):
    google_credentials = _build_app_gcs_credentials()
    client = storage.Client(credentials=google_credentials)
    gcs_bucket = client.get_bucket(bucket.name)
    blob = gcs_bucket.blob(object_key)
    blob.upload_from_filename(filename=src_path)


def _is_dir(blob):
    return blob.size == 0 and blob.name.endswith("/")


def get_object_metadata(*, bucket: models.Bucket, object_key: str):
    google_credentials = _build_app_gcs_credentials()
    client = storage.Client(credentials=google_credentials)
    gcs_bucket = client.get_bucket(bucket.name)
    blob = gcs_bucket.get_blob(object_key)

    return {
        "name": blob.name,
        "size": blob.size,
        "updated": blob.updated,
        "etag": blob.etag,
        "type": "directory" if _is_dir(blob) else "file",
    }


def list_objects_metadata(*, bucket: models.Bucket):
    gcs_credentials = _build_app_gcs_credentials()
    client = storage.Client(credentials=gcs_credentials)
    gcs_bucket = client.get_bucket(bucket.name)
    objects = []

    blobs = list(client.list_blobs(gcs_bucket))
    for blob in blobs:
        objects.append(
            {
                "name": blob.name,
                "size": blob.size,
                "updated": blob.updated,
                "etag": blob.etag,
                "type": "directory" if _is_dir(blob) else "file",
            }
        )

    return objects
