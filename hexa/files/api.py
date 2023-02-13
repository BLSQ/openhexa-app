import typing
from dataclasses import dataclass

from django.conf import settings
from django.core.exceptions import ValidationError
from google.api_core.exceptions import NotFound
from google.cloud import storage
from google.cloud.exceptions import Conflict
from google.cloud.storage.blob import Blob
from google.oauth2 import service_account


@dataclass
class ObjectsPage:
    items: typing.List[any]
    has_next_page: bool
    has_previous_page: bool
    page_number: int


def get_credentials():
    return service_account.Credentials.from_service_account_info(
        {
            "type": "service_account",
            "project_id": settings.GCS_SERVICE_ACCOUNT_PROJECT,
            "private_key_id": settings.GCS_SERVICE_ACCOUNT_KEY_ID,
            "private_key": settings.GCS_SERVICE_ACCOUNT_KEY.replace("\\n", "\n"),
            "client_email": settings.GCS_SERVICE_ACCOUNT_EMAIL,
            "client_id": settings.GCS_SERVICE_ACCOUNT_CLIENT_ID,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": settings.GCS_SERVICE_ACCOUNT_CERT_URL,
        }
    )


def get_storage_client():
    credentials = get_credentials()
    return storage.Client(credentials=credentials)


def _is_dir(blob):
    return blob.size == 0 and blob.name.endswith("/")


def create_bucket(bucket_name):
    client = get_storage_client()
    try:
        bucket = client.create_bucket(
            bucket_name, location=settings.WORKSPACE_BUCKET_REGION
        )
        bucket.cors = [
            {
                "origin": settings.CORS_ALLOWED_ORIGINS,
                "responseHeader": [
                    "Authorization",
                    "Content-Range",
                    "Accept",
                    "Content-Type",
                    "Origin",
                    "Range",
                ],
                "method": ["GET", "PUT"],
                "maxAgeSeconds": 3600,
            }
        ]
        bucket.patch()
        return bucket
    except Conflict as e:
        raise ValidationError(f"GCS: Bucket {bucket_name} already exists!")


def _blob_to_dict(blob: Blob):
    return {
        "name": blob.name.split("/")[-1],
        "key": blob.name,
        "path": "/".join([blob.bucket.name, blob.name]),
        "content_type": blob.content_type,
        "updated": blob.updated,
        "size": blob.size,
        "type": "directory" if _is_dir(blob) else "file",
    }


def _prefix_to_dict(bucket_name, name: str):
    return {
        "name": name.split("/")[-2],
        "key": name,
        "path": "/".join([bucket_name, name]),
        "size": 0,
        "type": "directory",
    }


def list_bucket_objects(bucket_name, prefix=None, page: int = 1, per_page=30):
    client = get_storage_client()
    request = client.list_blobs(
        bucket_name,
        prefix=prefix,
        page_size=per_page,
        delimiter="/",
        include_trailing_delimiter=True,
    )
    objects = []
    next_page = None
    page_number = 0
    for req_page in request.pages:
        if request.page_number == page:
            if page == 1:
                # Add the prefix to the response if the user requests the first page
                for prefix in request.prefixes:
                    objects.append(_prefix_to_dict(bucket_name, prefix))

            page_number = request.page_number
            objects += [_blob_to_dict(obj) for obj in req_page if _is_dir(obj) is False]
        elif request.page_number > page:
            next_page = req_page
            break

    return ObjectsPage(
        items=objects,
        page_number=page_number,
        has_previous_page=page_number > 1,
        has_next_page=bool(next_page),
    )


def ensure_is_folder(object_key: str):
    if object_key.endswith("/") is False:
        return object_key + "/"
    return object_key


def get_bucket_object(bucket_name: str, object_key: str):
    client = get_storage_client()
    bucket = client.get_bucket(bucket_name)
    object = bucket.get_blob(object_key)
    if object is None:
        raise NotFound("Object not found")

    return _blob_to_dict(object)


def create_bucket_folder(bucket_name: str, folder_key: str):
    client = get_storage_client()
    bucket = client.get_bucket(bucket_name)
    object = bucket.blob(ensure_is_folder(folder_key))
    object.upload_from_string(
        "", content_type="application/x-www-form-urlencoded;charset=UTF-8"
    )

    return _blob_to_dict(object)


def delete_object(bucket_name, name):
    client = get_storage_client()
    bucket = client.get_bucket(bucket_name)
    blob = bucket.get_blob(name)
    if _is_dir(blob):
        blobs = list(bucket.list_blobs(prefix=name))
        bucket.delete_blobs(blobs)

    bucket.delete_blob(name)
    return


def generate_download_url(bucket_name: str, target_key: str):
    client = get_storage_client()
    gcs_bucket = client.get_bucket(bucket_name)
    blob: Blob = gcs_bucket.get_blob(target_key)
    return blob.generate_signed_url(expiration=600, version="v4")


def generate_upload_url(bucket_name: str, target_key: str, content_type: str):
    client = get_storage_client()
    gcs_bucket = client.get_bucket(bucket_name)
    blob = gcs_bucket.blob(target_key)
    return blob.generate_signed_url(
        expiration=3600, version="v4", method="PUT", content_type=content_type
    )
