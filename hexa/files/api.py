import typing
from dataclasses import dataclass

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from google.api_core.exceptions import NotFound
from google.cloud import storage
from google.cloud.exceptions import Conflict
from google.oauth2 import service_account

WORKSPACE_BUCKET_PREFIX = settings.WORKSPACE_BUCKET_PREFIX or ""


@dataclass
class ObjectsPage:
    items: typing.List[any]
    next_page_token: str


def get_credentials():
    json_creds = {
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
    creds = service_account.Credentials.from_service_account_info(json_creds)
    return creds


def get_storage_client():
    credentials = get_credentials()
    return storage.Client(credentials=credentials)


def _is_dir(blob):
    return blob.size == 0 and blob.name.endswith("/")


def create_bucket(workspace):
    bucket_name = WORKSPACE_BUCKET_PREFIX + workspace.slug
    client = get_storage_client()
    try:
        bucket = client.create_bucket(bucket_name)
        return bucket
    except Conflict as e:
        print(f"GCS: Bucket {bucket_name} already exists!")


def _blob_to_dict(blob):
    return {
        "name": blob.name,
        "updated": blob.updated,
        "size": blob.size,
        "type": "directory" if _is_dir(blob) else "file",
    }


def list_bucket_objects(workspace, prefix=None, page_token=None, per_page=30):
    if workspace.bucket_name is None:
        raise ImproperlyConfigured("Workspace does not have a bucket")

    client = get_storage_client()
    results_iterator = client.list_blobs(
        workspace.bucket_name,
        prefix=prefix,
        page_token=page_token,
        max_results=per_page,
    )
    objects = []
    for obj in results_iterator:
        objects.append(_blob_to_dict(obj))

    return ObjectsPage(
        items=objects,
        next_page_token=results_iterator.next_page_token,
    )


def get_bucket_object(workspace, name):
    if workspace.bucket_name is None:
        raise ImproperlyConfigured("Workspace does not have a bucket")

    client = get_storage_client()
    bucket = client.get_bucket(workspace.bucket_name)
    object = bucket.get_blob(name)
    if object is None:
        raise NotFound("Object not found")

    return _blob_to_dict(object)


def delete_object(workspace, name):
    if workspace.bucket_name is None:
        raise ImproperlyConfigured("Workspace does not have a bucket")

    client = get_storage_client()
    bucket = client.get_bucket(workspace.bucket_name)
    bucket.delete_blob(name)
    return
