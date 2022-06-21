from __future__ import annotations

from django.conf import settings
from google.cloud import storage
from google.cloud.iam_credentials_v1 import IAMCredentialsClient
from google.oauth2 import service_account
from google.protobuf import duration_pb2

import hexa.plugins.connector_gcs.models as models


def _build_app_gcs_credentials(*, credentials: models.Credentials):
    json_cred = {
        "type": "service_account",
        "project_id": credentials.project_id,
        "private_key_id": credentials.private_key_id,
        "private_key": credentials.private_key,
        "client_email": credentials.client_email,
        "client_id": credentials.client_id,
        "auth_uri": credentials.auth_uri,
        "token_uri": credentials.token_uri,
        "auth_provider_x509_cert_url": credentials.auth_provider_x509_cert_url,
        "client_x509_cert_url": credentials.client_x509_cert_url,
    }
    return service_account.Credentials.from_service_account_info(json_cred)


def _build_app_short_lived_credentials(*, credentials: models.Credentials):
    token_lifetime = 3600
    if settings.GCS_TOKEN_LIFETIME is not None:
        token_lifetime = int(settings.GCS_TOKEN_LIFETIME)
    gcs_credentials = _build_app_gcs_credentials(credentials=credentials)
    iam_credentials = IAMCredentialsClient(credentials=gcs_credentials)
    token = iam_credentials.generate_access_token(
        name=f"projects/-/serviceAccounts/{gcs_credentials._service_account_email}",
        scope=["https://www.googleapis.com/auth/devstorage.full_control"],
        lifetime=duration_pb2.Duration(seconds=token_lifetime),
    )
    return token


def _is_dir(blob):
    return blob.size == 0 and blob.name.endswith("/")


def list_objects_metadata(*, credentials: models.Credentials, bucket: models.Bucket):

    gcs_credentials = _build_app_gcs_credentials(credentials=credentials)
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
