import base64
import json

from django.core.exceptions import ImproperlyConfigured

import hexa.plugins.connector_gcs.models as models
from hexa.notebooks.credentials import NotebooksCredentials
from hexa.plugins.connector_gcs.models import Bucket
from hexa.user_management.models import PermissionMode


def notebooks_credentials(credentials: NotebooksCredentials):
    """Provides the notebooks credentials data that allows users to access GCS buckets in the notebooks component."""

    read_only_buckets = []
    #    read_only_buckets = Bucket.objects.filter_for_user(
    #        credentials.user, mode=PermissionMode.VIEWER
    #    )
    read_write_buckets = Bucket.objects.filter_for_user(
        credentials.user, mode__in=[PermissionMode.EDITOR, PermissionMode.OWNER]
    )

    # We only need to generate GCS credentials if the user has access to one or more buckets
    if read_only_buckets or read_write_buckets:

        try:
            gcs_credentials = models.Credentials.objects.get()
        except (
            models.Credentials.DoesNotExist,
            models.Credentials.MultipleObjectsReturned,
        ):
            raise ImproperlyConfigured(
                "The GCS connector plugin should have a single credentials entry"
            )

        json_cred = {
            "type": "service_account",
            "project_id": gcs_credentials.project_id,
            "private_key_id": gcs_credentials.project_id,
            "private_key": gcs_credentials.private_key,
            "client_email": gcs_credentials.client_email,
            "client_id": gcs_credentials.client_id,
            "auth_uri": gcs_credentials.auth_uri,
            "token_uri": gcs_credentials.token_uri,
            "auth_provider_x509_cert_url": gcs_credentials.auth_provider_x509_cert_url,
            "client_x509_cert_url": gcs_credentials.client_x509_cert_url,
        }

        json_buckets = {
            "buckets": [{"name": b.name, "mode": "RO"} for b in read_only_buckets]
            + [{"name": b.name, "mode": "RW"} for b in read_write_buckets],
        }

        credentials.update_env(
            {
                "GCS_BUCKETS": base64.b64encode(
                    json.dumps(json_buckets).encode()
                ).decode(),
                "GCS_CREDENTIALS": base64.b64encode(
                    json.dumps(json_cred).encode()
                ).decode(),
            }
        )
